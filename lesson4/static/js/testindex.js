const menuButton = document.querySelector('.menu-button');  // 選取 HTML 中 class 為 "menu-button" 的元素，即 MENU 按鈕
const navLinks = document.querySelector('.nav-links');      // 選取 HTML 中 class 為 "nav-links" 的元素，即導覽連結列表

menuButton.addEventListener('click', () => {           // 為 MENU 按鈕新增一個點擊事件監聽器
    navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex'; // 切換導覽連結列表的顯示狀態：如果目前是 flex（顯示），就改為 none（隱藏），反之亦然
});