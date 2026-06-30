(function() {
    'use strict';

    // ----------------------------------------------------------------
    // 1. Add floating Dashboard button (will be hidden on desktop by CSS)
    // ----------------------------------------------------------------
    function addFloatingDashboardButton() {
        // Avoid duplicates
        if (document.getElementById('floating-dashboard-btn')) return;

        const btn = document.createElement('div');
        btn.id = 'floating-dashboard-btn';
        btn.innerHTML = '<i class="fas fa-tachometer-alt" style="margin-right: 8px;"></i> Dashboard';
        btn.addEventListener('click', function() {
            window.location.href = '/dashboard/admin/';
        });
        document.body.appendChild(btn);
    }

    // ----------------------------------------------------------------
    // 2. Prevent page from auto‑scrolling to top on sidebar link clicks
    // ----------------------------------------------------------------
    function preventAutoScroll() {
        window.addEventListener('beforeunload', function() {
            sessionStorage.setItem('scrollY', window.scrollY);
        });
        window.addEventListener('load', function() {
            const savedScroll = sessionStorage.getItem('scrollY');
            if (savedScroll && parseInt(savedScroll) > 0) {
                window.scrollTo(0, parseInt(savedScroll));
                sessionStorage.removeItem('scrollY');
            }
        });
        document.querySelectorAll('.nav-sidebar .nav-link, .sidebar .nav-link').forEach(link => {
            link.addEventListener('click', function() {
                sessionStorage.setItem('scrollY', window.scrollY);
            });
        });
    }

    // ----------------------------------------------------------------
    // 3. Highlight active sidebar link
    // ----------------------------------------------------------------
    function highlightActiveLink() {
        const links = document.querySelectorAll('.nav-sidebar .nav-link');
        const currentPath = window.location.pathname;
        links.forEach(link => {
            const href = link.getAttribute('href');
            if (href && currentPath.startsWith(href) && href !== '/dashboard/admin/') {
                link.classList.add('active');
                setTimeout(() => {
                    link.scrollIntoView({ block: 'center', behavior: 'smooth' });
                }, 100);
            } else if (href && currentPath === href) {
                link.classList.add('active');
                setTimeout(() => {
                    link.scrollIntoView({ block: 'center', behavior: 'smooth' });
                }, 100);
            }
        });
    }

    // ----------------------------------------------------------------
    // 4. Run on load
    // ----------------------------------------------------------------
    document.addEventListener('DOMContentLoaded', function() {
        addFloatingDashboardButton();
        preventAutoScroll();
        highlightActiveLink();
    });

})();