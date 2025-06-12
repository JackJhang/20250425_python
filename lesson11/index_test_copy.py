from flask import Flask,render_template
import os
import psycopg2
from psycopg2 import OperationalError, ProgrammingError, DatabaseError, InterfaceError, IntegrityError, Error
from dotenv import load_dotenv

load_dotenv()  # 讀取 .env 檔案中的環境變數
conn_string = os.getenv('RENDER_DATABASE')

app = Flask(__name__)

@app.route("/")
def index():
    # 從資料庫獲取數據
    data_from_db = get_accordion_data_from_db()
    # 將數據傳遞給 Jinja2 模板
    return render_template("index.html.jinja2", accordion_data=data_from_db)

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
    try:
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM 最新訊息 ORDER BY 編號 ASC;")
                rows = cur.fetchall()
                colnames = [desc[0] for desc in cur.description]  # 取得欄位名稱

    except OperationalError as e:
        print(f"🚨 連線失敗：伺服器未啟動、網路問題或參數錯誤 | 詳細訊息：{e}")
        return render_template("error.html.jinja2",error_message=f"🚨 連線失敗：伺服器未啟動、網路問題或參數錯誤 | 詳細訊息：{e}"), 500
    except InterfaceError as e:
        print(f"🚨 連線中斷：連線被意外關閉 | 詳細訊息：{e}")
        return render_template("error.html.jinja2",error_message=f"🚨 連線中斷：連線被意外關閉 | 詳細訊息：{e}"), 500
    except Error as e:
        print(f"🚨 資料庫錯誤：{e}")
        return render_template("error.html.jinja2",error_message=f"🚨 資料庫錯誤：{e}"), 500
    except Exception as e:
        print(f"🚨 其他錯誤：{e}")
        return render_template("error.html.jinja2",error_message=f"🚨 其他錯誤：{e}"), 500

    return render_template("news_ver3.html.jinja2", rows=rows, colnames=colnames)

def get_accordion_data_from_db():
    conn = None
    try:
        conn = psycopg2.connect('_python_course_database.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE public.最新訊息 (
	            編號 smallserial NOT NULL,
	            主題 text NOT NULL,
	            上版日期 date NULL,
	            內容 text NULL,
	            CONSTRAINT newtable_pk PRIMARY KEY ("編號")
            )
        ''')
       
        conn.commit()

        cursor.execute("SELECT 主題, 上版日期, 內容 FROM public.最新訊息 ORDER BY 上版日期 DESC")
        rows = cursor.fetchall()

        # 將資料轉換為 Jinja2 模板所需的字典列表格式
        python_course_database = []
        for row in rows:
            python_course_database.append({
                '主題': row[1],
                '上版日期': row[2],
                '內容': row[3]
            })
        return python_course_database
    except psycopg2.Error as e:
        print(f"資料庫錯誤: {e}")
        return []
    finally:
        if conn:
            conn.close()





@app.route("/traffic")
def traffic():
    return render_template("traffic.html.jinja2")

@app.route("/contact")
def contact():
    return render_template("contact.html.jinja2")

@app.route("/test")
def test():
    return render_template("testindex.html.jinja2")
