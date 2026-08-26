#!/usr/bin/env node
/**
 * finding·편집 지문 관리 — 하네스가 코드로 한다.
 *
 * 에이전트에게 이력을 보여주면 Contextual Drag(실패한 시도가 컨텍스트에 남으면 이후 생성이
 * 구조적으로 유사한 오류로 편향, 11모델·8과제 10~20% 하락)에 걸린다. 그래서 dedup 과
 * 라이브락 차단을 전부 코드 쪽에 둔다.
 *
 *   node scripts/dedup.mjs parse   <critic-output.txt> --screen /orders --axis spacing
 *   node scripts/dedup.mjs filter  <findings.json> --seen .ui-refine/seen.json
 *   node scripts/dedup.mjs edit-fp <diff.patch> --blocked .ui-refine/blocked.json
 */
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';

const [cmd, file, ...rest] = process.argv.slice(2);
const args = parseArgs(rest);

if (cmd === 'parse') {
  const raw = await readFile(file, 'utf8');
  console.log(JSON.stringify(parseFindings(raw, args.screen, args.axis), null, 2));
} else if (cmd === 'filter') {
  const findings = JSON.parse(await readFile(file, 'utf8'));
  const seen = await loadJson(args.seen, []);
  const seenSet = new Set(seen);
  const fresh = [], dropped = [];
  // ★ **축 간 실질 중복** — 지문에서 `axis` 를 뺐지만 `item` 이 축마다 다르면 지문도 달라져
  //   같은 지적이 두 번 남는다. 실측(p6-bigdom 7축 병렬): 정렬 축의 `3-6` 과 폼·테이블 축의
  //   `offlist` 가 **타깃 8개가 완전히 같고 관찰 문장까지 사실상 동일**한데 둘 다 통과했다.
  //   논문이 말한 "중복 지적 8~9건"이 그대로 재현된 것이다.
  //   ⚠️ 판정 기준은 **타깃 집합 완전 일치**로 둔다. 겹침 비율 임계값은 근거가 없어 지어내는
  //      값이 되고, 부분 겹침은 정당한 별개 지적(같은 카드의 다른 문제)일 수 있다.
  //      부분 겹침은 버리지 않고 `overlaps` 로 표시만 해 중재자가 보게 한다.
  const keyOf = (f) => `${f.screen}|${[...f.target].sort().join(',')}`;
  const byTargets = new Map();
  for (const f of findings) {
    // severity 0 은 비평가 자백이라 중재자에게 보내지 않는다.
    // ⚠️ [확인 필요] LLM 이 자기 오탐에 0 을 매긴다는 근거는 없다. 첫 실행에서
    //    0 이 실제로 나오는지 보고, 안 나오면 이 경로를 폐기한다.
    if (f.severity === 0) { dropped.push({ ...f, why: 'severity-0' }); continue; }
    if (seenSet.has(f.fingerprint)) { dropped.push({ ...f, why: 'duplicate' }); continue; }
    const k = keyOf(f);
    const twin = byTargets.get(k);
    if (twin && twin.axis !== f.axis) {
      twin.also_reported_by = [...new Set([...(twin.also_reported_by || []), f.axis])];
      dropped.push({ ...f, why: 'cross-axis-duplicate', kept: `${twin.axis}/${twin.item}` });
      continue;
    }
    seenSet.add(f.fingerprint);
    if (!twin) byTargets.set(k, f);
    fresh.push(f);
  }
  // ⚠️ **부분 겹침은 표시조차 하지 않는다.** 처음엔 "타깃이 하나라도 겹치면 중재자가 보게
  //    표시"를 넣었는데, 실측에서 **17건 중 16건에 붙었다** — 표 화면은 형제 셀을 여러 축이
  //    함께 가리키는 게 정상이라 신호가 아니라 배경 소음이 된다. 겹침 비율 임계는 지어낸 값이
  //    되므로 넣지 않는다. 완전 일치만 중복으로 본다.
  await writeFile(args.seen, JSON.stringify([...seenSet], null, 2));
  console.log(JSON.stringify({ fresh, dropped, freshCount: fresh.length }, null, 2));
} else if (cmd === 'edit-fp') {
  const patch = await readFile(file, 'utf8');
  const fp = editFingerprint(patch);
  const blocked = await loadJson(args.blocked, []);
  if (blocked.includes(fp)) {
    console.log(JSON.stringify({ blocked: true, fingerprint: fp,
      reason: '이미 기각된 편집이다. 같은 수정을 재생성했다 — 라운드 내부에서 재샘플하라.' }));
    process.exit(1);
  }
  console.log(JSON.stringify({ blocked: false, fingerprint: fp }));
} else if (cmd === 'block') {
  const fp = editFingerprint(await readFile(file, 'utf8'));
  const blocked = await loadJson(args.blocked, []);
  if (!blocked.includes(fp)) blocked.push(fp);
  await writeFile(args.blocked, JSON.stringify(blocked, null, 2));
  console.log(JSON.stringify({ added: fp, total: blocked.length }));
} else if (cmd === 'match') {
  // 3층 중재자: finding 을 1b 측정치와 대조한다.
  //
  // ⚠️ 번호가 하나라도 겹치면 매칭으로 치면 안 된다. 실측에서 "제목↔카드 간격"(1-3) 지적이
  //    무관한 `pad-asym`(카드 내부 상하 여백)에 붙었다 — 여러 번호를 나열한 finding 은
  //    우연히 겹친 측정치와도 매칭된다. **번호 교집합 + 항목↔판정 종류 대응**을 둘 다 본다.
  const findings = JSON.parse(await readFile(file, 'utf8'));
  const measure = JSON.parse(await readFile(args.measure, 'utf8'));

  // ⚠️ **1b 가 재는 요소와 비평가가 가리키는 요소는 층이 다르다.** 실측: 가로 넘침을 1b 는
  //    넘치는 컨테이너(HEADER·MAIN)에 붙이는데 비평가는 **잘려 보이는 셀**을 가리켰다. 번호가
  //    정확히 같기를 요구하면 같은 결함을 두고 unsupported 가 난다.
  //    → 비평가가 가리킨 번호의 **조상 사슬**까지 후보로 넣는다. 자손 방향은 넣지 않는다 —
  //      컨테이너를 지목했다고 그 안 모든 자식의 측정치를 근거로 삼으면 매칭이 헐거워진다.
  const parentOf = new Map(measure.elements.map((e) => [e.n, e.p ?? null]));
  const withAncestors = (nums) => {
    const out = new Set(nums);
    for (const n of nums) {
      let cur = parentOf.get(n);
      for (let d = 0; cur != null && d < 12; d++) { out.add(cur); cur = parentOf.get(cur); }
    }
    return out;
  };

  const out = findings.map((f) => {
    const nums = f.target.map(Number).filter(Number.isFinite);
    const chain = withAncestors(nums);
    const kinds = itemKindMap()[f.item] || [];
    const exact = measure.findings.filter(
      (m) => kinds.includes(m.kind) && m.targets.some((t) => nums.includes(t)));
    const viaAncestor = measure.findings.filter(
      (m) => kinds.includes(m.kind) && !exact.includes(m) && m.targets.some((t) => chain.has(t)));
    const hits = [...exact, ...viaAncestor];
    return {
      ...f,
      verdict: hits.length ? 'supported' : (kinds.length ? 'unsupported' : 'no-measure-for-item'),
      matched_via: exact.length ? 'target' : (viaAncestor.length ? 'ancestor' : null),
      evidence: hits.map((h) => `${h.kind}: ${h.detail}`),
    };
  });
  const g = (v) => out.filter((x) => x.verdict === v).length;
  console.log(JSON.stringify({
    findings: out,
    summary: { supported: g('supported'), unsupported: g('unsupported'),
               noMeasure: g('no-measure-for-item') },
  }, null, 2));
} else {
  console.error('commands: parse | filter | match | edit-fp | block');
  process.exit(1);
}

/**
 * 체크리스트 항목 → 그 항목을 뒷받침할 수 있는 1b 판정 종류.
 *
 * ⚠️ **없는 항목에 억지로 매핑을 붙이지 않는다.** `4-1`(색 의미)·`6-8`(정렬 상태 표시)·
 *    `7-10`(최대 폭)·`3-16`(열 폭 배분)은 1b 에 측정 수단이 **원리적으로** 없고, `offlist` 는
 *    항목 자체가 없다. 이런 것은 `no-measure-for-item` 이 **정직한 답**이고 보류함으로 가는 게 맞다.
 *    매핑을 지어내면 그 순간 오매칭 제조기가 된다(= 배제 규칙을 덧붙이지 않는다는 원칙의 매칭판).
 * 여기 없는 항목은 측정 수단이 없다는 뜻이고, 중재자는 예외 목록만 보고 대부분 보류함으로 보낸다.
 * collect.js 에 판정을 추가하면 이 표도 함께 갱신한다.
 */
function itemKindMap() {
  return {
    '1-1': ['repeat-padding', 'scale', 'undefined-var'],
    '1-2': ['alignment', 'scale', 'double-indent', 'dead-column'],
    '1-3': ['hierarchy'],
    '1-4': ['control-ratio'],
    '1-6': ['pad-asym'],
    '1-8': ['hierarchy', 'scale'],
    '1-12': ['gap-asym'],
    '1-14': ['double-indent'],
    '1-17': ['hierarchy'],
    '2-4': ['weight-variety'],
    '2-10': ['affordance'],
    '2-12': ['focus-missing'],
    '3-1': ['alignment'], '3-2': ['alignment'], '3-7': ['alignment'], '3-15': ['alignment'],
    // 열 경계 어긋남·버튼 라벨 줄바꿈 높이도 결국 1b 의 정렬 측정과 같은 종류다(실측에서
    // 비평가가 가장 많이 쓴 항목인데 표에 없어 통째로 no-measure 로 떨어졌다).
    '3-6': ['alignment', 'num-align'], '3-17': ['alignment', 'row-height'],
    '3-5': ['num-align'],
    '3-9': ['overflow', 'collapsed'],
    '3-4': ['collapsed'],      // 같은 행 카드 높이가 제각각 — 한 장이 무너진 경우
    '3-8': ['overlap', 'collapsed'],
    '3-12': ['decimals'],
    '3-13': ['tabular-nums'],
    '5-9': ['cls'],
    '6-1': ['input-width'],
    '6-2': ['required-mark'],
    '6-5': ['placeholder-label'],
    '6-6': ['table-header'],
    '6-7': ['cell-padding'],
    '6-9': ['empty-cell'],
    '6-10': ['row-height'],
  };
}

// ---------- ----------

/** 비평가 출력의 ---FINDING--- 블록을 파싱한다. 형식이 고정돼 있어야 지문이 안정된다. */
function parseFindings(raw, screen, axis) {
  if (/^\s*NO_FINDINGS\s*$/m.test(raw) && !raw.includes('---FINDING---')) return [];
  const blocks = raw.split('---FINDING---').slice(1);
  return blocks.map((b) => {
    const body = b.split('---END---')[0];
    const get = (k) => {
      const m = new RegExp(`^${k}:\\s*(.+)$`, 'm').exec(body);
      return m ? m[1].trim() : null;
    };
    const targets = (get('target') || '')
      .split(',').map((s) => s.trim().replace(/^#/, '')).filter(Boolean);
    const item = get('item') || 'offlist';
    return {
      screen, axis,
      seen_in: (get('seen_in') || '').replace(/[[\]]/g, '').split(',').map((s) => s.trim()).filter(Boolean),
      target: targets,
      target_desc: get('target_desc'),
      item,
      observed: get('observed'),
      why_wrong: get('why_wrong'),
      severity: Number(get('severity') ?? -1),
      severity_why: get('severity_why'),
      intent_flag: get('intent_flag') || 'none',
      intent_why: get('intent_why'),
      // 지문에 axis 를 넣지 않는다 — 축이 다르면 지문이 달라져 축 간 중복이 dedup 을 통과한다
      fingerprint: sha(`${screen}|${targets.sort().join(',')}|${item}`),
    };
  });
}

function editFingerprint(patch) {
  // 컨텍스트 줄·줄번호를 빼고 실제 변경 줄만 남긴다. 같은 편집의 재생성을 잡기 위해서다.
  const changed = patch.split('\n')
    .filter((l) => /^[+-]/.test(l) && !/^([+-]{3})/.test(l))
    .map((l) => l.replace(/\s+/g, ' ').trim())
    .sort()
    .join('\n');
  return sha(changed);
}

// 함수 선언이어야 한다 — 호출부가 모듈 최상단이라 const 화살표는 TDZ 에 걸린다
function sha(s) {
  return createHash('sha1').update(s).digest('hex').slice(0, 12);
}

async function loadJson(path, fallback) {
  if (!path) return fallback;
  try { return JSON.parse(await readFile(path, 'utf8')); } catch { return fallback; }
}

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    if (!argv[i].startsWith('--')) continue;
    const key = argv[i].slice(2);
    const nxt = argv[i + 1];
    if (!nxt || nxt.startsWith('--')) { out[key] = true; } else { out[key] = nxt; i++; }
  }
  return out;
}
