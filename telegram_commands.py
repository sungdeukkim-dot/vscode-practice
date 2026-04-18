import requests
import os
import json

TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
GIST_TOKEN       = os.environ.get("GIST_TOKEN", "")
GIST_ID          = os.environ.get("GIST_ID", "")
KEYWORDS_FILE    = "keywords.json"
OFFSET_FILE      = "telegram_offset.json"


# ================================
# Gist 읽기
# ================================
def gist_read(filename):
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
            if filename in files:
                return json.loads(files[filename]["content"])
    except Exception as e:
        print(f"[Gist 읽기 오류] {e}")
    return None


# ================================
# Gist 쓰기
# ================================
def gist_write(filename, data):
    try:
        requests.patch(
            f"https://api.github.com/gists/{GIST_ID}",
            headers={
                "Authorization": f"token {GIST_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            },
            json={
                "files": {
                    filename: {
                        "content": json.dumps(data, ensure_ascii=False, indent=2)
                    }
                }
            },
            timeout=10
        )
    except Exception as e:
        print(f"[Gist 쓰기 오류] {e}")


# ================================
# 텔레그램 발송
# ================================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id":    TELEGRAM_CHAT_ID,
        "text":       message,
        "parse_mode": "HTML",
    }, timeout=10)


# ================================
# 텔레그램 업데이트 가져오기
# ================================
def get_updates(offset=None):
    url    = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {"timeout": 0, "limit": 100}
    if offset:
        params["offset"] = offset
    try:
        res = requests.get(url, params=params, timeout=10)
        if res.status_code == 200:
            return res.json().get("result", [])
    except Exception as e:
        print(f"[getUpdates 오류] {e}")
    return []


# ================================
# 명령어 처리
# ================================
def process_command(text):
    text = text.strip()

    # 키워드 데이터 불러오기
    data     = gist_read(KEYWORDS_FILE) or {"keywords": []}
    keywords = data.get("keywords", [])

    # /list
    if text == "/list":
        if keywords:
            msg = "<b>[키워드 목록]</b>\n\n"
            for i, kw in enumerate(keywords, 1):
                msg += f"{i}. {kw}\n"
            msg += f"\n총 {len(keywords)}개"
        else:
            msg = "등록된 키워드가 없음."
        send_telegram(msg)

    # /add 키워드
    elif text.startswith("/add "):
        keyword = text[5:].strip()
        if not keyword:
            send_telegram("사용법: /add 키워드명")
        elif keyword in keywords:
            send_telegram(f"<b>'{keyword}'</b> 는 이미 등록된 키워드임.")
        else:
            keywords.append(keyword)
            data["keywords"] = keywords
            gist_write(KEYWORDS_FILE, data)
            send_telegram(f"<b>'{keyword}'</b> 추가 완료!\n현재 {len(keywords)}개 키워드 등록됨.")
            print(f"키워드 추가: {keyword}")

    # /remove 키워드
    elif text.startswith("/remove "):
        keyword = text[8:].strip()
        if not keyword:
            send_telegram("사용법: /remove 키워드명")
        elif keyword not in keywords:
            send_telegram(f"<b>'{keyword}'</b> 는 등록되지 않은 키워드임.")
        else:
            keywords.remove(keyword)
            data["keywords"] = keywords
            gist_write(KEYWORDS_FILE, data)
            send_telegram(f"<b>'{keyword}'</b> 삭제 완료!\n현재 {len(keywords)}개 키워드 등록됨.")
            print(f"키워드 삭제: {keyword}")

    # /help
    elif text == "/help":
        send_telegram(
            "<b>[사용 가능한 명령어]</b>\n\n"
            "/list — 키워드 목록 확인\n"
            "/add 키워드 — 키워드 추가\n"
            "/remove 키워드 — 키워드 삭제\n"
            "/help — 도움말"
        )

    else:
        send_telegram("알 수 없는 명령어. /help 로 확인할 것.")


# ================================
# 메인
# ================================
def main():
    print("텔레그램 명령어 처리 시작...")

    # 이전 offset 불러오기
    offset_data = gist_read(OFFSET_FILE) or {"offset": None}
    offset      = offset_data.get("offset")

    updates = get_updates(offset)
    print(f"  새 메시지 {len(updates)}건 확인")

    for update in updates:
        update_id = update.get("update_id")
        message   = update.get("message", {})
        text      = message.get("text", "")
        chat_id   = str(message.get("chat", {}).get("id", ""))

        # 본인 채팅만 처리
        if chat_id != str(TELEGRAM_CHAT_ID):
            print(f"  다른 채팅 무시: {chat_id}")
            continue

        if text.startswith("/"):
            print(f"  명령어 처리: {text}")
            process_command(text)

        # offset 업데이트
        offset = update_id + 1

    # offset 저장
    gist_write(OFFSET_FILE, {"offset": offset})
    print("완료.")


if __name__ == "__main__":
    main()
