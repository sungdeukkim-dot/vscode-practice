import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime


def get_stock_info(code):
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    try:
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        # 종목명
        name_tag = soup.select_one(".wrap_company h2 a")
        name = name_tag.get_text(strip=True) if name_tag else "N/A"

        # 현재가
        price_tag = soup.select_one(".no_today .blind")
        price = price_tag.get_text(strip=True) if price_tag else "N/A"

        # 전일대비
        change_tag = soup.select_one(".no_exday .blind")
        change = change_tag.get_text(strip=True) if change_tag else "N/A"

        # 시가총액
        market_cap = "N/A"
        for tr in soup.select(".tb_type1 tr"):
            th = tr.select_one("th")
            if th and "시가총액" in th.get_text():
                td = tr.select_one("td")
                if td:
                    market_cap = td.get_text(strip=True)
                break

        return {
            "code":       code,
            "name":       name,
            "price":      price,
            "change":     change,
            "market_cap": market_cap,
            "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    except Exception as e:
        print(f"오류 ({code}): {e}")
        return None


# ================================
# 관심 종목 리스트
# ================================
watchlist = [
    ("005930", "삼성전자"),
    ("000660", "SK하이닉스"),
    ("035420", "NAVER"),
    ("051910", "LG화학"),
    ("006400", "삼성SDI"),
]

print("=" * 60)
print("   네이버 금융 실시간 시세")
print("=" * 60)
print(f"{'종목명':<14} {'현재가':>10} {'전일대비':>10} {'시가총액':>14}")
print("-" * 60)

results = []
for code, name in watchlist:
    info = get_stock_info(code)
    if info:
        print(f"{info['name']:<14} {info['price']:>10} "
              f"{info['change']:>10} {info['market_cap']:>14}")
        results.append(info)

print("=" * 60)

# JSON 저장
with open("stock_data.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print(f"\nstock_data.json 저장 완료 ({len(results)}개 종목)")