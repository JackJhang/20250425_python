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
    // 取得分頁指示器容器元素
    const paginationContainer = document.querySelector('.carousel-pagination');

    let originalCards = []; // 用於儲存原始卡片的陣列
    let cardsPerPage = 3;   // 初始化每頁顯示的卡片數量 (RWD 會調整)
    let totalOriginalCards = 0; // 原始卡片的總數
    let infiniteScrollOffset = 0; // 無限輪播的偏移量 (複製的卡片數量)
    let currentSlideIndex = 0; // 當前在原始卡片中的邏輯索引

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
     * 複製卡片以實現無限輪播效果。
     * 會複製一定數量的原始卡片到列表的前後。
     */
    function setupInfiniteScroll() {
        // 取得所有原始的房源卡片
        originalCards = Array.from(propertyCardList.querySelectorAll('.property-card'));
        totalOriginalCards = originalCards.length;

        // 如果卡片數量不足以進行無限輪播，則不複製
        if (totalOriginalCards === 0) return;

        // 清空現有列表，準備重新添加
        propertyCardList.innerHTML = '';

        // 複製最後幾張卡片到開頭 (為向前無限輪播準備)
        // 複製數量應至少為 cardsPerPage
        infiniteScrollOffset = cardsPerPage; // 這裡簡化為複製一頁的數量
        for (let i = 0; i < infiniteScrollOffset; i++) {
            const cardToPrepend = originalCards[totalOriginalCards - infiniteScrollOffset + i].cloneNode(true);
            cardToPrepend.classList.add('cloned'); // 添加 class 以區分複製卡片
            propertyCardList.appendChild(cardToPrepend);
        }

        // 添加原始卡片
        originalCards.forEach(card => {
            const originalCardClone = card.cloneNode(true);
            originalCardClone.classList.add('original'); // 添加 class 以區分原始卡片
            propertyCardList.appendChild(originalCardClone);
        });

        // 複製前幾張卡片到結尾 (為向後無限輪播準備)
        for (let i = 0; i < infiniteScrollOffset; i++) {
            const cardToAppend = originalCards[i].cloneNode(true);
            cardToAppend.classList.add('cloned'); // 添加 class 以區分複製卡片
            propertyCardList.appendChild(cardToAppend);
        }

        // 調整初始位置到原始卡片的開頭
        // 初始 `currentSlideIndex` 仍然是 0 (邏輯上的第一張原始卡片)
        // 但實際 `transform` 的 `offset` 需要加上 `infiniteScrollOffset`
        currentSlideIndex = 0; // 邏輯上的第一張原始卡片
        // 第一次設定時，讓它跳到正確的起始位置，不帶過渡效果
        propertyCardList.style.transition = 'none';
        updateCarousel(false); // 初始時不帶過渡效果
        // 確保在下一幀開啟過渡效果，以便後續操作有動畫
        setTimeout(() => {
            propertyCardList.style.transition = 'transform 0.5s ease-in-out';
        }, 0);
    }

    /**
     * 動態生成分頁指示器點點。
     */
    function createPaginationDots() {
        paginationContainer.innerHTML = ''; // 清空現有所有點點
        for (let i = 0; i < totalOriginalCards; i++) {
            const dot = document.createElement('span');
            dot.classList.add('dot');
            dot.dataset.slide = i; // 儲存對應的原始卡片索引
            dot.addEventListener('click', (e) => {
                currentSlideIndex = parseInt(e.target.dataset.slide);
                updateCarousel(true); // 點擊點點時帶有過渡效果
            });
            paginationContainer.appendChild(dot);
        }
    }

    /**
     * 更新輪播顯示和位置。
     * @param {boolean} withTransition - 是否帶有 CSS 過渡效果。
     */
    function updateCarousel(withTransition = true) {
        // 取得所有房源卡片 (包括複製的)
        const allCards = propertyCardList.querySelectorAll('.property-card');
        if (allCards.length === 0) return;

        // 計算每張卡片的完整寬度 (卡片寬度 + 左右 margin)
        // 獲取第一張卡片的實際計算寬度
        const firstCard = allCards[0];
        const cardStyle = getComputedStyle(firstCard);
        const cardMarginLeft = parseFloat(cardStyle.marginLeft);
        const cardMarginRight = parseFloat(cardStyle.marginRight);
        const cardWidth = firstCard.offsetWidth + cardMarginLeft + cardMarginRight;

        // 計算實際要移動到的索引
        // 這是因為有複製的卡片在前面，所以要加上偏移量
        const actualIndex = infiniteScrollOffset + currentSlideIndex;

        // 計算需要移動的距離
        const offset = -actualIndex * cardWidth;

        // 設定或移除過渡效果
        propertyCardList.style.transition = withTransition ? 'transform 0.5s ease-in-out' : 'none';
        // 應用 CSS transform 來移動卡片列表
        propertyCardList.style.transform = `translateX(${offset}px)`;

        // 更新分頁指示器的 active 狀態
        const dots = document.querySelectorAll('.carousel-pagination .dot');
        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === currentSlideIndex);
        });
    }

    /**
     * 檢查是否到達了無限輪播的邊界，並進行瞬間跳轉。
     */
    function checkInfiniteLoop() {
        // 檢查是否移動到複製的前半部 (左側)
        if (currentSlideIndex < 0) {
            // 瞬間跳轉到原始卡片的最後一組
            currentSlideIndex = totalOriginalCards - 1;
            updateCarousel(false); // 不帶過渡效果
            // 在下一個動畫幀重新開啟過渡效果，以便後續操作有動畫
            setTimeout(() => {
                propertyCardList.style.transition = 'transform 0.5s ease-in-out';
            }, 0);
        }
        // 檢查是否移動到複製的後半部 (右側)
        else if (currentSlideIndex >= totalOriginalCards) {
            // 瞬間跳轉到原始卡片的第一組
            currentSlideIndex = 0;
            updateCarousel(false); // 不帶過渡效果
            // 在下一個動畫幀重新開啟過渡效果，以便後續操作有動畫
            setTimeout(() => {
                propertyCardList.style.transition = 'transform 0.5s ease-in-out';
            }, 0);
        }
    }


    /**
     * 處理輪播向前移動的邏輯。
     */
    prevBtn.addEventListener('click', () => {
        currentSlideIndex--; // 邏輯索引減一
        updateCarousel(true); // 帶過渡效果更新輪播
        // 在過渡結束後檢查是否需要瞬間跳轉
        propertyCardList.addEventListener('transitionend', checkInfiniteLoop, { once: true });
    });

    /**
     * 處理輪播向後移動的邏輯。
     */
    nextBtn.addEventListener('click', () => {
        currentSlideIndex++; // 邏輯索引加一
        updateCarousel(true); // 帶過渡效果更新輪播
        // 在過渡結束後檢查是否需要瞬間跳轉
        propertyCardList.addEventListener('transitionend', checkInfiniteLoop, { once: true });
    });

    /**
     * 根據螢幕寬度調整每頁顯示的卡片數量並重新初始化輪播。
     */
    function handleResize() {
        // 判斷當前螢幕尺寸下的 cardsPerPage
        if (window.innerWidth < 576) { // 超小型設備 (手機)
            cardsPerPage = 1;
        } else if (window.innerWidth >= 576 && window.innerWidth < 992) { // 小型到中型設備 (平板)
            cardsPerPage = 2;
        } else { // 大型設備 (筆記型電腦及以上)
            cardsPerPage = 3;
        }
        // 重新設置無限輪播 (複製卡片並調整位置)
        setupInfiniteScroll();
        // 重新創建分頁指示器點點
        createPaginationDots();
        // 確保初始位置正確顯示
        updateCarousel(false); // 第一次更新時不帶過渡
    }

    // 視窗大小改變時，重新處理輪播邏輯
    window.addEventListener('resize', handleResize);

    // 頁面首次載入時，初始化輪播
    handleResize(); // 第一次執行以設定正確的 cardsPerPage 和初始化輪播
});