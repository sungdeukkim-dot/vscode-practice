import json

# ================================
# 1. 투자 포트폴리오 데이터 정의
# ================================
portfolio = [
    {"company": "SemiFive",  "growth": 85,  "revenue": 120, "verdict": "양호함"},
    {"company": "CYTUR",     "growth": 42,  "revenue": 30,  "verdict": "주의"},
    {"company": "Mearitt",   "growth": 110, "revenue": 80,  "verdict": "탁월함"},
    {"company": "인탑스",    "growth": 75,  "revenue": 55,  "verdict": "양호함"},
]


# ================================
# 2. JSON 파일로 저장
# ================================
with open("portfolio.json", "w", encoding="utf-8") as f:
    json.dump(portfolio, f, ensure_ascii=False, indent=4)

print("portfolio.json 저장 완료!")


# ================================
# 3. JSON 파일 불러오기
# ================================
with open("portfolio.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)

print("\n=== 불러온 포트폴리오 ===")
for item in loaded:
    print(f"{item['company']}: 성장률 {item['growth']}%, 매출 {item['revenue']}억 → {item['verdict']}")


# ================================
# 4. 특정 회사만 검색
# ================================
search = "Mearitt"
result = [item for item in loaded if item["company"] == search]

print(f"\n=== {search} 검색 결과 ===")
print(result)