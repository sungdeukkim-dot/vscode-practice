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
    """
    반환값: (seen_dict, load_success)
    load_success=False 이면 Gist 연결 실패 → 발송 자체를 중단해야 함
    """
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
                return json.loads(content), True
            else:
                # 파일이 없으면 첫 실행으로 간주 → 빈 dict로 정상 시작
                print("  [Gist] seen_news.json 없음 → 첫 실행으로 초기화")
                return {}, True
        else:
            print(f"  [Gist 읽기 실패] HTTP {res.status_code}")
            return {}, False
    except Exception as e:
        print(f"  [Gist 읽기 오류] {e}")
        return {}, False  # ← 실패 시 False 반환


def save_seen(seen):
    # seen의 각 키워드별 링크 목록을 최근 200개로 제한 (무한 증가 방지)
    for kw in seen:
        if len(seen[kw]) > 200:
            seen[kw] = seen[kw][-200:]
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
                link  = title_tag.get("href", "").strip()
                press = press_tag.get_text(strip=True) if press_tag else "언론사 미상"
                date  = date_tag.get_text(strip=True)  if date_tag  else ""

                if link:  # link 없는 기사는 스킵
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
            title    = item.find("title").get_text(strip=True) if item.find("title") else ""
            pub_date = item.find("pubDate").get_text(strip=True) if item.find("pubDate") else ""
            source   = item.find("source").get_text(strip=True) if item.find("source") else "구글뉴스"

            # 구글 RSS <link>는 <title> 다음 텍스트 노드로 존재 → next_sibling으로 파싱
            link_tag = item.find("link")
            if link_tag:
                link = (link_tag.next_sibling or "").strip()
            else:
                link = ""

            if title and link:
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

    # Gist 로드 실패 시 중복 발송 위험 → 즉시 종료
    seen, load_ok = load_seen()
    if not load_ok:
        print("  [오류] Gist 로드 실패 → 중복 발송 방지를 위해 이번 실행 건너뜀")
        return

    new_count = 0

    for keyword in WATCH_KEYWORDS:
        print(f"\n  [{keyword}] 검색 중...")

        if keyword not in seen:
            seen[keyword] = []

        seen_links = set(seen[keyword])  # ← set으로 변환하여 O(1) 조회

        # 네이버 + 구글 동시 검색
        articles = search_naver_news(keyword) + search_google_news(keyword)
        time.sleep(1)

        for article in articles:
            link = article["link"]

            if not link:
                continue  # link 없으면 dedup 불가 → 스킵

            # ★ 핵심: title이 아닌 link로 중복 체크
            if link in seen_links:
                continue

            # 새 기사 감지
            seen[keyword].append(link)
            seen_links.add(link)
            new_count += 1

            message = (
                f"<b>[뉴스 알림] {keyword}</b>\n\n"
                f"<b>제목:</b> {article['title']}\n"
                f"<b>언론사:</b> {article['press']}\n"
                f"<b>날짜:</b> {article['date']}\n"
                f"<b>출처:</b> {article['source']}\n"
                f"<b>링크:</b> {link}"
            )
            send_telegram(message)
            print(f"    → 발송: {article['title'][:40]}...")
            time.sleep(0.5)

    save_seen(seen)
    print(f"\n  체크 완료. 신규 기사 {new_count}건 감지.\n")


if __name__ == "__main__":
    print("뉴스 알림 시스템 시작")
    check_news()
