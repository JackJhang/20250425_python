document.addEventListener('DOMContentLoaded', () => {
    // 取得漢堡選單按鈕元素
    const hamburgerMenu = document.querySelector('.hamburger-menu');
    // 取得手機版導覽選單疊層元素
    const mobileNavOverlay = document.querySelector('.mobile-nav-overlay');
    // 取得搜尋頁籤按鈕元素集合
    const searchTabs = document.querySelectorAll('.search-tab');
    // 取得房源卡片列表元素
    const propertyCardList = document.querySelector('.property-card-list');
    // 取得輪播向前按鈕元素
    const prevBtn = document.querySelector('.carousel-nav.prev-btn');
    // 取得輪播向後按鈕元素
    const nextBtn = document.querySelector('.carousel-nav.next-btn');
    // 取得分頁指示器點點的元素集合
    const dots = document.querySelectorAll('.carousel-pagination .dot');

    // 初始化當前輪播索引為 0
    let currentIndex = 0;
    // 初始化每頁顯示的卡片數量
    let cardsPerPage = 3; // 預設大螢幕顯示3張

    // 漢堡選單點擊事件監聽器
    hamburgerMenu.addEventListener('click', () => {
        // 切換手機版導覽選單的 'active' class，控制顯示/隱藏
        mobileNavOverlay.classList.toggle('active');
    });

    // 搜尋頁籤點擊事件監聽器
    searchTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // 移除所有頁籤的 'active' class
            searchTabs.forEach(t => t.classList.remove('active'));
            // 為當前點擊的頁籤添加 'active' class
            tab.classList.add('active');
            // 這裡可以根據不同的頁籤（Sale/Rent）實作不同的搜尋邏輯
            console.log(`切換到: ${tab.dataset.tab}`);
        });
    });

    /**
     * 更新輪播中每頁顯示的卡片數量，根據螢幕寬度調整。
     */
    function updateCardsPerPage() {
        if (window.innerWidth < 576) { // 超小型設備 (手機)
            cardsPerPage = 1;
        } else if (window.innerWidth >= 576 && window.innerWidth < 992) { // 小型到中型設備 (平板)
            cardsPerPage = 2;
        } else { // 大型設備 (筆記型電腦及以上)
            cardsPerPage = 3;
        }
        // 更新卡片列表的轉換 (transform) 效果，以反映新的顯示數量
        updateCarousel();
    }

    /**
     * 根據當前索引和每頁顯示的卡片數量來更新輪播的顯示。
     */
    function updateCarousel() {
        // 取得所有房源卡片的元素集合
        const cards = document.querySelectorAll('.property-card');
        if (cards.length === 0) return; // 如果沒有卡片，則不執行任何操作

        // 計算最大索引，確保不會超出卡片數量
        const maxIndex = Math.ceil(cards.length / cardsPerPage) - 1;
        // 如果當前索引超過最大索引，則調整為最大索引
        if (currentIndex > maxIndex) {
            currentIndex = maxIndex;
        }
        // 如果當前索引小於 0，則調整為 0
        if (currentIndex < 0) {
            currentIndex = 0;
        }

        // 計算每張卡片的寬度，包括左右 margin (30px = 15px * 2)
        // 這裡需要注意的是，由於 CSS 中 property-card 的 margin 是 15px，所以實際寬度要考慮到這個
        // 如果卡片在不同螢幕寬度下有不同的 margin 或 padding，這裡的計算需要更精確
        // 為了簡化，我們先假設每張卡片的實際佔用寬度是固定的，並通過 JS 動態計算偏移量
        // 一個更穩健的方法是動態獲取第一張卡片的實際寬度
        const cardWidth = cards[0].offsetWidth + (parseFloat(getComputedStyle(cards[0]).marginLeft) * 2);

        // 計算需要移動的距離
        const offset = -currentIndex * cardsPerPage * cardWidth;
        // 應用 CSS transform 來移動卡片列表
        propertyCardList.style.transform = `translateX(${offset}px)`;

        // 更新分頁指示器的 active 狀態
        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === currentIndex);
        });

        // 根據是否在起點或終點來啟用/禁用導覽按鈕
        prevBtn.disabled = currentIndex === 0;
        nextBtn.disabled = currentIndex >= maxIndex;
    }

    // 輪播向前按鈕點擊事件
    prevBtn.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--; // 索引減一
            updateCarousel(); // 更新輪播
        }
    });

    // 輪播向後按鈕點擊事件
    nextBtn.addEventListener('click', () => {
        // 取得所有房源卡片的元素集合
        const cards = document.querySelectorAll('.property-card');
        // 計算最大索引
        const maxIndex = Math.ceil(cards.length / cardsPerPage) - 1;
        if (currentIndex < maxIndex) {
            currentIndex++; // 索引加一
            updateCarousel(); // 更新輪播
        }
    });

    // 分頁指示器點擊事件
    dots.forEach(dot => {
        dot.addEventListener('click', (e) => {
            // 設定當前索引為點擊的點的 data-slide 值
            currentIndex = parseInt(e.target.dataset.slide);
            updateCarousel(); // 更新輪播
        });
    });

    // 視窗大小改變時更新每頁顯示的卡片數量
    window.addEventListener('resize', () => {
        updateCardsPerPage(); // 更新每頁卡片數量
    });

    // 頁面載入時和視窗大小改變時初始化輪播
    updateCardsPerPage();
});