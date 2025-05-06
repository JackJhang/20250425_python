import random

def get_random_names(filename="names.txt"):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            names = [line.strip() for line in file]
    except FileNotFoundError:
        return "找不到檔案：names.txt"
    except UnicodeDecodeError:
        return "檔案編碼錯誤，請確認檔案是 UTF-8 編碼格式。"
    except PermissionError:
        return "沒有權限讀取 names.txt，請檢查檔案權限。"
    except Exception as e:
        return f"讀取檔案時發生未預期的錯誤：{str(e)}"

    if len(names) < 3:
        return "姓名數量少於3個，請檢查 names.txt 檔案。"

    return random.sample(names, 3)

if __name__ == "__main__":
    random_names = get_random_names()
    if isinstance(random_names, str):
        print(random_names)
    else:
        print("隨機抽取的 3 個姓名：", ", ".join(random_names))