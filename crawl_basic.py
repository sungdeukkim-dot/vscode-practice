import requests
from bs4 import BeautifulSoup

# ================================
# 1. 웹페이지 HTML 가져오기
# ================================
url = "https://news.ycombinator.com"  # 실리콘밸리 테크 뉴스
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
print(f"상태코드: {response.status_code}")

# ================================
# 2. HTML 파싱
# ================================
soup = BeautifulSoup(response.text, "html.parser")

# ================================
# 3. 뉴스 제목 추출
# ================================
articles = soup.select(".titleline > a")

print(f"\n=== Hacker News 상위 {len(articles)}개 기사 ===\n")
for i, article in enumerate(articles[:10], 1):
    title = article.get_text()
    link  = article.get("href", "")
    print(f"{i:>2}. {title[:60]}")
    print(f"    {link[:70]}\n")