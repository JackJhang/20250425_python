document.addEventListener('DOMContentLoaded', function () {
    // 在 Jinja2 渲染的頁面中，JS 不再需要「模擬」資料獲取，
    // 因為資料已經在伺服器端渲染到 HTML 中了。
    // 這裡的 JS 僅負責手風琴的交互邏輯。

    const accordionItems = document.querySelectorAll('.accordion-item');

    accordionItems.forEach(item => {
        const header = item.querySelector('.accordion-header');
        const content = item.querySelector('.accordion-content');

        header.addEventListener('click', () => {
            // 收合所有其他項目（如果需要單一展開）
            accordionItems.forEach(otherItem => {
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

    // 預設展開第一個項目 (因為 Jinja2 已經添加了 active class)
    // 確保其內容高度被正確設定
    const firstActiveItem = document.querySelector('.accordion-item.active');
    if (firstActiveItem) {
        const firstContent = firstActiveItem.querySelector('.accordion-content');
        firstContent.style.maxHeight = '150px';
    }
});