import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

KEYWORDS = [
    "출자", "펀드", "블라인드", "GP", "운용사",
    "모태", "벤처", "투자", "공고", "선정",
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        res = requests.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
        }, timeout=10)
        if res.status_code == 200:
            print("  [발송 완료]")
        else:
            print(f"  [발송 실패] {res.text}")
    except Exception as e:
        print(f"  [발송 오류] {e}")

def is_relevant(title):
    return any(kw in title for kw in KEYWORDS)

def crawl_kvic():
    results = []
    try:
        url = "https://www.kvic.or.kr/site/main/board/list?boardManagementNo=23"
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        for row in soup.select(".board-list tbody tr")[:5]:
            title_tag = row.select_one("td.subject a")
            date_tag  = row.select_one("td.date")
            if title_tag:
                title = title_tag.get_text(strip=True)
                date  = date_tag.get_text(strip=True) if date_tag else ""
                href  = title_tag.get("href", "")
                link  = f"https://www.kvic.or.kr{href}" if href.startswith("/") else href
                results.append({"title": title, "date": date, "link": link})
    except Exception as e:
        print(f"  [한국벤처투자 오류] {e}")
    return results

def crawl_kgrowth():
    results = []
    try:
        url = "https://www.kgrowth.or.kr/bbs/B0000007/list.do"
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        for row in soup.select(".board_list tbody tr")[:5]:
            title_tag = row.select_one("td.title a")
            date_tag  = row.select_one("td.date")
            if title_tag:
                title = title_tag.get_text(strip=True)
                date  = date_tag.get_text(strip=True) if date_tag else ""
                href  = title_tag.get("href", "")
                link  = f"https://www.kgrowth.or.kr{href}" if href.startswith("/") else href
                results.append({"title": title, "date": date, "link": link})
    except Exception as e:
        print(f"  [한국성장금융 오류] {e}")
    return results

def crawl_sba():
    results = []
    try:
        url = "https://www.sba.seoul.kr/kr/SB0603"
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        for row in soup.select(".board-list tbody tr")[:5]:
            title_tag = row.select_one("td.tit a")
            date_tag  = row.select_one("td.date")
            if title_tag:
                title = title_tag.get_text(strip=True)
                date  = date_tag.get_text(strip=True) if date_tag else ""
                href  = title_tag.get("href", "")
                link  = f"https://www.sba.seoul.kr{href}" if href.startswith("/") else href
                results.append({"title": title, "date": date, "link": link})
    except Exception as e:
        print(f"  [서울산업진흥원 오류] {e}")
    return results

def crawl_ktcu():
    results = []
    try:
        url = "https://www.ktcu.or.kr/board/notice/list.do"
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        for row in soup.select(".board_list tbody tr")[:5]:
            title_tag = row.select_one("td.title a")
            date_tag  = row.select_one("td.date")
            if title_tag:
                title = title_tag.get_text(strip=True)
                date  = date_tag.get_text(strip=True) if date_tag else ""
                href  = title_tag.get("href", "")
                link  = f"https://www.ktcu.or.kr{href}" if href.startswith("/") else href
                results.append({"title": title, "date": date, "link": link})
    except Exception as e:
        print(f"  [과학기술인공제회 오류] {e}")
    return results

def check_all():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 공고 체크 시작...")

    sources = [
        ("한국벤처투자",    crawl_kvic),
        ("한국성장금융",    crawl_kgrowth),
        ("서울산업진흥원",  crawl_sba),
        ("과학기술인공제회", crawl_ktcu),
    ]

    found_any = False

    for org_name, crawler in sources:
        print(f"  {org_name} 체크 중...")
        for item in crawler():
            if is_relevant(item["title"]):
                send_telegram(
                    f"<b>[출자 공고 알림]</b>\n\n"
                    f"<b>기관:</b> {org_name}\n"
                    f"<b>제목:</b> {item['title']}\n"
                    f"<b>날짜:</b> {item['date']}\n"
                    f"<b>링크:</b> {item['link']}"
                )
                print(f"    → 발송: {item['title'][:40]}...")
                found_any = True

    if not found_any:
        print("  신규 관련 공고 없음.")
    print("  체크 완료.\n")

if __name__ == "__main__":
    print("출자 공고 알림 시스템 시작")
    check_all()
