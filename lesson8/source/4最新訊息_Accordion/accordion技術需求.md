# Accordion 手風琴組件技術需求規格

## 功能需求

### 1. 基本功能
- 實現手風琴折疊/展開功能
- 預設第一筆資料為展開狀態
- 點擊標題區域可切換展開/收合狀態
- 同時只能有一個項目處於展開狀態

### 2. 資料顯示需求
- **標題顯示**: 支援多行標題文字，自動換行處理
- **日期顯示**: 格式為 "日期：YYYY-MM-DD"
- **內容顯示**: 固定高度顯示，超出部分隱藏或滾動

### 3. 佈局需求
- 標題區域採用兩欄式佈局：
  - 左欄：標題文字（支援多行）
  - 右欄：展開/收合圖示
- 響應式設計，確保在不同視窗大小下維持兩欄佈局
- 內容區域固定高度，避免過度撐開版面

## 技術實現

### HTML 結構
- 使用語義化 HTML 標籤
- 便於 Jinja 模板引擎進行資料迭代
- 清晰的 class 命名規範

### CSS 樣式
- 使用 Flexbox 或 Grid 實現兩欄佈局
- 響應式設計確保跨設備兼容
- 平滑的展開/收合動畫效果
- 固定內容區域高度

### JavaScript 功能
- 展開/收合切換邏輯
- 確保同時只有一個項目展開
- 平滑的動畫過渡效果

## 資料來源
- 所有資料從資料庫動態取得
- 支援 Jinja 模板變數綁定
- 標題、日期、內容均為動態資料

## 部署需求
- 生成完整的測試頁面
- 可獨立運行的 HTML 檔案
- 未來可整合至容器化環境
- 便於手動套用 Jinja 模板

## 瀏覽器兼容性
- 支援現代瀏覽器（Chrome、Firefox、Safari、Edge）
- 確保在行動裝置上正常顯示
- 提供適當的降級方案