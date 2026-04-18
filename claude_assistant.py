import requests
import os
import json
from datetime import datetime

TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GIST_TOKEN       = os.environ.get("GIST_TOKEN", "")
GIST_ID          = os.environ.get("GIST_ID", "")
OFFSET_FILE      = "claude_offset.json"
HISTORY_FILE     = "claude_history.json"


# ================================
# Gist 읽기 / 쓰기
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
    # 메시지 4096자 초과 시 분할 발송
    for i in range(0, len(message), 4000):
        chunk = message[i:i+4000]
        try:
            requests.post(url, data={
                "chat_id":    TELEGRAM_CHAT_ID,
                "text":       chunk,
                "parse_mode": "Markdown",
            }, timeout=10)
        except Exception as e:
            print(f"[발송 오류] {e}")


# ================================
# Claude API 호출
# ================================
def ask_claude(user_message, history):
    system_prompt = """당신은 대한민국 벤처투자기관 심사역을 위한 AI 비서입니다.

주요 역할:
- 투자 관련 질문에 대한 전문적인 분석 및 답변
- 뉴스/이슈에 대한 투자 관점 해석
- 기업 분석 및 밸류에이션 관련 조언
- 출자사업/펀드레이징 관련 인사이트
- KOSPI/KOSDAQ 시장 동향 분석
- 비상장 기업 투자 검토 관련 조언

답변 스타일:
- 간결하고 핵심적으로 (~임, ~함 음습체 사용)
- 투자 전문가 수준의 날카로운 인사이트
- 필요시 구체적인 수치와 근거 제시
- 텔레그램 특성상 너무 길지 않게 핵심만"""

    # 대화 히스토리 최근 10개만 유지
    recent_history = history[-10:] if len(history) > 10 else history
    messages = recent_history + [{"role": "user", "content": user_message}]

    try:
        res = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key":         ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type":      "application/json",
            },
            json={
                "model":      "claude-sonnet-4-20250514",
                "max_tokens": 1500,
                "system":     system_prompt,
                "messages":   messages,
            },
            timeout=30
        )
        if res.status_code == 200:
            return res.json()["content"][0]["text"]
        else:
            print(f"[Claude API 오류] {res.status_code}: {res.text}")
            return "API 오류 발생. 잠시 후 다시 시도할 것."
    except Exception as e:
        print(f"[Claude 호출 오류] {e}")
        return "오류 발생. 잠시 후 다시 시도할 것."


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
# 메인
# ================================
def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Claude 비서 실행 중...")

    # offset 불러오기
    offset_data = gist_read(OFFSET_FILE) or {"offset": None}
    offset      = offset_data.get("offset")

    # 대화 히스토리 불러오기
    history_data = gist_read(HISTORY_FILE) or {"history": []}
    history      = history_data.get("history", [])

    updates = get_updates(offset)
    print(f"  새 메시지 {len(updates)}건")

    for update in updates:
        update_id = update.get("update_id")
        message   = update.get("message", {})
        text      = message.get("text", "").strip()
        chat_id   = str(message.get("chat", {}).get("id", ""))

        # 본인 채팅만 처리
        if chat_id != str(TELEGRAM_CHAT_ID):
            continue

        # 슬래시 명령어는 telegram_commands.py 가 처리 — 여기선 스킵
        if text.startswith("/"):
            offset = update_id + 1
            continue

        if not text:
            offset = update_id + 1
            continue

        print(f"  질문: {text[:50]}...")

        # Claude에게 질문
        answer = ask_claude(text, history)
        print(f"  답변: {answer[:50]}...")

        # 대화 히스토리 업데이트
        history.append({"role": "user",      "content": text})
        history.append({"role": "assistant", "content": answer})

        # 히스토리 최근 20개만 유지
        if len(history) > 20:
            history = history[-20:]

        # 텔레그램 발송
        send_telegram(answer)

        offset = update_id + 1

    # 저장
    gist_write(OFFSET_FILE, {"offset": offset})
    gist_write(HISTORY_FILE, {"history": history})
    print("  완료.")


if __name__ == "__main__":
    main()
