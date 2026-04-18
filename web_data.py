import requests

# ================================
# 1. 기본 GET 요청
# ================================
url = "https://httpbin.org/get"
response = requests.get(url)

print(f"상태코드: {response.status_code}")  # 200이면 성공
print(f"응답 타입: {response.headers['Content-Type']}")


# ================================
# 2. JSON 데이터 받아오기
# ================================
# 무료 환율 API (실제 데이터)
url2 = "https://open.er-api.com/v6/latest/USD"
response2 = requests.get(url2)

if response2.status_code == 200:
    data = response2.json()
    usd_to_krw = data["rates"]["KRW"]
    usd_to_jpy = data["rates"]["JPY"]
    usd_to_eur = data["rates"]["EUR"]

    print("\n=== 실시간 환율 (기준: 1 USD) ===")
    print(f"USD → KRW : {usd_to_krw:,.0f} 원")
    print(f"USD → JPY : {usd_to_jpy:,.0f} 엔")
    print(f"USD → EUR : {usd_to_eur:.4f} 유로")
else:
    print("API 호출 실패")