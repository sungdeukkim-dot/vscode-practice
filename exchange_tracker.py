import requests
import json
import os
from datetime import datetime

SAVE_FILE = "exchange_history.json"


def load_history():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def fetch_exchange():
    url = "https://open.er-api.com/v6/latest/USD"
    response = requests.get(url)

    if response.status_code != 200:
        print("API 호출 실패")
        return None

    data = response.json()
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "USD_KRW": round(data["rates"]["KRW"], 2),
        "USD_JPY": round(data["rates"]["JPY"], 2),
        "USD_EUR": round(data["rates"]["EUR"], 4),
        "USD_CNY": round(data["rates"]["CNY"], 4),
    }


def show_history(history):
    if not history:
        print("\n저장된 데이터 없음.\n")
        return
    print("\n=== 환율 기록 ===")
    print(f"{'시간':<18} {'KRW':>8} {'JPY':>8} {'EUR':>8} {'CNY':>8}")
    print("-" * 55)
    for item in history:
        print(f"{item['timestamp']:<18} "
              f"{item['USD_KRW']:>8,.0f} "
              f"{item['USD_JPY']:>8,.0f} "
              f"{item['USD_EUR']:>8.4f} "
              f"{item['USD_CNY']:>8.4f}")
    print()


def main():
    while True:
        print("=" * 40)
        print("   환율 트래커 v1.0")
        print("=" * 40)
        print("1. 현재 환율 조회 & 저장")
        print("2. 기록 보기")
        print("3. 기록 초기화")
        print("0. 종료")
        print("-" * 40)

        choice = input("메뉴 선택: ").strip()

        if choice == "1":
            print("\n환율 데이터 가져오는 중...")
            result = fetch_exchange()
            if result:
                history = load_history()
                history.append(result)
                save_history(history)
                print(f"\n[{result['timestamp']}] 저장 완료!")
                print(f"  USD → KRW : {result['USD_KRW']:,.0f} 원")
                print(f"  USD → JPY : {result['USD_JPY']:,.0f} 엔")
                print(f"  USD → EUR : {result['USD_EUR']:.4f} 유로")
                print(f"  USD → CNY : {result['USD_CNY']:.4f} 위안\n")

        elif choice == "2":
    history = load_history()
    show_history(history)
    if history:
        krw_values = [item["USD_KRW"] for item in history]
        print(f"최고 환율: {max(krw_values):,.0f} 원")
        print(f"최저 환율: {min(krw_values):,.0f} 원")
        print(f"평균 환율: {sum(krw_values)/len(krw_values):,.0f} 원")

        elif choice == "3":
            save_history([])
            print("\n기록 초기화 완료.\n")

        elif choice == "0":
            print("\n종료합니다.\n")
            break

        else:
            print("\n0~3 중에서 선택할 것.\n")


if __name__ == "__main__":
    main()
    # 기록 중 KRW 최고값 / 최저값 출력
krw_values = [item["USD_KRW"] for item in history]
print(f"최고 환율: {max(krw_values):,.0f} 원")
print(f"최저 환율: {min(krw_values):,.0f} 원")
print(f"평균 환율: {sum(krw_values)/len(krw_values):,.0f} 원")