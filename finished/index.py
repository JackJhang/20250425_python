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
    # 詳細的調試信息
    print("="*50)
    print("DEBUG: 進入 index 路由")
    print(f"DEBUG: MODEL_PERFORMANCE = {MODEL_PERFORMANCE}")
    print(f"DEBUG: blended_model 是否已加載: {blended_model is not None}")
    print(f"DEBUG: poi_database 是否已加載: {poi_database is not None}")
    print(f"DEBUG: feature_defaults 是否已加載: {feature_defaults is not None}")
    print("="*50)
    
    # 構建傳遞給模板的數據
    template_data = {
        'performance': MODEL_PERFORMANCE,
        'model_loaded': blended_model is not None,
        'debug_info': {
            'mae_value': MODEL_PERFORMANCE['mae'],
            'total_price_example': MODEL_PERFORMANCE['mae_total_price_example']
        }
    }
    
    return render_template('index.html', **template_data)

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


@app.route('/predict', methods=['POST'])
def predict_route(): # 路由函式名稱保持 predict_route
    # 執行嚴格的初始檢查
    if not blended_model:
        app.logger.error("Predict attempt failed: Blended model not loaded.")
        return jsonify({'error': '模型未能成功載入或初始化失敗，無法提供預測服務。'}), 500
    if not poi_database: # 檢查 poi_database 是否為 None 或空
        app.logger.error("Predict attempt failed: POI database not loaded or empty.")
        return jsonify({'error': 'POI資料庫未能成功載入或為空，無法提供預測服務。'}), 500
    if not feature_defaults:
        app.logger.error("Predict attempt failed: Feature defaults not loaded.")
        return jsonify({'error': '特徵預設值未能成功載入，無法提供預測服務。'}), 500
    if not geolocator:
        app.logger.error("Predict attempt failed: Geolocator not initialized.")
        return jsonify({'error': '地理編碼器未能成功初始化，無法提供預測服務。'}), 500

    # 【關鍵修改】: 在 predict_route 的作用域內捕獲 poi_database 的當前參考
    # 這樣 generate_progress 透過閉包訪問的是這個穩定的參考
    stable_poi_database_ref = poi_database
    stable_feature_defaults_ref = feature_defaults # 同樣為 feature_defaults 做此處理

    data = request.get_json()
    address = data.get('address')
    user_features = data.get('features', {})

    if not address:
        return jsonify({'error': '地址為必填項目！'}), 400

    def generate_progress():
        """一個生成器函式，分步執行任務並用yield返回進度"""
        try:
                    # 【【【新增除錯打印】】】
            app.logger.debug(f"Inside generate_progress: type of stable_poi_database_ref: {type(stable_poi_database_ref)}")
            app.logger.debug(f"Inside generate_progress: stable_poi_database_ref is None: {stable_poi_database_ref is None}")
            if stable_poi_database_ref:
                app.logger.debug(f"Inside generate_progress: keys in stable_poi_database_ref (first 5): {list(stable_poi_database_ref.keys())[:5] if isinstance(stable_poi_database_ref, dict) else 'Not a dict'}")
            # 階段一：地理編碼
            yield f"data: {json.dumps({'status': '正在定位地址...', 'progress': 20})}\n\n"
            location = geolocator.geocode(address, timeout=10, country_codes='TW')
            if not location:
                raise ValueError(f"無法定位地址「{address}」。請嘗試輸入更詳細的地址，例如包含「新北市永和區」。")
            lat, lon = location.latitude, location.longitude
            
            # 階段二：生成地理特徵
            yield f"data: {json.dumps({'status': '正在計算周邊環境特徵...', 'progress': 40})}\n\n"
            # 【關鍵修改】: 使用從外部作用域捕獲的穩定參考
            geo_features_calculated = calculate_geo_features(lat, lon, stable_poi_database_ref)

            # 階段三：構建完整特徵向量
            yield f"data: {json.dumps({'status': '正在準備數據並請求模型...', 'progress': 60})}\n\n"
            
            expected_features_list = blended_model.get_expected_features()
            if not isinstance(expected_features_list, (list, np.ndarray)):
                raise TypeError("get_expected_features() 返回的不是有效的列表或陣列。")
            
            app.logger.debug(f"Model expected features ({len(expected_features_list)}): {sorted(list(expected_features_list))}")
            
            # 【關鍵修改】: 使用從外部作用域捕獲的穩定參考
            input_df = build_feature_vector(user_features, geo_features_calculated, stable_feature_defaults_ref, expected_features_list)

            app.logger.debug(f"Generated features for model ({len(input_df.columns)}): {sorted(list(input_df.columns))}")
            
            set_expected = set(expected_features_list)
            set_generated = set(input_df.columns)

            if set_expected != set_generated:
                missing_in_generated = sorted(list(set_expected - set_generated))
                extra_in_generated = sorted(list(set_generated - set_expected))
                error_msg_parts = ["後端特徵生成與模型期望不符！"]
                if missing_in_generated: error_msg_parts.append(f"模型期望但未生成的特徵 ({len(missing_in_generated)}個): {str(missing_in_generated[:5])}...")
                if extra_in_generated: error_msg_parts.append(f"生成了但模型不期望的特徵 ({len(extra_in_generated)}個): {str(extra_in_generated[:5])}...")
                if input_df.isnull().values.any():
                    nan_cols = input_df.columns[input_df.isnull().any()].tolist()
                    error_msg_parts.append(f"輸入數據中包含NaN值，在欄位: {nan_cols}")
                app.logger.error("\n".join(error_msg_parts))
                raise ValueError("\n".join(error_msg_parts))
            elif input_df.isnull().values.any():
                nan_cols = input_df.columns[input_df.isnull().any()].tolist()
                app.logger.error(f"Input data contains NaN values in columns: {nan_cols}")
                raise ValueError(f"輸入數據中包含NaN值，即使特徵集匹配。在欄位: {nan_cols}")
            else:
                app.logger.debug("Feature sets match and no NaN values.")

            yield f"data: {json.dumps({'status': '模型預測中...', 'progress': 80})}\n\n"
            prediction_per_ping = blended_model.predict(input_df[list(expected_features_list)])[0] # 確保順序
            
            total_price_prediction = "N/A"
            user_ping_str = user_features.get('建物總坪數')
            if user_ping_str and str(user_ping_str).strip():
                try:
                    user_ping = float(user_ping_str)
                    if user_ping > 0:
                        total_price = prediction_per_ping * user_ping
                        total_price_prediction = f"{total_price:,.1f} 萬元"
                except (ValueError, TypeError):
                    app.logger.warning(f"無法將建物總坪數 '{user_ping_str}' 轉換為數字。")
                    pass

            result = {
                "status": "預測完成！", 
                "progress": 100, 
                "prediction": f"{prediction_per_ping:,.2f} 萬元/坪",
                "total_price": total_price_prediction
            }
            yield f'data: {json.dumps(result)}\n\n'

        except (GeocoderTimedOut, GeocoderServiceError) as geo_e:
            app.logger.error(f"Geocoding error: {geo_e}", exc_info=True)
            error_result = {"error": f"地理編碼服務失敗：{geo_e}. 請稍後再試或檢查地址。"}
            yield f'data: {json.dumps(error_result)}\n\n'
        except ValueError as ve:
            app.logger.error(f"Data processing or validation error: {ve}", exc_info=True)
            error_result = {"error": f"數據處理失敗：{str(ve)}"} # 確保 ve 可以序列化
            yield f'data: {json.dumps(error_result)}\n\n'
        except Exception as e:
            app.logger.error(f"Unexpected error in prediction stream: {e}", exc_info=True)
            error_result = {"error": f"預測失敗：發生未預期的錯誤 ({type(e).__name__})，請檢查伺服器日誌。"}
            yield f'data: {json.dumps(error_result)}\n\n'

    return Response(generate_progress(), mimetype='text/event-stream')