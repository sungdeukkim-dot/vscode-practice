# ================================
# 1. 파일 쓰기 (write)
# ================================
with open("memo.txt", "w", encoding="utf-8") as f:
    f.write("오늘 검토한 회사: SemiFive\n")
    f.write("매출 성장률: 85%\n")
    f.write("판정: 양호함\n")

print("memo.txt 저장 완료!")


# ================================
# 2. 파일 읽기 (read)
# ================================
with open("memo.txt", "r", encoding="utf-8") as f:
    content = f.read()

print("=== 파일 내용 ===")
print(content)


# ================================
# 3. 파일에 내용 추가 (append)
# ================================
with open("memo.txt", "a", encoding="utf-8") as f:
    f.write("추가 메모: 다음 주 IR 미팅 예정\n")

print("내용 추가 완료!")