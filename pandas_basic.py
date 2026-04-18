import pandas as pd

# ================================
# 1. DataFrame 만들기 (표 형태)
# ================================
data = {
    "company":  ["SemiFive", "CYTUR", "Mearitt", "인탑스", "Olive"],
    "growth":   [85, 42, 110, 75, 60],
    "revenue":  [120, 30, 80, 55, 45],
    "stage":    ["Series B", "Series A", "Series B", "Series A", "Series A"],
}

df = pd.DataFrame(data)

print("=== 전체 데이터 ===")
print(df)

# ================================
# 2. 기본 통계
# ================================
print("\n=== 기본 통계 ===")
print(df[["growth", "revenue"]].describe())

# ================================
# 3. 정렬
# ================================
print("\n=== 성장률 높은 순 정렬 ===")
print(df.sort_values("growth", ascending=False))

# ================================
# 4. 필터링
# ================================
print("\n=== 성장률 70% 이상 회사만 ===")
filtered = df[df["growth"] >= 70]
print(filtered)

# ================================
# 5. 새 컬럼 추가
# ================================
df["score"] = df["growth"] * 0.6 + df["revenue"] * 0.4
print("\n=== 종합점수 추가 ===")
print(df.sort_values("score", ascending=False))
df.to_excel("portfolio.xlsx", index=False)
print("Excel 저장 완료: portfolio.xlsx")