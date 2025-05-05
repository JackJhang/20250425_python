import random

# 1. 讀取 names.txt 檔案
with open("names.txt", "r", encoding="utf-8") as file:
    names = [line.strip() for line in file if line.strip()]  # 2. 將文字儲存於 list 內，排除空行

# 檢查名單是否足夠
if len(names) < 3:
    print("名單少於3人，請確認 names.txt 內容。")
else:
    # 3. 亂數選出3個姓名
    selected_names = random.sample(names, 3)
    print("隨機選出的姓名：", selected_names)
