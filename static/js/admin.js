(function() {
    'use strict';

    // ----------------------------------------------------------------
    // 1. Add a floating Dashboard button on mobile (always visible)
    // ----------------------------------------------------------------
    function addFloatingDashboardButton() {
        // Only for screens smaller than 768px (mobile)
        if (window.innerWidth >= 768) return;

        // Check if button already exists
        if (document.getElementById('floating-dashboard-btn')) return;

        const btn = document.createElement('div');
        btn.id = 'floating-dashboard-btn';
        btn.innerHTML = '<i class="fas fa-tachometer-alt" style="margin-right: 6px;"></i> Dashboard';
        btn.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            background: #28a745;
            color: white;
            padding: 12px 18px;
            border-radius: 50px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            border: none;
        `;
        btn.addEventListener('click', function() {
            window.location.href = '/dashboard/admin/';
        });
        // Hover effect (on desktop, but works on mobile too)
        btn.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.95)';
        });
        btn.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
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
    // 3. Keep active sidebar link highlighted and visible
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
    // 4. Run on DOM ready and on resize (to re-check screen width)
    // ----------------------------------------------------------------
    document.addEventListener('DOMContentLoaded', function() {
        addFloatingDashboardButton();
        preventAutoScroll();
        highlightActiveLink();
    });

    // Re-run on resize (for orientation changes)
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            // Remove old button if it exists and re-add based on new width
            const oldBtn = document.getElementById('floating-dashboard-btn');
            if (oldBtn) oldBtn.remove();
            addFloatingDashboardButton();
        }, 300);
    });

})();