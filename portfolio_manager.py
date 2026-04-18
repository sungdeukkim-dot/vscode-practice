import json
import os

DATA_FILE = "portfolio_data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def evaluate(growth, revenue):
    if growth >= 100:
        g = 3
    elif growth >= 50:
        g = 2
    elif growth >= 0:
        g = 1
    else:
        g = 0

    if revenue >= 100:
        r = 3
    elif revenue >= 50:
        r = 2
    elif revenue >= 10:
        r = 1
    else:
        r = 0

    total = g + r

    if total >= 5:
        return "[최우선] 탁월함"
    elif total >= 3:
        return "[검토]   양호함"
    elif total >= 1:
        return "[주의]   부족함"
    else:
        return "[제외]   부적격"


def show_all(data):
    if not data:
        print("\n등록된 회사가 없음.\n")
        return
    print("\n" + "=" * 55)
    print(f"{'번호':<5} {'회사명':<14} {'성장률':>6} {'매출액':>8}  판정")
    print("=" * 55)
    for i, item in enumerate(data, 1):
        verdict = evaluate(item["growth"], item["revenue"])
        print(f"{i:<5} {item['company']:<14} {item['growth']:>5}%  {item['revenue']:>6}억   {verdict}")
    print("=" * 55 + "\n")


def add_company(data):
    print("\n--- 회사 추가 ---")
    name    = input("회사명: ")
    growth  = int(input("매출 성장률 (%): "))
    revenue = int(input("매출액 (억원): "))
    stage   = input("투자 단계 (예: Series A): ")

    company = {
        "company": name,
        "growth": growth,
        "revenue": revenue,
        "stage": stage
    }
    data.append(company)
    save_data(data)
    print(f"\n'{name}' 추가 완료!\n")


def search_company(data):
    keyword = input("\n검색할 회사명: ")
    results = [item for item in data if keyword in item["company"]]
    if not results:
        print("검색 결과 없음.\n")
    else:
        for item in results:
            verdict = evaluate(item["growth"], item["revenue"])
            print(f"\n>> {item['company']}")
            print(f"   성장률: {item['growth']}%")
            print(f"   매출액: {item['revenue']}억")
            print(f"   단계:   {item['stage']}")
            print(f"   판정:   {verdict}\n")


def delete_company(data):
    show_all(data)
    if not data:
        return
    try:
        num = int(input("삭제할 번호 입력: "))
        removed = data.pop(num - 1)
        save_data(data)
        print(f"\n'{removed['company']}' 삭제 완료!\n")
    except (IndexError, ValueError):
        print("잘못된 번호임.\n")


def run_evaluation(data):
    if not data:
        print("\n등록된 회사가 없음.\n")
        return
    print("\n=== 전체 투자 판정 결과 ===")
    top = []
    for item in data:
        verdict = evaluate(item["growth"], item["revenue"])
        print(f"  {item['company']}: {verdict}")
        if "탁월함" in verdict:
            top.append(item["company"])
    if top:
        print(f"\n최우선 검토 회사: {', '.join(top)}")
    print()


def main():
    data = load_data()

    while True:
        print("=" * 40)
        print("   투자 포트폴리오 관리 도구 v1.0")
        print("=" * 40)
        print("1. 전체 포트폴리오 조회")
        print("2. 회사 추가")
        print("3. 회사 검색")
        print("4. 회사 삭제")
        print("5. 투자 판정 실행")
        print("0. 종료")
        print("-" * 40)

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
            run_evaluation(data)
        elif choice == "0":
            print("\n종료합니다.\n")
            break
        else:
            print("\n0~5 중에서 선택할 것.\n")


if __name__ == "__main__":
    main()