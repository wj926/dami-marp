"""
AX 전환 설문 bar chart 생성
- DAMI Lab 네이비 톤
- 최대 응답 강조 (진한 네이비), 나머지 연한 gray-blue
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.font_manager import FontProperties
from pathlib import Path

# TTC 파일 직접 FontProperties 로 지정 (miniconda matplotlib 이 CJK TTC 의 서브패밀리를 등록 못 하는 케이스 대응)
_KR_TTC = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
KR = FontProperties(fname=_KR_TTC)
KR_BOLD = FontProperties(fname="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
mpl.rcParams["axes.unicode_minus"] = False

NAVY = "#1F3864"
NAVY_HL = "#2E5AAC"
GRAY = "#D0D4DC"
TEXT = "#222222"

OUT = Path(__file__).parent


def horizontal_bar(
    labels, values, title, out_name, highlight_max=True, total=9, fig_h=3.2
):
    """수평 bar + 우측에 응답 수/비율 표시"""
    fig, ax = plt.subplots(figsize=(9.0, fig_h), dpi=150)
    y = range(len(labels))[::-1]

    max_v = max(values) if values else 0
    colors = [
        NAVY if (highlight_max and v == max_v and v > 0) else GRAY for v in values
    ]

    bars = ax.barh(list(y), values, color=colors, height=0.62, edgecolor="none")

    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=12, color=TEXT, fontproperties=KR)
    ax.set_xlim(0, max(values) * 1.22 + 0.5)
    ax.set_xticks([])
    for spine in ("top", "right", "bottom", "left"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(left=False)

    for bar, v in zip(bars, values):
        pct = (v / total * 100) if total else 0
        ax.text(
            bar.get_width() + 0.15,
            bar.get_y() + bar.get_height() / 2,
            f"  {v}명 ({pct:.1f}%)",
            va="center",
            ha="left",
            fontsize=11,
            color=TEXT,
            fontproperties=KR,
        )

    ax.set_title(title, fontsize=14, color=TEXT, loc="left", pad=10, fontproperties=KR_BOLD)
    plt.tight_layout()
    fig.savefig(OUT / out_name, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"saved: {out_name}")


# ─────────────────────────────────────────────
# Q3. 전환 속도 (9명, 5점 척도)
horizontal_bar(
    labels=[
        "너무 빠르다",
        "조금 빠르다",
        "적당하다",
        "조금 느리다",
        "너무 느리다",
    ],
    values=[0, 4, 5, 0, 0],
    title="Q3. 전환 속도 체감  (n=9)",
    out_name="q3_speed.png",
    total=9,
    fig_h=3.2,
)

# Q4. 스트레스 (9명, 1~5)
horizontal_bar(
    labels=["1 (낮음)", "2", "3", "4", "5 (높음)"],
    values=[1, 3, 4, 1, 0],
    title="Q4. 전환 부담·스트레스  (n=9,  평균 2.56 / 5)",
    out_name="q4_stress.png",
    total=9,
    fig_h=3.2,
)

# Q7. 생산성 (9명)
horizontal_bar(
    labels=[
        "크게 향상",
        "약간 향상",
        "변화 없음",
        "오히려 떨어짐",
        "판단하기 이르다",
    ],
    values=[2, 3, 1, 1, 2],
    title="Q7. AI 전환 이후 연구 생산성 변화  (n=9)",
    out_name="q7_productivity.png",
    total=9,
    fig_h=3.2,
)

# Q8. 노션→웹페이지 선호도 (9명)
horizontal_bar(
    labels=["매우 선호", "선호", "중립", "비선호", "매우 비선호"],
    values=[1, 5, 3, 0, 0],
    title="Q8. 노션 발표 → 웹페이지 전환 선호도  (n=9)",
    out_name="q8_webpage.png",
    total=9,
    fig_h=3.2,
)

# Q13. 연구실 지원 (복수선택, 9명)
horizontal_bar(
    labels=[
        "유료 구독 지원",
        "도구 세팅 가이드",
        "프롬프트 템플릿 공유",
        "노하우 공유 세션",
        "체계적 교육·워크샵",
        "멘토링 / 1:1 상담",
    ],
    values=[8, 5, 4, 1, 0, 0],
    title="Q13. 연구실에서 원하는 지원  (n=9, 복수 선택)",
    out_name="q13_support.png",
    total=9,
    fig_h=3.6,
)

print("\nall charts generated.")
