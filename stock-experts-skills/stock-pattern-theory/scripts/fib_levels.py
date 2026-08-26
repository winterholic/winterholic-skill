"""피보나치 레벨 — 되돌림·확장 목표 + 무효화 레벨. (표준 라이브러리만)

사용: python fib_levels.py             # 데모
임포트: from fib_levels import retracements, extensions
"""

RETRACE = [0.236, 0.382, 0.5, 0.618, 0.786]
EXTEND = [1.0, 1.272, 1.618, 2.618]


def retracements(swing_low, swing_high):
    """상승 파동(저점->고점)의 되돌림 레벨. 2파≈0.618, 4파≈0.382가 빈도 높음(타깃 아닌 '구간')."""
    rng = swing_high - swing_low
    return {f"{r:.3f}": round(swing_high - rng * r, 1) for r in RETRACE}


def extensions(swing_low, swing_high, retrace_low=None):
    """확장 목표. retrace_low(되돌림 저점) 주어지면 그 지점부터 투영(3파 목표 등)."""
    rng = swing_high - swing_low
    base = retrace_low if retrace_low is not None else swing_low
    return {f"{e:.3f}": round(base + rng * e, 1) for e in EXTEND}


def invalidation(wave1_start, label="Wave 2"):
    """엘리어트 무효화: 2파는 1파 시작점을 100% 하향 돌파할 수 없다."""
    return {f"{label} 무효화 레벨": wave1_start,
            "규칙": "이 가격 하향 시 카운트 폐기 -> 대안 카운트 채택"}


if __name__ == "__main__":
    print("== 데모: (가상) 지수 2,350 -> 2,720 상승 파동 ==")
    print("되돌림:", retracements(2350, 2720))
    print("확장(되돌림 저점 2,580 기준):", extensions(2350, 2720, retrace_low=2580))
    print(invalidation(2350))
