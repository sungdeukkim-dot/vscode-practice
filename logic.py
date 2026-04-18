# ================================
# 1. 함수 (def)
# ================================
def greet(name):
    return f"안녕하세요, {name}님!"

def calculate_age(birth_year):
    return 2026 - birth_year

# 함수 호출
print(greet("Brandon"))
print(f"나이: {calculate_age(1983)}세")


# ================================
# 2. 조건문 (if / elif / else)
# ================================
def evaluate_investment(revenue_growth):
    if revenue_growth >= 100:
        return "🟢 탁월함 — 투자 적극 검토"
    elif revenue_growth >= 50:
        return "🟡 양호함 — 추가 실사 필요"
    elif revenue_growth >= 0:
        return "🟠 주의 — 성장성 부족"
    else:
        return "🔴 위험 — 투자 부적격"

# 테스트
print(evaluate_investment(120))
print(evaluate_investment(65))
print(evaluate_investment(10))
print(evaluate_investment(-20))


# ================================
# 3. 리스트 + 반복문 조합
# ================================
portfolio = [
    {"company": "SemiFive", "growth": 85},
    {"company": "CYTUR",    "growth": 42},
    {"company": "Mearitt",  "growth": 110},
    {"company" : "인탑스", "growth": 75},
    {"company": "테스트컴퍼니", "growth": -10},
]

print("\n--- 포트폴리오 투자 평가 ---")
for item in portfolio:
    result = evaluate_investment(item["growth"])
    print(f"{item['company']} (성장률 {item['growth']}%): {result}")