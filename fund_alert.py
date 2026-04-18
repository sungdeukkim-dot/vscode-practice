import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# ================================
# 설정 — 여기만 본인 정보로 바꿀 것
# ================================
TELEGRAM_TOKEN   = os.environ.get("8613964576:AAHwzxro25iRAOlDTZRnTd29VPdLn-yznpc ", "")
TELEGRAM_CHAT_ID = os.environ.get("49924895", "")
SEEN_FILE        = "seen_announcements.json"


# ================================
# 텔레그램 메시지 발송
# ================================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id":    TELEGRAM_CHAT_ID,
        "text":       message,
        "parse_mode": "HTML",
    }
    try:
        res = requests.post(url, data=payload, timeout=10)
        if res.status_code == 200:
            print(f"  [텔레그램 발송 완료]")
        else:
            print(f"  [발송 실패] {res.text}")
    except Exception as e:
        print(f"  [발송 오류] {e}")


# ================================
# 기존 공고 목록 불러오기 / 저장
# ================================
def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=4)


# ================================
# 각 기관별 크롤러
# ================================
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def crawl_kvic():
    """한국벤처투자"""
    results = []
    try:
        url = "https://www.kvic.or.kr/site/main/board/list?boardManagementNo=23"
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        rows = soup.select(".board-list tbody tr")
        for row in rows[:5]:
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
    """한국성장금융"""
    results = []
    try:
        url = "https://www.kgrowth.or.kr/bbs/B0000007/list.do"
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        rows = soup.select(".board_list tbody tr")
        for row in rows[:5]:
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
    """서울산업진흥원"""
    results = []
    try:
        url = "https://www.sba.seoul.kr/kr/SB0603"
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        rows = soup.select(".board-list tbody tr")
        for row in rows[:5]:
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
    """과학기술인공제회"""
    results = []
    try:
        url = "https://www.ktcu.or.kr/board/notice/list.do"
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        rows = soup.select(".board_list tbody tr")
        for row in rows[:5]:
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


# ================================
# 키워드 필터 — 관련 공고만 감지
# ================================
KEYWORDS = [
    "출자", "펀드", "블라인드", "GP", "운용사",
    "모태", "벤처", "투자", "공고", "선정",
    "AI융합", "혁신성장", "NEXT UNICORN"
]

def is_relevant(title):
    return any(kw in title for kw in KEYWORDS)


# ================================
# 핵심 함수 — 전체 기관 체크
# ================================
def check_all():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 공고 체크 시작...")

    # 오늘 날짜 기준으로 필터링
    today = datetime.now().strftime("%Y")  # 연도 기준 (최근 공고만)

    sources = [
        ("한국벤처투자",    crawl_kvic),
        ("한국성장금융",    crawl_kgrowth),
        ("서울산업진흥원",  crawl_sba),
        ("과학기술인공제회", crawl_ktcu),
    ]

    found_any = False

    for org_name, crawler in sources:
        print(f"  {org_name} 체크 중...")
        announcements = crawler()

        for item in announcements:
            title = item["title"]

            # 키워드 관련 공고만 발송
            if is_relevant(title):
                message = (
                    f"<b>[출자 공고 알림]</b>\n\n"
                    f"<b>기관:</b> {org_name}\n"
                    f"<b>제목:</b> {title}\n"
                    f"<b>날짜:</b> {item['date']}\n"
                    f"<b>링크:</b> {item['link']}"
                )
                send_telegram(message)
                print(f"    → 발송: {title[:40]}...")
                found_any = True

    if not found_any:
        print("  신규 관련 공고 없음.")

    print("  체크 완료.\n")


# ================================
# 실행
# ================================
if __name__ == "__main__":
    print("=" * 50)
    print("   출자 공고 알림 시스템 시작")
    print("=" * 50)

    # GitHub Actions에서는 1회 실행 후 종료
    check_all()