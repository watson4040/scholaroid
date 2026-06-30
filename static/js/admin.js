(function() {
    'use strict';

    // ----------------------------------------------------------------
    // 1. Ensure Dashboard link appears in the top menu (especially on mobile)
    // ----------------------------------------------------------------
    function addDashboardLinkToTopMenu() {
        const topMenu = document.querySelector('#header .top-menu');
        if (!topMenu) return;

        // Check if Dashboard link already exists
        const existing = topMenu.querySelector('a[href*="/dashboard/admin/"]');
        if (existing) return;

        // Create the Dashboard link
        const dashboardLink = document.createElement('a');
        dashboardLink.href = '/dashboard/admin/';
        dashboardLink.className = 'nav-link';
        dashboardLink.textContent = 'Dashboard';
        dashboardLink.style.fontWeight = 'bold';
        dashboardLink.style.color = '#28a745';
        dashboardLink.style.display = 'inline-block';
        // Insert it before the first child (or after Home)
        const firstLink = topMenu.querySelector('.nav-link');
        if (firstLink) {
            topMenu.insertBefore(dashboardLink, firstLink.nextSibling);
        } else {
            topMenu.appendChild(dashboardLink);
        }
    }

    // ----------------------------------------------------------------
    // 2. Prevent page from auto‑scrolling to top on sidebar link clicks
    // ----------------------------------------------------------------
    function preventAutoScroll() {
        // Store scroll position before unloading
        window.addEventListener('beforeunload', function() {
            sessionStorage.setItem('scrollY', window.scrollY);
        });

        // Restore scroll position after load (if not at top)
        window.addEventListener('load', function() {
            const savedScroll = sessionStorage.getItem('scrollY');
            if (savedScroll && parseInt(savedScroll) > 0) {
                window.scrollTo(0, parseInt(savedScroll));
                sessionStorage.removeItem('scrollY');
            }
        });

        // Also, listen to sidebar link clicks and store current scroll position
        document.querySelectorAll('.nav-sidebar .nav-link, .sidebar .nav-link').forEach(link => {
            link.addEventListener('click', function(e) {
                // Save current scroll position before navigation
                sessionStorage.setItem('scrollY', window.scrollY);
                // Allow navigation to proceed (the page will reload)
                // The 'load' event will restore the position.
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
    // 4. Run all on DOM ready
    // ----------------------------------------------------------------
    document.addEventListener('DOMContentLoaded', function() {
        addDashboardLinkToTopMenu();
        preventAutoScroll();
        highlightActiveLink();
    });

})();