好的，根據您的新需求，我將修改 CSS 樣式，確保無論視窗大小如何變化，手風琴元件的項目在標題部分始終保持兩欄佈局（即標題 `accordion-title` 和日期 `accordion-date` 在一行顯示，而不會在小螢幕上堆疊）。

這主要涉及調整 `768px` 和 `576px` 中斷點下的 `accordion-header` 樣式。

以下是修改後的完整技術需求規格 `技術需求_accordion.md`：

```markdown
# 技術需求規格：手風琴 (Accordion) 元件

## 1. 概述

本文件旨在規範一個手風琴 (Accordion) 元件的技術需求，該元件將用於顯示動態載入的標題和內容，並具有手風琴的收展功能。此元件將與 Jinja 模板引擎整合，並支援響應式設計 (RWD)。

## 2. 功能需求

* **手風琴功能**：支援單一或多個手風琴項目同時展開/收合。
* **標題與日期顯示**：每個手風琴項目需同時顯示標題 (Title) 和日期 (Date)。如 `accordion.png` 所示，日期應位於標題下方。
* **預設展開**：元件載入時，預設展開第一個手風琴項目。
* **多行標題**：標題內容可能為多行文字，需支援自動換行顯示。
* **固定高度內容**：內容區域的高度應固定不變，不論實際內容多寡。超出固定高度的內容應被截斷或隱藏，並考慮提供捲軸（視實際情況決定）。
* **最外層容器固定高度**：`accordion-container` 最外層容器需要固定顯示的高度，無論內部手風琴項目有多少列，並且應支援捲軸。
* **兩欄佈局（標題與日期）**：無論視窗如何改變，手風琴項目的標題 (`accordion-title`) 和日期 (`accordion-date`) 始終顯示在同一行，保持兩欄佈局。
* **響應式設計 (RWD)**：元件需具備響應式設計，並在以下中斷點調整佈局：
    * `576px` (sm)
    * `768px` (md)
    * `992px` (lg)
    * `1200px` (xl)
* **動態資料載入**：所有手風琴項目的資料（標題、日期、內容）應從外部資料庫動態取得。
* **版型嚴格遵循**：顯示的版型須嚴格按照 `accordion.png` 圖片所示。包括但不限於字體大小、間距、箭頭圖示位置等。
* **Jinja 模板整合**：網頁未來會手動套用來自 Jinja 格式的頁面。因此，HTML 結構應便於 Jinja 模板引擎進行資料迭代與渲染。

## 3. 技術規格

### 3.1. HTML 結構 (為 Jinja 模板設計)

HTML 結構應考慮到未來透過 Jinja 進行資料渲染，因此將採用類似以下結構：

```html
<div class="accordion-container">
    {% for item in accordion_data %}
    <div class="accordion-item {% if loop.first %}active{% endif %}">
        <div class="accordion-header">
            <h3 class="accordion-title">{{ item.title }}</h3>
            <div class="accordion-date">日期：{{ item.date }}</div>
            <span class="accordion-toggle-icon"></span> </div>
        <div class="accordion-content">
            <p>{{ item.content }}</p>
        </div>
    </div>
    {% endfor %}
</div>
```

**說明：**

* `accordion-container`: 整個手風琴元件的容器。此容器將設定固定高度和捲軸。
* `accordion-item`: 單個手風琴項目。`active` class 用於標示當前展開的項目。
* `accordion-header`: 手風琴項目的標題區域，包含標題、日期和切換圖示。
* `accordion-title`: 顯示標題的元素。
* `accordion-date`: 顯示日期的元素。
* `accordion-toggle-icon`: 用於表示展開/收合狀態的箭頭圖示。
* `accordion-content`: 手風琴項目的內容區域。
* `{{ item.title }}`, `{{ item.date }}`, `{{ item.content }}`: Jinja 模板語法，表示將從 `accordion_data` 變數中迭代出的資料。
* `{% if loop.first %}active{% endif %}`: Jinja 語法，用於在第一個項目上添加 `active` class，實現預設展開。

### 3.2. CSS 樣式

CSS 樣式將負責元件的視覺呈現、佈局以及響應式調整。

```css
/* 基本樣式 */
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f0f2f5;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    min-height: 100vh;
    padding-top: 20px;
}

.accordion-container {
    width: 100%;
    max-width: 800px; /* 根據實際需求調整最大寬度 */
    height: 400px; /* 固定容器高度，根據實際需求調整 */
    overflow-y: auto; /* 超出高度時顯示垂直捲軸 */
    margin: 20px auto;
    border: 1px solid #ddd;
    border-radius: 5px;
    background-color: #fff;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.accordion-item {
    border-bottom: 1px solid #eee;
}

.accordion-item:last-child {
    border-bottom: none;
}

.accordion-header {
    display: flex; /* 確保標題和日期在同一行 */
    align-items: center;
    padding: 15px 20px;
    background-color: #fff;
    cursor: pointer;
    position: relative;
    box-sizing: border-box; /* 確保 padding 不會影響寬度計算 */
}

.accordion-header:hover {
    background-color: #f9f9f9;
}

.accordion-title {
    flex-grow: 1; /* 標題佔據大部分空間 */
    margin: 0;
    font-size: 16px;
    line-height: 1.5; /* 確保多行標題的行高 */
    word-wrap: break-word; /* 允許長單詞換行 */
    color: #333;
    /* 為了在小螢幕上標題不擠壓日期，可以設定最小寬度或更靈活的 flex-basis */
    min-width: 0; /* 允許標題在空間不足時收縮 */
}

.accordion-date {
    font-size: 14px;
    color: #666;
    margin-left: 20px; /* 與標題的間距 */
    white-space: nowrap; /* 日期不換行 */
    flex-shrink: 0; /* 防止日期被壓縮 */
}

.accordion-toggle-icon {
    width: 0;
    height: 0;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 6px solid #333;
    transition: transform 0.3s ease;
    margin-left: 15px; /* 與日期的間距 */
    flex-shrink: 0; /* 防止箭頭被壓縮 */
}

.accordion-item.active .accordion-toggle-icon {
    transform: rotate(180deg);
}

.accordion-content {
    max-height: 0; /* 預設收合 */
    overflow: hidden;
    transition: max-height 0.3s ease-out;
    padding: 0 20px; /* 預設為0，展開時再設定 */
    box-sizing: border-box; /* 確保 padding 不會增加實際高度 */
    background-color: #fdfdfd;
    color: #555;
    font-size: 14px;
    line-height: 1.6;
}

.accordion-content p {
    margin: 0;
}

.accordion-item.active .accordion-content {
    max-height: 150px; /* 固定內容高度，根據實際需求調整 */
    padding: 15px 20px;
    border-top: 1px solid #eee;
    overflow-y: auto; /* 超出固定高度時顯示捲軸 */
}

/* 響應式設計 */
@media (max-width: 1200px) {
    /* Large devices (desktops, 992px and up) */
}

@media (max-width: 992px) {
    /* Medium devices (tablets, 768px and up) */
    .accordion-header {
        padding: 12px 15px;
    }
    .accordion-content {
        padding: 0 15px;
    }
    .accordion-item.active .accordion-content {
        padding: 12px 15px;
    }
    .accordion-date {
        margin-left: 15px;
    }
    .accordion-toggle-icon {
        margin-left: 10px;
    }
}

@media (max-width: 768px) {
    /* Small devices (landscape phones, 576px and up) */
    /* 保持 flex 佈局，不堆疊 */
    .accordion-header {
        flex-direction: row; /* 確保是行佈局 */
        align-items: center; /* 保持垂直居中 */
    }
    .accordion-title {
        margin-bottom: 0; /* 移除堆疊時的間距 */
    }
    .accordion-date {
        margin-left: 10px; /* 調整與標題的間距 */
        text-align: right; /* 確保日期靠右對齊 */
    }
    .accordion-toggle-icon {
        position: static; /* 箭頭保持在流中 */
        transform: none; /* 重置可能存在的轉換 */
        margin-left: 10px; /* 調整與日期的間距 */
        flex-shrink: 0;
    }
    .accordion-item.active .accordion-toggle-icon {
        transform: rotate(180deg); /* 僅旋轉 */
    }
}

@media (max-width: 576px) {
    /* Extra small devices (portrait phones, less than 576px) */
    .accordion-container {
        margin: 10px auto;
        border-radius: 0;
    }
    .accordion-header {
        padding: 10px 10px;
    }
    .accordion-content {
        padding: 0 10px;
    }
    .accordion-item.active .accordion-content {
        padding: 10px 10px;
    }
    .accordion-title {
        font-size: 15px;
    }
    .accordion-date {
        font-size: 13px;
        margin-left: 8px; /* 進一步調整小螢幕下的間距 */
    }
    .accordion-toggle-icon {
        margin-left: 8px; /* 進一步調整小螢幕下的間距 */
    }
}
```

### 3.3. JavaScript 行為

JavaScript 將負責處理手風琴的展開/收合邏輯，以及動態資料的載入（雖然資料載入部分通常由後端或數據層處理，但前端 JS 仍需接收並渲染）。

```javascript
document.addEventListener('DOMContentLoaded', function() {
    const accordionContainer = document.querySelector('.accordion-container');

    // 模擬從外部動態取得資料庫內容並顯示 (這部分通常由後端 API 或 AJAX 實現)
    // 這裡僅為示意，實際應用中應替換為實際的資料獲取邏輯
    function fetchDataAndRenderAccordion() {
        const mockData = [
            {
                title: "這是第一篇文章的標題，它可能會很長，需要自動換行以確保可讀性。",
                date: "2022-01-19",
                content: "回答常見問題的簡單句子，一個較長的段落，或者甚至是一個列表。這是一個範例內容，用來展示固定高度的效果。回答常見問題的簡單句子，一個較長的段落，或者甚至是一個列表。這是一個範例內容，用來展示固定高度的效果。回答常見問題的簡單句子，一個較長的段落，或者甚至是一個列表。這是一個範例內容，用來展示固定高度的效果。回答常見問題的簡單句子，一個較長的段落，或者甚至是一個列表。這是一個範例內容，用來展示固定高度的效果。回答常見問題的簡單句子，一個較長的段落，或者甚至是一個列表。這是一個範例內容，用來展示固定高度的效果。"
            },
            {
                title: "第二個手風琴項目，包含一些關於產品特色的說明。",
                date: "2023-03-01",
                content: "我們的產品具有高度的靈活性和可擴展性，能滿足您不斷變化的業務需求。它整合了最新的技術，提供了無縫的使用者體驗。我們的產品具有高度的靈活性和可擴展性，能滿足您不斷變化的業務需求。它整合了最新的技術，提供了無縫的使用者體驗。"
            },
            {
                title: "關於服務條款的重要通知，請仔細閱讀。",
                date: "2024-05-15",
                content: "使用本服務前，請仔細閱讀並同意我們的服務條款。服務條款可能不時更新，請定期查閱最新版本。使用本服務前，請仔細閱讀並同意我們的服務條款。服務條款可能不時更新，請定期查閱最新版本。"
            },
            {
                title: "常見問題解答，幫助您快速了解。",
                date: "2025-01-01",
                content: "Q: 如何聯繫客服？ A: 您可以透過電子郵件或電話聯繫我們的客服團隊。 Q: 是否支援多國語言？ A: 是的，我們的系統支援多種語言介面。 Q: 如何聯繫客服？ A: 您可以透過電子郵件或電話聯繫我們的客服團隊。 Q: 是否支援多國語言？ A: 是的，我們的系統支援多種語言介面。"
            },
            {
                title: "最後一個手風琴項目，展示較短的內容。",
                date: "2025-05-20",
                content: "這是簡短的內容。"
            }
        ];

        // 清空現有內容（如果有的話，以防重複渲染）
        accordionContainer.innerHTML = '';

        mockData.forEach((data, index) => {
            const isActive = index === 0 ? 'active' : ''; // 第一筆預設展開
            const itemHTML = `
                <div class="accordion-item ${isActive}">
                    <div class="accordion-header">
                        <h3 class="accordion-title">${data.title}</h3>
                        <div class="accordion-date">日期：${data.date}</div>
                        <span class="accordion-toggle-icon"></span>
                    </div>
                    <div class="accordion-content">
                        <p>${data.content}</p>
                    </div>
                </div>
            `;
            accordionContainer.insertAdjacentHTML('beforeend', itemHTML);
        });

        // 重新綁定事件監聽器，因為元素是動態添加的
        const newAccordionItems = document.querySelectorAll('.accordion-item');
        newAccordionItems.forEach(item => {
            const header = item.querySelector('.accordion-header');
            const content = item.querySelector('.accordion-content');

            header.addEventListener('click', () => {
                // 收合所有其他項目，若需多個同時展開，則移除此段
                newAccordionItems.forEach(otherItem => {
                    if (otherItem !== item && otherItem.classList.contains('active')) {
                        otherItem.classList.remove('active');
                        otherItem.querySelector('.accordion-content').style.maxHeight = '0';
                    }
                });

                // 切換當前項目的展開/收合狀態
                item.classList.toggle('active');
                if (item.classList.contains('active')) {
                    content.style.maxHeight = '150px'; // 固定內容高度
                } else {
                    content.style.maxHeight = '0';
                }
            });
        });

        // 確保動態載入後，第一個項目也預設展開並設定高度
        if (newAccordionItems.length > 0) {
            const firstItem = newAccordionItems[0];
            firstItem.classList.add('active');
            const firstContent = firstItem.querySelector('.accordion-content');
            firstContent.style.maxHeight = '150px';
        }
    }

    // 在頁面載入完成後模擬載入資料
    fetchDataAndRenderAccordion();
});
```

### 3.4. 資料格式 (外部資料庫內容)

來自外部資料庫的內容預期為一個 JSON 陣列，每個物件代表一個手風琴項目，包含 `title`、`date` 和 `content` 欄位。

```json
[
    {
        "title": "這是第一篇文章的標題，它可能會很長，需要自動換行以確保可讀性。",
        "date": "2022-01-19",
        "content": "回答常見問題的簡單句子，一個較長的段落，或者甚至是一個列表。"
    },
    {
        "title": "第二個手風琴項目，包含一些關於產品特色的說明。",
        "date": "2023-03-01",
        "content": "我們的產品具有高度的靈活性和可擴展性，能滿足您不斷變化的業務需求。"
    },
    // ... 更多項目
]
```

## 4. 測試頁面 (test.html)

為了方便開發與測試，需提供一個 `test.html` 頁面，該頁面將包含上述 HTML、CSS 和 JavaScript，並模擬動態資料載入。

```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>手風琴元件測試頁面</title>
    <style>
        /* CSS 樣式將直接嵌入此處或連結外部CSS檔案 */
        /* 參照 3.2. CSS 樣式 的內容 */
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f0f2f5;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
            padding-top: 20px;
        }

        .accordion-container {
            width: 100%;
            max-width: 800px; /* 根據實際需求調整最大寬度 */
            height: 400px; /* 固定容器高度，根據實際需求調整 */
            overflow-y: auto; /* 超出高度時顯示垂直捲軸 */
            margin: 20px auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #fff;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        .accordion-item {
            border-bottom: 1px solid #eee;
        }

        .accordion-item:last-child {
            border-bottom: none;
        }

        .accordion-header {
            display: flex; /* 確保標題和日期在同一行 */
            align-items: center;
            padding: 15px 20px;
            background-color: #fff;
            cursor: pointer;
            position: relative;
            box-sizing: border-box; /* 確保 padding 不會影響寬度計算 */
        }

        .accordion-header:hover {
            background-color: #f9f9f9;
        }

        .accordion-title {
            flex-grow: 1; /* 標題佔據大部分空間 */
            margin: 0;
            font-size: 16px;
            line-height: 1.5; /* 確保多行標題的行高 */
            word-wrap: break-word; /* 允許長單詞換行 */
            color: #333;
            min-width: 0; /* 允許標題在空間不足時收縮 */
        }

        .accordion-date {
            font-size: 14px;
            color: #666;
            margin-left: 20px; /* 與標題的間距 */
            white-space: nowrap; /* 日期不換行 */
            flex-shrink: 0; /* 防止日期被壓縮 */
        }

        .accordion-toggle-icon {
            width: 0;
            height: 0;
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-top: 6px solid #333;
            transition: transform 0.3s ease;
            margin-left: 15px; /* 與日期的間距 */
            flex-shrink: 0; /* 防止箭頭被壓縮 */
        }

        .accordion-item.active .accordion-toggle-icon {
            transform: rotate(180deg);
        }

        .accordion-content {
            max-height: 0; /* 預設收合 */
            overflow: hidden;
            transition: max-height 0.3s ease-out;
            padding: 0 20px; /* 預設為0，展開時再設定 */
            box-sizing: border-box; /* 確保 padding 不會增加實際高度 */
            background-color: #fdfdfd;
            color: #555;
            font-size: 14px;
            line-height: 1.6;
        }

        .accordion-content p {
            margin: 0;
        }

        .accordion-item.active .accordion-content {
            max-height: 150px; /* 固定內容高度，根據實際需求調整 */
            padding: 15px 20px;
            border-top: 1px solid #eee;
            overflow-y: auto; /* 超出固定高度時顯示捲軸 */
        }

        /* 響應式設計 */
        @media (max-width: 1200px) {
            /* Large devices (desktops, 992px and up) */
        }

        @media (max-width: 992px) {
            /* Medium devices (tablets, 768px and up) */
            .accordion-header {
                padding: 12px 15px;
            }
            .accordion-content {
                padding: 0 15px;
            }
            .accordion-item.active .accordion-content {
                padding: 12px 15px;
            }
            .accordion-date {
                margin-left: 15px;
            }
            .accordion-toggle-icon {
                margin-left: 10px;
            }
        }

        @media (max-width: 768px) {
            /* Small devices (landscape phones, 576px and up) */
            /* 保持 flex 佈局，不堆疊 */
            .accordion-header {
                flex-direction: row; /* 確保是行佈局 */
                align-items: center; /* 保持垂直居中 */
            }
            .accordion-title {
                margin-bottom: 0; /* 移除堆疊時的間距 */
            }
            .accordion-date {
                margin-left: 10px; /* 調整與標題的間距 */
                text-align: right; /* 確保日期靠右對齊 */
            }
            .accordion-toggle-icon {
                position: static; /* 箭頭保持在流中 */
                transform: none; /* 重置可能存在的轉換 */
                margin-left: 10px; /* 調整與日期的間距 */
                flex-shrink: 0;
            }
            .accordion-item.active .accordion-toggle-icon {
                transform: rotate(180deg); /* 僅旋轉 */
            }
        }

        @media (max-width: 576px) {
            /* Extra small devices (portrait phones, less than 576px) */
            .accordion-container {
                margin: 10px auto;
                border-radius: 0;
            }
            .accordion-header {
                padding: 10px 10px;
            }
            .accordion-content {
                padding: 0 10px;
            }
            .accordion-item.active .accordion-content {
                padding: 10px 10px;
            }
            .accordion-title {
                font-size: 15px;
            }
            .accordion-date {
                font-size: 13px;
                margin-left: 8px; /* 進一步調整小螢幕下的間距 */
            }
            .accordion-toggle-icon {
                margin-left: 8px; /* 進一步調整小螢幕下的間距 */
            }
        }
    </style>
</head>
<body>
    <div class="accordion-container">
        </div>

    <script>
        // JavaScript 程式碼將直接嵌入此處或連結外部JS檔案
        // 參照 3.3. JavaScript 行為 的內容
        document.addEventListener('DOMContentLoaded', function() {
            const accordionContainer = document.querySelector('.accordion-container');

            // 模擬從外部動態取得資料庫內容並顯示
            function fetchDataAndRenderAccordion() {
                const mockData = [
                    {
                        title: "這是第一篇文章的標題，它可能會很長，需要自動換行以確保可讀性。",
                        date: "2022-01-19",
                        content: "回答常見問題的簡單句子，一個較長的段落，或者甚至是一個列表。這是一個範例內容，用來展示固定高度的效果。回答常見問題的簡單句子，一個較長的段落，或者甚至是一個列表。這是一個範例內容，用來展示固定高度的效果。回答常見問題的簡單句子，一個較長的段落，或者甚至是一個列表。這是一個範例內容，用來展示固定高度的效果。回答常見問題的簡單句子，一個較長的段落，或者甚至是一個列表。這是一個範例內容，用來展示固定高度的效果。"
                    },
                    {
                        title: "第二個手風琴項目，包含一些關於產品特色的說明。",
                        date: "2023-03-01",
                        content: "我們的產品具有高度的靈活性和可擴展性，能滿足您不斷變化的業務需求。它整合了最新的技術，提供了無縫的使用者體驗。我們的產品具有高度的靈活性和可擴展性，能滿足您不斷變化的業務需求。它整合了最新的技術，提供了無縫的使用者體驗。"
                    },
                    {
                        title: "關於服務條款的重要通知，請仔細閱讀。",
                        date: "2024-05-15",
                        content: "使用本服務前，請仔細閱讀並同意我們的服務條款。服務條款可能不時更新，請定期查閱最新版本。使用本服務前，請仔細閱讀並同意我們的服務條款。服務條款可能不時更新，請定期查閱最新版本。"
                    },
                    {
                        title: "常見問題解答，幫助您快速了解。",
                        date: "2025-01-01",
                        content: "Q: 如何聯繫客服？ A: 您可以透過電子郵件或電話聯繫我們的客服團隊。 Q: 是否支援多國語言？ A: 是的，我們的系統支援多種語言介面。 Q: 如何聯繫客服？ A: 您可以透過電子郵件或電話聯繫我們的客服團隊。 Q: 是否支援多國語言？ A: 是的，我們的系統支援多種語言介面。"
                    },
                    {
                        title: "最後一個手風琴項目，展示較短的內容。",
                        date: "2025-05-20",
                        content: "這是簡短的內容。"
                    }
                ];

                // 清空現有內容（如果有的話，以防重複渲染）
                accordionContainer.innerHTML = '';

                mockData.forEach((data, index) => {
                    const isActive = index === 0 ? 'active' : ''; // 第一筆預設展開
                    const itemHTML = `
                        <div class="accordion-item ${isActive}">
                            <div class="accordion-header">
                                <h3 class="accordion-title">${data.title}</h3>
                                <div class="accordion-date">日期：${data.date}</div>
                                <span class="accordion-toggle-icon"></span>
                            </div>
                            <div class="accordion-content">
                                <p>${data.content}</p>
                            </div>
                        </div>
                    `;
                    accordionContainer.insertAdjacentHTML('beforeend', itemHTML);
                });

                // 重新綁定事件監聽器，因為元素是動態添加的
                const newAccordionItems = document.querySelectorAll('.accordion-item');
                newAccordionItems.forEach(item => {
                    const header = item.querySelector('.accordion-header');
                    const content = item.querySelector('.accordion-content');

                    header.addEventListener('click', () => {
                        newAccordionItems.forEach(otherItem => {
                            if (otherItem !== item && otherItem.classList.contains('active')) {
                                otherItem.classList.remove('active');
                                otherItem.querySelector('.accordion-content').style.maxHeight = '0';
                            }
                        });

                        item.classList.toggle('active');
                        if (item.classList.contains('active')) {
                            content.style.maxHeight = '150px'; // 固定內容高度
                        } else {
                            content.style.maxHeight = '0';
                        }
                    });
                });

                // 確保動態載入後，第一個項目也預設展開並設定高度
                if (newAccordionItems.length > 0) {
                    const firstItem = newAccordionItems[0];
                    firstItem.classList.add('active');
                    const firstContent = firstItem.querySelector('.accordion-content');
                    firstContent.style.maxHeight = '150px';
                }
            }

            // 在頁面載入完成後模擬載入資料
            fetchDataAndRenderAccordion();
        });
    </script>
</body>
</html>
```