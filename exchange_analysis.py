import pandas as pd
import matplotlib.pyplot as plt
import json
import os

SAVE_FILE = "exchange_history.json"

# ================================
# 1. 데이터 불러오기
# ================================
if not os.path.exists(SAVE_FILE):
    print("exchange_history.json 없음. 7강 exchange_tracker.py 먼저 실행할 것.")
    exit()

with open(SAVE_FILE, "r", encoding="utf-8") as f:
    history = json.load(f)

if len(history) < 2:
    print("데이터가 2개 이상 필요함. exchange_tracker.py 메뉴 1번 더 실행할 것.")
    exit()

df = pd.DataFrame(history)
print("=== 환율 데이터 ===")
print(df)

# ================================
# 2. 기본 통계
# ================================
print("\n=== KRW 통계 ===")
print(f"최고: {df['USD_KRW'].max():,.0f} 원")
print(f"최저: {df['USD_KRW'].min():,.0f} 원")
print(f"평균: {df['USD_KRW'].mean():,.0f} 원")

# ================================
# 3. 차트 그리기
# ================================
plt.figure(figsize=(10, 4))
plt.plot(df["timestamp"], df["USD_KRW"],
         marker="o", linewidth=2,
         color="steelblue", markersize=8)

plt.title("USD/KRW Exchange Rate Trend")
plt.xlabel("Time")
plt.ylabel("KRW per 1 USD")
plt.xticks(rotation=30)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("exchange_chart.png", dpi=150, bbox_inches="tight")
plt.show()

print("\n차트 저장 완료: exchange_chart.png")