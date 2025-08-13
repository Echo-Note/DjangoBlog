// =页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化回到顶部按钮
    initBackToTop();

    // 初始化移动端菜单切换
    initMobileMenu();

    // 初始化评论回复功能
    initCommentReply();

    // 初始化所有需要的函数
    initAll();
});

// =回到顶部功能
function initBackToTop() {
    const rocket = document.getElementById('rocket');

    if (!rocket) return;

    // 监听滚动事件
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            rocket.classList.add('show');
        } else {
            rocket.classList.remove('show');
        }
    });

    // 点击回到顶部
    rocket.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// =移动端菜单切换
function initMobileMenu() {
    const menuToggle = document.querySelector('.menu-toggle');
    const menuContainer = document.querySelector('.menu-container');

    if (!menuToggle || !menuContainer) return;

    menuToggle.addEventListener('click', function() {
        menuContainer.classList.toggle('active');
    });
}

// =评论回复功能
function initCommentReply() {
    // 处理回复按钮点击
    document.querySelectorAll('.reply a').forEach(function(replyLink) {
        replyLink.addEventListener('click', function(e) {
            e.preventDefault();

            const commentId = this.getAttribute('data-comment-id');
            const commentForm = document.getElementById('comment-form');
            const parentIdInput = document.getElementById('id_parent');

            if (commentForm && parentIdInput) {
                parentIdInput.value = commentId;
                commentForm.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // 处理取消回复
    const cancelReplyLink = document.getElementById('cancel-reply');
    if (cancelReplyLink) {
        cancelReplyLink.addEventListener('click', function(e) {
            e.preventDefault();

            const parentIdInput = document.getElementById('id_parent');
            if (parentIdInput) {
                parentIdInput.value = '';
            }
        });
    }
}

// =初始化所有功能
function initAll() {
    // 可以在这里添加其他需要初始化的功能
    console.log('页面初始化完成');
}

// =工具函数：平滑滚动到指定元素
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// =工具函数：获取URL参数
function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    const results = regex.exec(window.location.href);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

// =页面加载进度条（使用NProgress）
window.addEventListener('beforeunload', function() {
    if (typeof NProgress !== 'undefined') {
        NProgress.start();
    }
});

window.addEventListener('load', function() {
    if (typeof NProgress !== 'undefined') {
        NProgress.done();
    }
});
