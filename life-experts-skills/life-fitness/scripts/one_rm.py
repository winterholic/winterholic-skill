#!/usr/bin/env python3
"""1RM(1회 최대중량) 추정 계산기 — Epley / Brzycki 공식.

표준 라이브러리만 사용. 진단·치료가 아니라 점진적 과부하 설계용 참고 수치다.
- Epley:   1RM = w * (1 + reps/30)
- Brzycki: 1RM = w * 36 / (37 - reps)

주의: 추정식은 통상 reps <= 10~12 구간에서만 신뢰할 만하다(고반복일수록 오차↑).
실제 1RM 테스트는 부상 위험이 크므로 초보는 추정값으로 갈음하는 편이 안전하다.

사용:
    python one_rm.py            # 데모(내장 예시)
    python one_rm.py 100 5      # 100kg를 5회 든 경우 1RM 추정 + 훈련 중량표
"""
import io
import sys

# Windows 콘솔(cp949)에서 em-dash 등 출력 시 인코딩 오류 방지
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
else:  # 구버전 폴백
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def epley(weight: float, reps: int) -> float:
    """Epley 공식. reps=1이면 weight 그대로 반환."""
    if reps <= 1:
        return weight
    return weight * (1 + reps / 30)


def brzycki(weight: float, reps: int) -> float:
    """Brzycki 공식. reps>=37이면 분모가 0/음수가 되어 정의 불가."""
    if reps <= 1:
        return weight
    if reps >= 37:
        raise ValueError("Brzycki 공식은 reps < 37 에서만 유효합니다 (고반복 추정 부적합)")
    return weight * 36 / (37 - reps)


def estimate(weight: float, reps: int) -> dict:
    """두 공식의 평균을 대표 1RM으로 사용."""
    e = epley(weight, reps)
    b = brzycki(weight, reps)
    return {"epley": e, "brzycki": b, "avg": (e + b) / 2}


# 추정 1RM에 대한 목표 반복수별 권장 강도(%1RM) — 근거 기반 통상 구간(확인 필요)
PCT_TABLE = [
    (1, 1.00, "최대 근력(초보 비권장)"),
    (3, 0.93, "근력"),
    (5, 0.87, "근력/근비대 경계 — 초보 주력 구간"),
    (8, 0.78, "근비대"),
    (10, 0.74, "근비대/지구력"),
    (12, 0.70, "지구력 쪽"),
]


def training_table(one_rm: float) -> list:
    return [(reps, round(one_rm * pct, 1), pct, note) for reps, pct, note in PCT_TABLE]


def report(weight: float, reps: int) -> str:
    if reps > 12:
        warn = "  [경고] 12회 초과 추정은 오차가 큽니다 — 참고만 하세요.\n"
    else:
        warn = ""
    est = estimate(weight, reps)
    lines = [
        f"입력: {weight}kg x {reps}회",
        warn.rstrip("\n") if warn else None,
        f"  Epley   : {est['epley']:.1f} kg",
        f"  Brzycki : {est['brzycki']:.1f} kg",
        f"  추정 1RM(평균): {est['avg']:.1f} kg",
        "",
        "목표 반복수별 권장 중량(추정 1RM 기준, 확인 필요):",
    ]
    for reps_t, w_t, pct, note in training_table(est["avg"]):
        lines.append(f"  {reps_t:>2}회: {w_t:>6.1f} kg ({pct*100:>3.0f}%) — {note}")
    lines.append("")
    lines.append("※ 정보 제공용 추정치입니다 — 통증/기저질환이 있으면 의사·물리치료사 상담 권고.")
    return "\n".join(l for l in lines if l is not None)


def main(argv):
    if len(argv) >= 3:
        try:
            weight = float(argv[1])
            reps = int(argv[2])
        except ValueError:
            print("사용법: python one_rm.py <중량kg> <반복수>")
            return 1
        print(report(weight, reps))
        return 0

    # 데모
    print("=== 1RM 추정 데모 ===\n")
    for w, r in [(100, 5), (60, 8), (40, 12)]:
        print(report(w, r))
        print("-" * 40)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
