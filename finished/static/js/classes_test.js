document.addEventListener('DOMContentLoaded', () => {
    const courseOptionsContainer = document.querySelector('.course-options');
    const buttons = courseOptionsContainer.querySelectorAll('.course-btn');

    // 預設選中第一個按鈕 (如果沒有在HTML中預設active)
    // 這裡根據HTML結構，預設 '一般課程' 是選中的
    // if (!courseOptionsContainer.querySelector('.course-btn.active')) {
    //     buttons[0].classList.add('active');
    //     buttons[0].setAttribute('aria-checked', 'true');
    //     buttons[0].setAttribute('tabindex', '0');
    // }

    courseOptionsContainer.addEventListener('click', (event) => {
        const clickedButton = event.target.closest('.course-btn');

        if (clickedButton && !clickedButton.classList.contains('active')) {
            // 移除所有按鈕的 active 狀態和 aria-checked
            buttons.forEach(button => {
                button.classList.remove('active');
                button.setAttribute('aria-checked', 'false');
                button.setAttribute('tabindex', '-1'); // 將未選中的按鈕移出 tab 順序
            });

            // 為被點擊的按鈕添加 active 狀態和 aria-checked
            clickedButton.classList.add('active');
            clickedButton.setAttribute('aria-checked', 'true');
            clickedButton.setAttribute('tabindex', '0'); // 將選中的按鈕加入 tab 順序

            // 可以加入一個回調函數，供外部監聽選擇變化
            const selectedCourseType = clickedButton.dataset.course;
            console.log(`課程類型已切換至: ${selectedCourseType}`);
            // 觸發自定義事件，供外部模組監聽
            const customEvent = new CustomEvent('courseSelected', {
                detail: { courseType: selectedCourseType }
            });
            document.dispatchEvent(customEvent);
        }
    });

    // 鍵盤導航支援
    courseOptionsContainer.addEventListener('keydown', (event) => {
        const currentActive = courseOptionsContainer.querySelector('.course-btn[tabindex="0"]');
        let nextButton;

        if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
            event.preventDefault();
            nextButton = currentActive.nextElementSibling;
            if (!nextButton || !nextButton.classList.contains('course-btn')) {
                nextButton = buttons[0]; // 循環到第一個
            }
        } else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
            event.preventDefault();
            nextButton = currentActive.previousElementSibling;
            if (!nextButton || !nextButton.classList.contains('course-btn')) {
                nextButton = buttons[buttons.length - 1]; // 循環到最後一個
            }
        } else if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            // 模擬點擊當前焦點元素
            currentActive.click();
        }

        if (nextButton) {
            currentActive.setAttribute('tabindex', '-1');
            currentActive.setAttribute('aria-checked', 'false');
            nextButton.setAttribute('tabindex', '0');
            nextButton.setAttribute('aria-checked', 'true');
            nextButton.focus(); // 將焦點移動到新的活動按鈕
            // 觸發點擊事件，確保狀態同步
            nextButton.click();
        }
    });
});