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
    return render_template("index.html")

@app.route("/index")
def index2():
    return render_template("index.html.jinja2")


@app.route("/classes", defaults={'course_type': '一般課程'})
@app.route("/classes/<course_type>")
def classes(course_type):
    print(f"目前顯示的課程類別是: {course_type}")

    # all_course_categories 用於導覽列或篩選器 (例如顯示所有課程類別的列表)
    all_course_categories = []
    # courses_for_cards 用於卡片顯示，會是字典列表
    courses_for_cards = []

    try:
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                # 步驟 1: 查詢所有獨特的課程類別 (如果你的頁面有類別篩選功能，這會很有用)
                sql_get_categories = """
                SELECT DISTINCT "課程類別" FROM "進修課程";
                """
                cur.execute(sql_get_categories)
                raw_categories = cur.fetchall()
                all_course_categories = [cat[0] for cat in raw_categories]
                all_course_categories.reverse() # 如果你需要反向排序

                # 步驟 2: 根據選定的 course_type 查詢詳細的課程資料
                sql_get_courses = """
                SELECT
                    "課程名稱",
                    "老師",
                    "進修人數",
                    "報名開始日期",
                    "報名結束日期",
                    "課程內容",
                    "進修費用"
                FROM
                    "進修課程"
                WHERE
                    "課程類別" = %s -- 使用參數化查詢，防止 SQL 注入
                ORDER BY "報名開始日期" DESC -- 可以加上排序，例如按日期降序
                LIMIT 6; -- 限制顯示的卡片數量，這裡限制為 6 張
                """
                # 注意：傳遞給 execute 的參數必須是元組 (即使只有一個參數)
                cur.execute(sql_get_courses, (course_type,))
                raw_course_rows = cur.fetchall()

                # 取得查詢結果的欄位名稱，用於將元組轉換為字典
                column_names = [desc[0] for desc in cur.description]

                # 將每一行課程資料 (元組) 轉換為字典
                for row in raw_course_rows:
                    course_dict = {}
                    for i, col_name in enumerate(column_names):
                        # 將資料庫欄位名稱映射到 Jinja 模板中使用的鍵名
                        if col_name == "課程名稱":
                            course_dict['title'] = row[i]
                        elif col_name == "課程內容":
                            course_dict['body'] = row[i]
                        elif col_name == "老師":
                            course_dict['teacher'] = row[i]
                        elif col_name == "進修費用":
                            course_dict['price'] = row[i]
                        # 可以根據你的需求，繼續映射其他欄位
                        # 比如日期可以格式化，人數可能需要轉換等等
                        # 例如:
                        # elif col_name == "報名開始日期":
                        #     course_dict['start_date'] = row[i].strftime('%Y-%m-%d') if row[i] else None
                        else:
                            course_dict[col_name] = row[i] # 其他欄位如果不需要特別映射，就保持原名

                    courses_for_cards.append(course_dict)

                print("從資料庫獲取的課程類別 (all_course_categories):", all_course_categories)
                print("從資料庫獲取的課程資料 (courses_for_cards):", courses_for_cards)

    except OperationalError as e:
        print(f"🚨 連線失敗：伺服器未啟動、網路問題或參數錯誤 | 詳細訊息：{e}")
        return render_template("error.html.jinja2", error_message=f"🚨 連線失敗：伺服器未啟動、網路問題或參數錯誤 | 詳細訊息：{e}"), 500
    except InterfaceError as e:
        print(f"🚨 連線中斷：連線被意外關閉 | 詳細訊息：{e}")
        return render_template("error.html.jinja2", error_message=f"🚨 連線中斷：連線被意外關閉 | 詳細訊息：{e}"), 500
    except Error as e:
        print(f"🚨 資料庫錯誤：{e}")
        return render_template("error.html.jinja2", error_message=f"🚨 資料庫錯誤：{e}"), 500
    except Exception as e:
        print(f"🚨 其他錯誤：{e}")
        return render_template("error.html.jinja2", error_message=f"🚨 其他錯誤：{e}"), 500

    # 將處理好的資料傳遞給 Jinja 模板
    return render_template(
        "classes.html.jinja2",
        kinds=all_course_categories,    # 所有課程類別 (用於導覽列/篩選器)
        course_data=courses_for_cards,  # 實際要顯示的課程卡片資料
        course_type=course_type         # 當前選中的課程類別，用於在導覽列中高亮顯示
    )


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

    return render_template("news.html.jinja2", rows=rows, colnames=colnames)


@app.route("/traffic")
def traffic():
    return render_template("traffic.html.jinja2")

@app.route("/contact")
def contact():
    return render_template("contact.html.jinja2")

@app.route("/test")
def test():
    return render_template("testindex.html.jinja2")
