class Accordion {
    constructor(element) {
        this.accordion = element;
        this.headers = this.accordion.querySelectorAll('.accordion-header');
        this.contents = this.accordion.querySelectorAll('.accordion-content');

        this.init();
    }

    init() {
        this.headers.forEach(header => {
            header.addEventListener('click', (e) => {
                this.toggle(e.currentTarget);
            });
        });
    }

    toggle(clickedHeader) {
        const targetId = clickedHeader.getAttribute('data-target');
        const targetContent = document.getElementById(targetId);
        const isActive = clickedHeader.classList.contains('active');

        // 關閉所有其他項目
        this.headers.forEach(header => {
            if (header !== clickedHeader) {
                header.classList.remove('active');
            }
        });

        this.contents.forEach(content => {
            if (content !== targetContent) {
                content.classList.remove('expanded');
                content.classList.add('collapsed');
            }
        });

        // 切換點擊的項目
        if (isActive) {
            clickedHeader.classList.remove('active');
            targetContent.classList.remove('expanded');
            targetContent.classList.add('collapsed');
        } else {
            clickedHeader.classList.add('active');
            targetContent.classList.remove('collapsed');
            targetContent.classList.add('expanded');
        }
    }
}

// 初始化手風琴
document.addEventListener('DOMContentLoaded', function () {
    const accordionElement = document.querySelector('.accordion');
    if (accordionElement) {
        new Accordion(accordionElement);
    }
});