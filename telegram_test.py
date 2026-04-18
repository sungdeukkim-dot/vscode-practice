import requests

TOKEN   = "8613964576:AAHwzxro25iRAOlDTZRnTd29VPdLn-yznpc"
CHAT_ID = "49924895"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
res = requests.post(url, data={
    "chat_id":    CHAT_ID,
    "text":       "테스트 메시지입니다. 출자 공고 알림 시스템 정상 작동 중.",
    "parse_mode": "HTML",
})
print(res.json())
