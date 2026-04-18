import schedule
import time
import requests
from datetime import datetime


def fetch_and_alert():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 환율 체크 중...")
    try:
        res = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
        if res.status_code == 200:
            krw = res.json()["rates"]["KRW"]
            print(f"  USD/KRW : {krw:,.0f} 원")

            # 환율 급등 경보 (1,400원 이상이면 경고)
            if krw >= 1400:
                print("  [경고] 환율 1,400원 이상 - 포트폴리오 점검 필요!")
            else:
                print("  [정상] 환율 안정 구간")
    except Exception as e:
        print(f"  오류: {e}")


# ================================
# 스케줄 설정
# ================================
print("스케줄러 시작. 10초마다 환율 체크.")
print("종료하려면 Ctrl+C 누를 것.\n")

schedule.every(10).seconds.do(fetch_and_alert)   # 테스트용: 10초마다
# schedule.every().hour.do(fetch_and_alert)       # 실전: 1시간마다
# schedule.every().day.at("09:00").do(fetch_and_alert)  # 실전: 매일 9시

fetch_and_alert()  # 시작하자마자 1회 즉시 실행

while True:
    schedule.run_pending()
    time.sleep(1)