"""사후 채점 계산기 — Brier score·스킬별 적중률·캘리브레이션 표. (표준 라이브러리만)

사용: python scorecard_calc.py         # 데모
임포트: from scorecard_calc import brier, hit_rate_by, calibration_table
레코드 형식: {"skill": str, "confidence": 0.5~0.95, "outcome": 1(적중)/0(빗나감)}
ledger.md 표에서 행을 옮겨 적거나, 파싱해 리스트로 만든 뒤 호출한다.
"""


def brier(records):
    """Brier score = 평균 (확신도 - 결과)^2. 0이 완벽, 0.25 = 무정보(동전)."""
    if not records:
        return None
    return sum((r["confidence"] - r["outcome"]) ** 2 for r in records) / len(records)


def hit_rate_by(records, key="skill"):
    """key별 적중률과 표본 수. n<10이면 '표본부족' 플래그(환류 판단 금지)."""
    groups = {}
    for r in records:
        groups.setdefault(r[key], []).append(r["outcome"])
    out = {}
    for k, outcomes in groups.items():
        n = len(outcomes)
        out[k] = {"적중률": round(sum(outcomes) / n, 2), "n": n,
                  "판정가능": n >= 10, "비고": "" if n >= 10 else "표본부족(기록만)"}
    return out


def calibration_table(records, buckets=((0.50, 0.60), (0.60, 0.75), (0.75, 0.96))):
    """확신도 구간별 [평균 확신도 vs 실제 적중률] — 격차 양(+)이면 과신."""
    rows = []
    for lo, hi in buckets:
        grp = [r for r in records if lo <= r["confidence"] < hi]
        if not grp:
            rows.append({"구간": f"{int(lo*100)}~{int(hi*100)}%", "n": 0})
            continue
        conf = sum(r["confidence"] for r in grp) / len(grp)
        hit = sum(r["outcome"] for r in grp) / len(grp)
        rows.append({"구간": f"{int(lo*100)}~{int(hi*100)}%", "n": len(grp),
                     "평균확신도": round(conf, 2), "실제적중률": round(hit, 2),
                     "과신격차%p": round((conf - hit) * 100, 1)})
    return rows


if __name__ == "__main__":
    demo = [
        {"skill": "trend", "confidence": 0.75, "outcome": 1},
        {"skill": "trend", "confidence": 0.80, "outcome": 0},
        {"skill": "trend", "confidence": 0.65, "outcome": 1},
        {"skill": "deepvalue", "confidence": 0.60, "outcome": 1},
        {"skill": "deepvalue", "confidence": 0.70, "outcome": 0},
        {"skill": "swing", "confidence": 0.85, "outcome": 1},
        {"skill": "swing", "confidence": 0.90, "outcome": 0},
        {"skill": "swing", "confidence": 0.55, "outcome": 1},
    ]
    print("== 데모 (8건 — 실전은 10건+부터 판정) ==")
    print(f"Brier: {brier(demo):.3f} (0.25=동전 수준)")
    print("스킬별:", hit_rate_by(demo))
    for row in calibration_table(demo):
        print(row)
