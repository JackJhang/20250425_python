from flask import Flask,render_template
import os
import psycopg2
from psycopg2 import OperationalError, ProgrammingError, DatabaseError, InterfaceError, IntegrityError, Error
from dotenv import load_dotenv

from flask import Flask, render_template, request, Response, jsonify
import pandas as pd
import numpy as np
import joblib # joblib for .pkl
import json
import os
import time
import traceback
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from sklearn.metrics import mean_absolute_error

# --- 導入所有必要的API查詢工具和全局變數 ---
try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
except ImportError:
    print("❌ 錯誤：缺少 geopy 套件！請執行 pip install geopy")
    exit()

# --- 初始化 Flask 應用程式 ---
app = Flask(__name__)

# --- 全局變數 ---
MODEL_PERFORMANCE = {
    "mae": "N/A", # 預設值，以防測試數據載入失敗
    "mae_total_price_example": "N/A"
}
blended_model = None
poi_database = None      # <--- 初始化為 None
feature_defaults = None  # <--- 初始化為 None
geolocator = None

# --- 【重大修改點：創建一個 BlendedModel 類來管理融合邏輯】 ---
class BlendedModel:
    def __init__(self, config_filepath):
        print(f"--- 正在載入融合模型配置: {config_filepath} ---")
        
        if not os.path.exists(config_filepath):
            raise FileNotFoundError(f"融合模型配置文件不存在: {config_filepath}")
            
        with open(config_filepath, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.models = []
        base_dir = os.path.dirname(config_filepath)
        
        print(f"配置文件基礎目錄: {base_dir}")
        print(f"需要加載 {len(config['models'])} 個子模型")

        for i, model_info in enumerate(config['models']):
            print(f"\n--- 處理第 {i+1} 個模型: {model_info['name']} ---")
            
            # 嘗試多種路徑解析方式
            model_path_options = [
                model_info['path'],  # 原始路徑
                os.path.join(base_dir, model_info['path']),  # 相對於配置文件
                os.path.join(base_dir, os.path.basename(model_info['path'])),  # 只取文件名
            ]
            
            model_path = None
            for path_option in model_path_options:
                print(f"  嘗試路徑: {path_option}")
                if os.path.exists(path_option):
                    model_path = path_option
                    print(f"  ✅ 找到文件!")
                    break
                else:
                    print(f"  ❌ 文件不存在")
            
            if model_path is None:
                print(f"  💡 建議解決方案:")
                print(f"     1. 檢查文件是否存在於: {model_info['path']}")
                print(f"     2. 或將文件複製到: {os.path.join(base_dir, os.path.basename(model_info['path']))}")
                print(f"     3. 或修改配置文件中的路徑為相對路徑")
                raise FileNotFoundError(f"融合配置中的子模型檔案未找到: {model_info['path']}")
            
            # 加載模型
            try:
                print(f"  正在載入模型文件: {model_path}")
                model = joblib.load(model_path)
                print(f"  ✅ 模型載入成功 (類型: {type(model)})")
                
                self.models.append({
                    'name': model_info['name'],
                    'model': model,
                    'weight': model_info['weight'],
                    'path': model_path
                })
                
            except Exception as load_error:
                print(f"  ❌ 模型載入失敗: {load_error}")
                raise RuntimeError(f"無法載入模型 {model_info['name']}: {load_error}")
        
        print(f"\n✅ 所有 {len(self.models)} 個子模型載入成功！")
        for model_info in self.models:
            print(f"  - {model_info['name']}: 權重 {model_info['weight']}, 路徑 {model_info['path']}")

    def predict(self, X):
        """執行加權平均預測"""
        if not self.models:
            print("❌ 錯誤：融合模型中沒有子模型可供預測。")
            return np.zeros(len(X))
        
        final_predictions = np.zeros(len(X))
        total_weight = sum(m['weight'] for m in self.models)

        if total_weight == 0:
            print("⚠️ 警告：模型權重總和為0，將採用簡單平均法。")
            for m_info in self.models:
                final_predictions += m_info['model'].predict(X)
            return final_predictions / len(self.models)
        
        for m_info in self.models:
            model_pred = m_info['model'].predict(X)
            final_predictions += model_pred * m_info['weight']
        
        return final_predictions / total_weight

    def get_expected_features(self):
        """獲取模型期望的輸入特徵列表"""
        if not self.models:
            raise AttributeError("無法從融合模型獲取期望特徵：沒有加載任何子模型")
            
        first_model = self.models[0]['model']
        
        if hasattr(first_model, 'named_steps') and 'preprocessor' in first_model.named_steps:
            preprocessor = first_model.named_steps['preprocessor']
            if hasattr(preprocessor, 'feature_names_in_'):
                return preprocessor.feature_names_in_
            elif hasattr(preprocessor, 'transformers_') and preprocessor.transformers_:
                # 處理 ColumnTransformer
                all_features = []
                for name, trans, columns in preprocessor.transformers_:
                    if isinstance(columns, str):
                        all_features.append(columns)
                    else:
                        all_features.extend(list(columns))
                return np.array(list(dict.fromkeys(all_features)))
        
        # 如果是簡單的模型，嘗試其他屬性
        if hasattr(first_model, 'feature_names_in_'):
            return first_model.feature_names_in_
        
        raise AttributeError("無法從融合模型中獲取期望的特徵列表")


# --- 在應用程式啟動時，一次性載入所有必要的靜態資源 ---
# --- 在應用程式啟動時，一次性載入所有必要的靜態資源 ---
try:
    MODEL_CONFIG_PATH = os.path.join('models', 'FINAL_blended_config.json')
    POI_DB_PATH = os.path.join('models', 'poi_database.pkl')
    DEFAULTS_PATH = os.path.join('models', 'feature_defaults.json')
    TEST_DATA_PATH = os.path.join('data', 'FINAL_TEST_2024-2025.parquet')

    print("=== 開始加載靜態資源 ===")
    
    # 【步驟1】檢查文件存在性
    required_files = {
        'MODEL_CONFIG': MODEL_CONFIG_PATH,
        'POI_DB': POI_DB_PATH,
        'DEFAULTS': DEFAULTS_PATH,
        'TEST_DATA': TEST_DATA_PATH
    }
    
    for name, path in required_files.items():
        if os.path.exists(path):
            print(f"✅ {name}: {path}")
        else:
            print(f"❌ {name}: {path} - 文件不存在！")
    
    # 【步驟2】加載 POI 數據庫
    print("正在載入 POI 資料庫...")
    if os.path.exists(POI_DB_PATH):
        poi_database = joblib.load(POI_DB_PATH)
        print(f"✅ POI 資料庫載入成功 (類型: {type(poi_database)})")
    else:
        raise FileNotFoundError(f"POI 資料庫檔案未找到: {POI_DB_PATH}")

    # 【步驟3】加載特徵默認值
    print("正在載入特徵預設值...")
    if os.path.exists(DEFAULTS_PATH):
        with open(DEFAULTS_PATH, 'r', encoding='utf-8') as f:
            feature_defaults = json.load(f)
        print(f"✅ 特徵預設值載入成功 (特徵數: {len(feature_defaults)})")
    else:
        raise FileNotFoundError(f"特徵預設值檔案未找到: {DEFAULTS_PATH}")
    
    # 【步驟4】加載融合模型
    print("正在載入融合模型...")
    blended_model = BlendedModel(MODEL_CONFIG_PATH)
    print("✅ 融合模型載入成功")

    # 【步驟5】評估模型性能
    print("正在評估模型性能...")
    if os.path.exists(TEST_DATA_PATH):
        try:
            df_test = pd.read_parquet(TEST_DATA_PATH)
            target_col = '建物單價_元坪'
            
            expected_features = blended_model.get_expected_features()
            X_test = df_test[expected_features].copy()
            y_test_true = df_test[target_col]
            
            y_test_pred = blended_model.predict(X_test)
            mae_value = mean_absolute_error(y_test_true, y_test_pred)
            
            # 更新性能指標
            MODEL_PERFORMANCE['mae'] = f"{mae_value:,.2f}"
            MODEL_PERFORMANCE['mae_total_price_example'] = f"{(mae_value * 30):,.0f}"
            
            print(f"✅ 模型性能評估完成: MAE = {mae_value:.2f}")
            print(f"   -> 更新後的 MODEL_PERFORMANCE: {MODEL_PERFORMANCE}")
            
        except Exception as perf_error:
            print(f"⚠️ 模型性能評估失敗: {perf_error}")
            print("   -> MODEL_PERFORMANCE 將保持默認值")
            # 不拋出異常，讓應用繼續運行
    else:
        print(f"⚠️ 警告: 找不到測試集檔案 {TEST_DATA_PATH}，無法計算模型性能指標。")
        print("   -> MODEL_PERFORMANCE 將保持默認值")

    # 【步驟6】初始化地理編碼器
    print("正在初始化地理編碼器...")
    geolocator = Nominatim(user_agent=f"RealEstateWebApp/{int(time.time())}")
    print("✅ 地理編碼器初始化成功")
    
    print("=== 所有資源加載完成 ===")
    print(f"最終 MODEL_PERFORMANCE: {MODEL_PERFORMANCE}")

except Exception as e:
    print(f"❌ 啟動錯誤：載入模型或數據時發生問題！")
    print(f"錯誤類型: {type(e).__name__}")
    print(f"錯誤訊息: {str(e)}")
    print("完整錯誤追蹤:")
    print(traceback.format_exc())
    
    # 設置錯誤狀態
    blended_model = None
    poi_database = None
    feature_defaults = None
    geolocator = None
    
    # 更新 MODEL_PERFORMANCE 以反映錯誤狀態
    MODEL_PERFORMANCE['mae'] = "加載失敗"
    MODEL_PERFORMANCE['mae_total_price_example'] = "無法計算"
    
    print(f"錯誤狀態下的 MODEL_PERFORMANCE: {MODEL_PERFORMANCE}")
    print("應用程式將以受限模式運行（無法提供預測服務）")


# --- 後端魔法：核心輔助函式 ---

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    a = np.sin(delta_phi / 2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0)**2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

def calculate_geo_features(lat, lon, current_poi_db): # 參數名改為 current_poi_db 以避免與全局變數混淆
    """根據經緯度和POI資料庫，即時計算所有地理空間特徵"""
    geo_features = {}
    
    if not current_poi_db: # 檢查 poi_database 是否已成功載入
        print("❌ 錯誤: POI 資料庫未載入，無法計算地理特徵。")
        return geo_features # 返回空的地理特徵

    if 'final_locs' in current_poi_db:
        for name, poi_coord in current_poi_db['final_locs'].items():
            feature_name = f'距離_{name}'
            geo_features[feature_name] = haversine_distance(lat, lon, poi_coord[0], poi_coord[1])
    
    if 'loc_density' in current_poi_db:
        for name, coords_list in current_poi_db['loc_density'].items():
            feature_name = f'{name.replace(" ","_")}數量_300m'
            if not coords_list:
                geo_features[feature_name] = 0
                continue
            # 確保 coords_list 中的座標是 (lat, lon) 對
            if coords_list and isinstance(coords_list[0], (list, tuple)) and len(coords_list[0]) == 2:
                distances = [haversine_distance(lat, lon, p_lat, p_lon) for p_lat, p_lon in coords_list]
                geo_features[feature_name] = int(np.sum(np.array(distances) <= 300))
            else:
                print(f"⚠️ 警告: POI密度數據 '{name}' 格式不正確，跳過計算。應為座標列表。")
                geo_features[feature_name] = 0
            
    all_cats = ['捷運', '橋樑', '學區', '文教', '運動', '市場', '主要幹道', '未來捷運', '警察局', '公園', '購物', '行政', '嫌惡_宮廟']
    for cat in all_cats:
        cat_distances = [v for k, v in geo_features.items() if k.startswith(f'距離_{cat}_')]
        if cat_distances:
            geo_features[f'距離_最近{cat}'] = min(cat_distances)
        else:
            # 確保 feature_defaults 已成功載入
            default_val = 99999 # 硬編碼的最終備用值
            if feature_defaults and f'距離_最近{cat}' in feature_defaults:
                 default_val = feature_defaults[f'距離_最近{cat}']
            else:
                print(f"⚠️ 警告: 特徵 '距離_最近{cat}' 在 feature_defaults 中未找到，使用硬編碼預設值 {default_val}。")
            geo_features[f'距離_最近{cat}'] = default_val


    return geo_features

def build_feature_vector(user_input, geo_features, current_defaults, expected_features_list):
    """構建最終用於預測的、完整的特徵向量 (v2 - 增強版)"""
    print("--- 開始構建特徵向量 ---")
    if not current_defaults: # 檢查 feature_defaults 是否已成功載入
        print("❌ 錯誤: 特徵預設值未載入，無法構建特徵向量。")
        # 即使預設值未載入，我們仍然嘗試創建一個空的 DataFrame
        # 但這很可能會導致後續的錯誤
        return pd.DataFrame(columns=expected_features_list)

    vector = current_defaults.copy()
    
    for key, value in user_input.items():
        if value not in [None, ""] and key in vector:
            try:
                vector[key] = float(value)
            except (ValueError, TypeError):
                vector[key] = value # 保持原樣 (例如文字型特徵)
    
    vector.update(geo_features)
    
    # 創建一個Series，其索引與 expected_features_list 匹配，並用 vector 中的值填充
    # 這樣可以確保順序和欄位名稱都正確
    # 對於 vector 中沒有，但 expected_features_list 中有的特徵，會是 NaN
    # 對於 vector 中有，但 expected_features_list 中沒有的特徵，會被忽略
    # （後者不應該發生，如果 expected_features_list 是全面的）
    
    # 先從 vector 創建一個 Series
    temp_series = pd.Series(vector)
    # 根據 expected_features_list 重新索引，缺失的用 NaN 填充
    # 這裡的 reindex 很重要，它確保了欄位的順序和模型期望的一致
    final_series = temp_series.reindex(expected_features_list)


    # 將 Series 轉換為 DataFrame (單行)
    final_df = pd.DataFrame([final_series])


    # --- 計算交叉特徵 ---
    # 確保這些基礎特徵存在於 final_df 中，如果不存在，使用預設值或0
    # 注意：現在 final_df 的欄位順序已經由 expected_features_list 決定
    # 我們需要確保用於計算交叉特徵的基礎欄位在 final_df 中存在
    
    # 示例交叉特徵：最終_屋齡_X_樓層比
    # 確保 '最終_屋齡' 和 '樓層比' 在 current_defaults 中有合理的預設值
    屋齡 = final_df.loc[0, '最終_屋齡'] if '最終_屋齡' in final_df.columns else current_defaults.get('最終_屋齡', 0)
    樓層比 = final_df.loc[0, '樓層比'] if '樓層比' in final_df.columns else current_defaults.get('樓層比', 0)
    
    # 如果交叉特徵欄位本身在模型期望的特徵列表中
    if '最終_屋齡_X_樓層比' in final_df.columns:
        final_df.loc[0, '最終_屋齡_X_樓層比'] = 屋齡 * 樓層比
    # ... (添加所有其他交叉特徵的計算邏輯) ...
    # 示例:
    # if '主建物坪數_X_樓層比' in final_df.columns:
    #     主建物坪數 = final_df.loc[0, '主建物坪數'] if '主建物坪數' in final_df.columns else current_defaults.get('主建物坪數',0)
    #     final_df.loc[0, '主建物坪數_X_樓層比'] = 主建物坪數 * 樓層比

    # 【重要】再次使用 current_defaults 對 NaN 值進行填充，以處理 reindex 可能產生的 NaN
    # 或者處理交叉特徵計算中，因基礎特徵缺失而導致的 NaN
    # 只填充 final_df 中實際存在的欄位
    for col in final_df.columns:
        if final_df[col].isnull().any():
            if col in current_defaults:
                final_df[col].fillna(current_defaults[col], inplace=True)
            else:
                # 如果某個期望的欄位在 defaults 中也沒有，這是一個潛在問題
                # 這裡可以選擇填充一個通用值 (如0) 或發出警告
                print(f"⚠️ 警告: 欄位 '{col}' 在 defaults 中沒有預設值，NaN 值可能未被處理。")
                final_df[col].fillna(0, inplace=True) # 備用填充

    print(f"--- 特徵向量構建完成 (欄位數: {len(final_df.columns)}) ---")
    return final_df



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

if __name__ == '__main__':
    # 建議在開發時啟用 Flask logger
    import logging
    logging.basicConfig(level=logging.DEBUG) # 可以看到 app.logger.debug/info 等訊息
    app.run(debug=True, threaded=True)
