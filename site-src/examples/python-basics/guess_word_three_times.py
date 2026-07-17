answer = "python"
attempt = 1
guessed = False

while attempt <= 3:
    guess = input(f"第 {attempt} 次：")
    if guess == answer:
        print("答对了")
        guessed = True
        break
    print("不对，再想想")
    attempt = attempt + 1

if not guessed:
    print("次数用完")
