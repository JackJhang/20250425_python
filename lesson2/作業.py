import random

def get_random_names(filename="names.txt"):
    # """
    # 1. 讀取 names.txt
    # 2. 將文字儲存於 list 內
    # 3. 每次執行可以亂數取出3個姓名
    # """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            names = [line.strip() for line in file]
    except FileNotFoundError:
        return "找不到檔案：names.txt"
    except Exception as e:
        return f"讀取檔案時發生錯誤：{str(e)}"

    if len(names) < 3:
        return "姓名數量少於3個，請檢查 names.txt 檔案。"

    return random.sample(names, 3)

# 執行程式並印出結果
# if __name__ == "__main__":
random_names = get_random_names()
if isinstance(random_names, str):
    print(random_names)  # 輸出錯誤訊息
else:
    print("隨機抽取的 3 個姓名：", random_names)