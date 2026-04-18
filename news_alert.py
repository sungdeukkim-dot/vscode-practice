import requests
from bs4 import BeautifulSoup
import os
import json
from datetime import datetime
import time

TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
GIST_TOKEN       = os.environ.get("GIST_TOKEN", "")
GIST_ID          = os.environ.get("GIST_ID", "")
GIST_FILENAME    = "seen_news.json"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# ================================
# 모니터링할 키워드 목록
# 회사명, 제품명, 인물명 등 자유롭게 추가
# ================================
def load_keywords():
    try:
        res = requests.get(
            f"https://api.github.com/gists/{GIST_ID}",
            headers={
                "Authorization": f"token {GIST_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=10
        )
        if res.status_code == 200:
            files = res.json().get("files", {})
            if "keywords.json" in files:
                data = json.loads(files["keywords.json"]["content"])
                kws  = data.get("keywords", [])
                print(f"  키워드 {len(kws)}개 로드됨: {kws}")
                return kws
    except Exception as e:
        print(f"  [키워드 로드 오류] {e}")
    return ["인포스테크놀로지", "한국형 테이저건"]


# ================================
# Gist 읽기 / 쓰기
# ================================
def load_seen():
    try:
        res = requests.get(
            f"https://api.github.com/gists/{GIST_ID}",
            headers={
                "Authorization": f"token {GIST_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=10
        )
        if res.status_code == 200:
            files = res.json().get("files", {})
            if GIST_FILENAME in files:
                content = files[GIST_FILENAME]["content"]
                return json.loads(content)
    except Exception as e:
        print(f"  [Gist 읽기 오류] {e}")
    return {}


def save_seen(seen):
    try:
        requests.patch(
            f"https://api.github.com/gists/{GIST_ID}",
            headers={
                "Authorization": f"token {GIST_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            },
            json={
                "files": {
                    GIST_FILENAME: {
                        "content": json.dumps(seen, ensure_ascii=False, indent=2)
                    }
                }
            },
            timeout=10
        )
        print("  [Gist 저장 완료]")
    except Exception as e:
        print(f"  [Gist 저장 오류] {e}")


# ================================
# 텔레그램 발송
# ================================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        res = requests.post(url, data={
            "chat_id":    TELEGRAM_CHAT_ID,
            "text":       message,
            "parse_mode": "HTML",
        }, timeout=10)
        if res.status_code == 200:
            print("  [텔레그램 발송 완료]")
        else:
            print(f"  [발송 실패] {res.status_code}")
    except Exception as e:
        print(f"  [발송 오류] {e}")


# ================================
# 네이버 뉴스 검색
# ================================
def search_naver_news(keyword):
    results = []
    try:
        query = requests.utils.quote(keyword)
        url   = f"https://search.naver.com/search.naver?where=news&query={query}&sort=1"
        res   = requests.get(url, headers=headers, timeout=10)
        soup  = BeautifulSoup(res.text, "html.parser")

        articles = soup.select(".news_area")
        for article in articles[:5]:
            title_tag = article.select_one(".news_tit")
            press_tag = article.select_one(".info_group .press")
            date_tag  = article.select_one(".info_group span.info")

            if title_tag:
                title = title_tag.get_text(strip=True)
                link  = title_tag.get("href", "")
                press = press_tag.get_text(strip=True) if press_tag else "언론사 미상"
                date  = date_tag.get_text(strip=True)  if date_tag  else ""
                results.append({
                    "title": title,
                    "link":  link,
                    "press": press,
                    "date":  date,
                    "source": "네이버뉴스"
                })
    except Exception as e:
        print(f"  [네이버 검색 오류 - {keyword}] {e}")
    return results


# ================================
# 구글 뉴스 검색
# ================================
def search_google_news(keyword):
    results = []
    try:
        query = requests.utils.quote(keyword)
        url   = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
        res   = requests.get(url, headers=headers, timeout=10)
        soup  = BeautifulSoup(res.content, "xml")

        items = soup.select("item")
        for item in items[:5]:
            title     = item.find("title").get_text(strip=True)     if item.find("title")     else ""
            link      = item.find("link").get_text(strip=True)      if item.find("link")      else ""
            pub_date  = item.find("pubDate").get_text(strip=True)   if item.find("pubDate")   else ""
            source    = item.find("source").get_text(strip=True)    if item.find("source")    else "구글뉴스"

            if title:
                results.append({
                    "title":  title,
                    "link":   link,
                    "press":  source,
                    "date":   pub_date,
                    "source": "구글뉴스"
                })
    except Exception as e:
        print(f"  [구글 검색 오류 - {keyword}] {e}")
    return results


# ================================
# 핵심 함수 — 전체 키워드 뉴스 체크
# ================================
def check_news():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 뉴스 체크 시작...")
    WATCH_KEYWORDS = load_keywords()
    seen      = load_seen()
    new_count = 0

    for keyword in WATCH_KEYWORDS:
        print(f"\n  [{keyword}] 검색 중...")

        if keyword not in seen:
            seen[keyword] = []

        # 네이버 + 구글 동시 검색
        articles = search_naver_news(keyword) + search_google_news(keyword)
        time.sleep(1)  # 서버 부하 방지

        for article in articles:
            title = article["title"]

            # 중복 체크
            if title in seen[keyword]:
                continue

            # 새 기사 감지
            seen[keyword].append(title)
            new_count += 1

            # 텔레그램 발송
            message = (
                f"<b>[뉴스 알림] {keyword}</b>\n\n"
                f"<b>제목:</b> {title}\n"
                f"<b>언론사:</b> {article['press']}\n"
                f"<b>날짜:</b> {article['date']}\n"
                f"<b>출처:</b> {article['source']}\n"
                f"<b>링크:</b> {article['link']}"
            )
            send_telegram(message)
            print(f"    → 발송: {title[:40]}...")
            time.sleep(0.5)  # 텔레그램 발송 간격

    save_seen(seen)
    print(f"\n  체크 완료. 신규 기사 {new_count}건 감지.\n")


if __name__ == "__main__":
    print("뉴스 알림 시스템 시작")
    check_news()
