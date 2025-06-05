from flask import Flask,render_template
import os
import psycopg2
from psycopg2 import OperationalError, ProgrammingError, DatabaseError, InterfaceError, IntegrityError, Error
from dotenv import load_dotenv
import datetime

load_dotenv()  # 讀取 .env 檔案中的環境變數
conn_string = os.getenv('RENDER_DATABASE')

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html.jinja2")

@app.route("/index")
def index2():
    return render_template("index.html")

@app.route("/classes")
def classes():
    title = "Tom"
    items = ["蘋果", "香蕉", "橘子"]
    days_of_week = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期天"]
    return render_template("classes.html.jinja2", title=title, items=items, days=days_of_week)

@app.route("/news")
def news():
    rows = []
    colnames = []
    accordion_data = []

    try:
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                # 假設您的表格中包含 '主題', '上版日期', '內容' 欄位
                cur.execute("SELECT 編號, 主題, 上版日期, 內容 FROM 最新訊息 ORDER BY 上版日期 DESC;")
                rows = cur.fetchall()
                colnames = [desc[0] for desc in cur.description]

                # 找到對應欄位的索引
                title_idx = -1
                date_idx = -1
                content_idx = -1

                try:
                    title_idx = colnames.index('主題')
                    date_idx = colnames.index('上版日期')
                    content_idx = colnames.index('內容')
                except ValueError as e:
                    print(f"🚨 資料庫欄位名稱錯誤：{e}")
                    return render_template("error.html.jinja2", error_message=f"🚨 資料庫欄位名稱錯誤：未找到所需的 '主題'、'上版日期' 或 '內容' 欄位。詳細訊息：{e}"), 500

                # 將查詢結果轉換為手風琴所需的字典列表格式
                for row in rows:
                    # 正確使用 datetime.date 和 datetime.datetime
                    formatted_date = row[date_idx].strftime('%Y-%m-%d') \
                                   if isinstance(row[date_idx], (datetime.date, datetime.datetime)) \
                                   else str(row[date_idx])

                    accordion_data.append({
                        'title': row[title_idx],
                        'date': formatted_date,
                        'content': row[content_idx]
                    })

    except OperationalError as e:
        print(f"🚨 連線失敗：伺服器未啟動、網路問題或參數錯誤 | 詳細訊息：{e}")
        return render_template("error.html.jinja2", error_message=f"🚨 連線失敗：伺服器未啟動、網路問題或參數錯誤 | 詳細訊息：{e}"), 500
    except InterfaceError as e:
        print(f"🚨 連線中斷：連線被意外關閉 | 詳細訊息：{e}")
        return render_template("error.html.jinja2", error_message=f"🚨 連線中斷：連線被意外關閉 | 詳細訊息：{e}"), 500
    except Error as e:
        print(f"🚨 資料庫錯誤：{e}")
        return render_template("error.html.jinja2", error_message=f"🚨 資料庫錯誤：{e}"), 500
    except Exception as e: # 捕獲其他所有異常，包括您遇到的類型錯誤
        print(f"🚨 其他錯誤：{e}")
        return render_template("error.html.jinja2", error_message=f"🚨 其他錯誤：{e}"), 500

    return render_template("news_ver3.html.jinja2", rows=rows, colnames=colnames, accordion_data=accordion_data)




@app.route("/traffic")
def traffic():
    return render_template("traffic.html.jinja2")

@app.route("/contact")
def contact():
    return render_template("contact.html.jinja2")

@app.route("/test")
def test():
    return render_template("testindex.html.jinja2")
