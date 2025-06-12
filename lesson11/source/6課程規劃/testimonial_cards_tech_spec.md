# 卡片組件技術需求文件

## 專案概述
根據 Figma 設計稿開發一組水平排列的卡片組件，此組件將作為網頁的局部元素使用，需支援響應式設計(RWD)。

## 設計規格分析

### 整體佈局
- **容器寬度**: 1072px (桌面版)
- **卡片排列**: 橫向排列，支援換行
- **卡片間距**: 64px
- **卡片數量**: 6張卡片
- **卡片寬度**: 約 301.33px (桌面版)

### 單一卡片規格
- **佈局方向**: 水平排列 (Icon + 內容)
- **內部間距**: 24px (圖示與內容間)
- **內容區間距**: 
  - 標題與內文間距: 8px
  - 文字區塊下方間距: 16px

### 視覺元素

#### 圖示 (Icon)
- **尺寸**: 32x32px
- **樣式**: SVG 圖示
- **顏色**: #1E1E1E (黑色)
- **邊框**: 3px 實線
- **背景**: #FFFFFF (白色)

#### 文字內容
**標題 (Title)**
- **字體**: Inter
- **字重**: 600 (Semi-bold)
- **大小**: 24px
- **行高**: 1.2em
- **字距**: -2%
- **顏色**: #1E1E1E (黑色)
- **對齊**: 左對齊

**內文 (Body)**
- **字體**: Inter
- **字重**: 400 (Regular)
- **大小**: 16px
- **行高**: 1.4em
- **顏色**: #757575 (灰色)
- **對齊**: 左對齊
- **內容**: "Body text for whatever you'd like to say. Add main takeaway points, quotes, anecdotes, or even a very very short story."

## 技術實作需求

### HTML 結構
```html
<div class="cards-container">
  <div class="card">
    <div class="card-icon">
      <!-- SVG Icon -->
    </div>
    <div class="card-content">
      <h3 class="card-title">Title</h3>
      <p class="card-body">Body text content...</p>
    </div>
  </div>
  <!-- 重複 6 次 -->
</div>
```

### CSS 規格

#### 響應式斷點
- **桌面版** (≥1200px): 3列排列，卡片寬度 301.33px
- **平板版** (768px-1199px): 2列排列，卡片寬度自適應
- **手機版** (<768px): 1列排列，卡片寬度 100%

#### 容器樣式
```css
.cards-container {
  display: flex;
  flex-wrap: wrap;
  gap: 64px;
  max-width: 1072px;
  /* 響應式調整 */
}
```

#### 單一卡片樣式
```css
.card {
  display: flex;
  gap: 24px;
  flex: 0 1 301.33px; /* 桌面版寬度 */
  /* 響應式調整 */
}
```

### 響應式設計要求

#### 桌面版 (≥1200px)
- 容器寬度: 1072px
- 卡片寬度: 301.33px
- 每行 3 張卡片
- 卡片間距: 64px

#### 平板版 (768px-1199px)
- 容器寬度: 100%，最大 800px
- 卡片寬度: calc(50% - 32px)
- 每行 2 張卡片
- 卡片間距: 64px → 32px

#### 手機版 (<768px)
- 容器寬度: 100%
- 卡片寬度: 100%
- 每行 1 張卡片
- 卡片間距: 64px → 24px
- 卡片內部間距: 24px → 16px

### 圖示處理
- 使用 SVG 格式確保清晰度
- 支援圖示替換功能
- 預設提供 Info 圖示
- 圖示需支援深色/淺色主題切換

### 無障礙設計 (Accessibility)
- 圖示需提供 alt 文字或 aria-label
- 標題使用適當的語義標籤 (h3)
- 確保鍵盤導航支援
- 色彩對比度符合 WCAG 2.1 AA 標準

### 瀏覽器支援
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+
- 移動端瀏覽器支援

### 效能考量
- 圖示使用 SVG sprite 或 icon font 優化載入
- CSS 使用現代佈局技術 (Flexbox)
- 圖片採用 lazy loading
- 支援 prefers-reduced-motion 媒體查詢

## 內容管理
- 標題和內文需支援動態內容
- 字數限制: 標題最多 30 字，內文最多 150 字
- 支援多語系顯示
- 內容超出時使用省略號處理

## 測試需求
- 各種螢幕尺寸的顯示測試
- 不同長度內容的排版測試
- 載入效能測試
- 無障礙功能測試
- 跨瀏覽器相容性測試

## 備註
- 此組件為獨立模組，可嵌入任何頁面
- 需提供完整的 CSS 和 HTML 範例
- 建議使用 CSS Grid 或 Flexbox 實作
- 考慮未來擴充性 (如新增按鈕、連結等功能)