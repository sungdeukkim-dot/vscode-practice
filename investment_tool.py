import json
import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

DATA_FILE = "investment_data.json"


# ================================
# 데이터 불러오기 / 저장
# ================================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# ================================
# 투자 판정
# ================================
def evaluate(growth, revenue):
    g = 3 if growth >= 100 else 2 if growth >= 50 else 1 if growth >= 0 else 0
    r = 3 if revenue >= 100 else 2 if revenue >= 50 else 1 if revenue >= 10 else 0
    total = g + r
    if total >= 5:
        return "[A] Excellent"
    elif total >= 3:
        return "[B] Good"
    elif total >= 1:
        return "[C] Caution"
    else:
        return "[D] Reject"


# ================================
# 1. 전체 조회
# ================================
def show_all(data):
    if not data:
        print("\n등록된 회사 없음.\n")
        return
    print("\n" + "=" * 60)
    print(f"{'No.':<5} {'회사명':<14} {'성장률':>6} {'매출액':>8} {'단계':<12} 판정")
    print("=" * 60)
    for i, item in enumerate(data, 1):
        verdict = evaluate(item["growth"], item["revenue"])
        print(f"{i:<5} {item['company']:<14} {item['growth']:>5}%"
              f"  {item['revenue']:>6}억  {item['stage']:<12} {verdict}")
    print("=" * 60 + "\n")


# ================================
# 2. 회사 추가
# ================================
def add_company(data):
    print("\n--- 회사 추가 ---")
    name    = input("회사명: ")
    growth  = int(input("매출 성장률 (%): "))
    revenue = int(input("매출액 (억원): "))
    stage   = input("투자 단계 (Series A/B 등): ")
    memo    = input("메모 (없으면 Enter): ")

    company = {
        "company": name,
        "growth": growth,
        "revenue": revenue,
        "stage": stage,
        "memo": memo,
        "added": datetime.now().strftime("%Y-%m-%d"),
    }
    data.append(company)
    save_data(data)
    print(f"\n'{name}' 추가 완료!\n")


# ================================
# 3. 회사 검색
# ================================
def search_company(data):
    keyword = input("\n검색할 회사명: ")
    results = [item for item in data if keyword.lower() in item["company"].lower()]
    if not results:
        print("검색 결과 없음.\n")
    else:
        for item in results:
            verdict = evaluate(item["growth"], item["revenue"])
            print(f"\n>> {item['company']}")
            print(f"   성장률 : {item['growth']}%")
            print(f"   매출액 : {item['revenue']}억")
            print(f"   단계   : {item['stage']}")
            print(f"   판정   : {verdict}")
            print(f"   메모   : {item.get('memo', '-')}")
            print(f"   등록일 : {item.get('added', '-')}\n")


# ================================
# 4. 회사 삭제
# ================================
def delete_company(data):
    show_all(data)
    if not data:
        return
    try:
        num = int(input("삭제할 번호: "))
        removed = data.pop(num - 1)
        save_data(data)
        print(f"\n'{removed['company']}' 삭제 완료!\n")
    except (IndexError, ValueError):
        print("잘못된 번호.\n")


# ================================
# 5. pandas 분석 + Excel 저장
# ================================
def analyze(data):
    if len(data) < 2:
        print("\n분석하려면 회사가 2개 이상 필요함.\n")
        return

    df = pd.DataFrame(data)
    df["verdict"] = df.apply(lambda row: evaluate(row["growth"], row["revenue"]), axis=1)
    df["score"]   = df["growth"] * 0.6 + df["revenue"] * 0.4

    print("\n=== 종합 분석 결과 ===")
    print(df[["company", "growth", "revenue", "score", "verdict"]]
          .sort_values("score", ascending=False)
          .to_string(index=False))

    print(f"\n평균 성장률 : {df['growth'].mean():.1f}%")
    print(f"평균 매출액 : {df['revenue'].mean():.1f}억")
    print(f"최고 성장률 : {df['growth'].max()}% ({df.loc[df['growth'].idxmax(), 'company']})")
    print(f"최고 매출액 : {df['revenue'].max()}억 ({df.loc[df['revenue'].idxmax(), 'company']})")

    # Excel 저장
    excel_file = "investment_analysis.xlsx"
    df.to_excel(excel_file, index=False)
    print(f"\nExcel 저장 완료: {excel_file}\n")


# ================================
# 6. 차트 생성
# ================================
def make_chart(data):
    if len(data) < 2:
        print("\n차트 생성하려면 회사가 2개 이상 필요함.\n")
        return

    df = pd.DataFrame(data)
    df["score"] = df["growth"] * 0.6 + df["revenue"] * 0.4

    plt.figure(figsize=(14, 5))

    # 차트 1. 성장률 막대
    plt.subplot(1, 3, 1)
    colors = ["steelblue" if g >= 70 else "orange" if g >= 40 else "tomato"
              for g in df["growth"]]
    plt.bar(df["company"], df["growth"], color=colors)
    plt.title("Growth Rate (%)")
    plt.xticks(rotation=20)
    plt.ylabel("%")

    # 차트 2. 산점도
    plt.subplot(1, 3, 2)
    plt.scatter(df["growth"], df["revenue"], s=200, alpha=0.7, color="steelblue")
    for _, row in df.iterrows():
        plt.annotate(row["company"], (row["growth"], row["revenue"]),
                     textcoords="offset points", xytext=(5, 5), fontsize=8)
    plt.title("Growth vs Revenue")
    plt.xlabel("Growth (%)")
    plt.ylabel("Revenue (100M)")
    plt.grid(True, alpha=0.3)

    # 차트 3. 종합점수 막대
    plt.subplot(1, 3, 3)
    df_sorted = df.sort_values("score", ascending=True)
    plt.barh(df_sorted["company"], df_sorted["score"], color="mediumseagreen")
    plt.title("Total Score")
    plt.xlabel("Score")

    plt.tight_layout()
    chart_file = "investment_chart.png"
    plt.savefig(chart_file, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"\n차트 저장 완료: {chart_file}\n")


# ================================
# 7. 실시간 환율 조회
# ================================
def fetch_rate():
    print("\n환율 데이터 가져오는 중...")
    try:
        res = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
        if res.status_code == 200:
            rates = res.json()["rates"]
            print(f"\n=== 실시간 환율 (기준: 1 USD) ===")
            print(f"  KRW : {rates['KRW']:,.0f} 원")
            print(f"  JPY : {rates['JPY']:,.0f} 엔")
            print(f"  EUR : {rates['EUR']:.4f} 유로")
            print(f"  CNY : {rates['CNY']:.4f} 위안\n")
        else:
            print("API 호출 실패.\n")
    except Exception as e:
        print(f"오류: {e}\n")


# ================================
# 메인 메뉴
# ================================
def main():
    data = load_data()

    while True:
        print("=" * 45)
        print("   투자 분석 자동화 도구 v2.0")
        print(f"   등록 회사: {len(data)}개")
        print("=" * 45)
        print("1. 전체 포트폴리오 조회")
        print("2. 회사 추가")
        print("3. 회사 검색")
        print("4. 회사 삭제")
        print("5. pandas 분석 + Excel 저장")
        print("6. 차트 생성")
        print("7. 실시간 환율 조회")
        print("0. 종료")
        print("-" * 45)

        choice = input("메뉴 선택: ").strip()

        if choice == "1":
            show_all(data)
        elif choice == "2":
            add_company(data)
        elif choice == "3":
            search_company(data)
        elif choice == "4":
            delete_company(data)
        elif choice == "5":
            analyze(data)
        elif choice == "6":
            make_chart(data)
        elif choice == "7":
            fetch_rate()
        elif choice == "0":
            print("\n종료합니다.\n")
            break
        else:
            print("\n0~7 중에서 선택할 것.\n")


if __name__ == "__main__":
    main()