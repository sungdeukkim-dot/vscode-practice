# ================================
# 업그레이드된 투자 판정 함수
# 조건 1: 매출 성장률 (%)
# 조건 2: 매출액 (억원)
# ================================
def evaluate_investment(revenue_growth, revenue_billion):
    
    # 성장률 점수
    if revenue_growth >= 100:
        growth_score = 3
    elif revenue_growth >= 50:
        growth_score = 2
    elif revenue_growth >= 0:
        growth_score = 1
    else:
        growth_score = 0

    # 매출액 점수
    if revenue_billion >= 100:
        revenue_score = 3
    elif revenue_billion >= 50:
        revenue_score = 2
    elif revenue_billion >= 10:
        revenue_score = 1
    else:
        revenue_score = 0

    # 두 점수 합산
    total = growth_score + revenue_score

    if total >= 5:
        return "🟢 탁월함 — 투자 적극 검토"
    elif total >= 3:
        return "🟡 양호함 — 추가 실사 필요"
    elif total >= 1:
        return "🟠 주의 — 성장성 부족"
    else:
        return "🔴 위험 — 투자 부적격"


# ================================
# 포트폴리오 평가
# ================================
portfolio = [
    {"company": "SemiFive",  "growth": 85,  "revenue": 120},
    {"company": "CYTUR",     "growth": 42,  "revenue": 30},
    {"company": "Mearitt",   "growth": 110, "revenue": 80},
    {"company": "인탑스",    "growth": 75,  "revenue": 55},
]

print("=" * 45)
print(f"{'회사명':<12} {'성장률':>6} {'매출액':>8}  판정")
print("=" * 45)

for item in portfolio:
    result = evaluate_investment(item["growth"], item["revenue"])
    print(f"{item['company']:<12} {item['growth']:>5}%  {item['revenue']:>6}억   {result}")

print("=" * 45)