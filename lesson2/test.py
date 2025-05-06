import random

with open('names.txt', 'r', encoding='utf-8') as f:
    names = [line.strip() for line in f]

sample = random.sample(names, 3)
print("隨機抽取的 3 個姓名：", (sample))
