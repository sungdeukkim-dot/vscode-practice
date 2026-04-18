import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

# Windows 한글 폰트 설정
matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False

# ================================
# 데이터 준비
# ================================
data = {
    "company":  ["SemiFive", "CYTUR", "Mearitt", "Intops", "Olive"],
    "growth":   [85, 42, 110, 75, 60],
    "revenue":  [120, 30, 80, 55, 45],
}
df = pd.DataFrame(data)


# ================================
# 1. 막대 차트 — 성장률 비교
# ================================
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.bar(df["company"], df["growth"], color=["green","orange","green","blue","orange"])
plt.title("Revenue Growth Rate (%)")
plt.xlabel("Company")
plt.ylabel("Growth (%)")
plt.xticks(rotation=15)

# ================================
# 2. 산점도 — 성장률 vs 매출액
# ================================
plt.subplot(1, 2, 2)
plt.scatter(df["growth"], df["revenue"], s=200, color="steelblue", alpha=0.7)

for i, row in df.iterrows():
    plt.annotate(row["company"],
                 (row["growth"], row["revenue"]),
                 textcoords="offset points",
                 xytext=(5, 5))

plt.title("Growth vs Revenue")
plt.xlabel("Growth Rate (%)")
plt.ylabel("Revenue (100M KRW)")
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("portfolio_chart.png", dpi=150, bbox_inches="tight")
plt.show()

print("차트 저장 완료: portfolio_chart.png")