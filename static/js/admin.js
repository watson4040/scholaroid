(function() {
    'use strict';

    // ─── Highlight active sidebar link and scroll it into view inside sidebar ───
    function highlightActiveLink() {
        const links = document.querySelectorAll('.nav-sidebar .nav-link');
        const currentPath = window.location.pathname;
        let activeFound = false;
        links.forEach(link => {
            const href = link.getAttribute('href');
            if (href && (currentPath.startsWith(href) && href !== '/dashboard/admin/')) {
                link.classList.add('active');
                activeFound = true;
                // Scroll only the sidebar container, not the whole page
                const sidebar = link.closest('.nav-sidebar, .sidebar');
                if (sidebar) {
                    setTimeout(() => {
                        link.scrollIntoView({ block: 'center', behavior: 'smooth', inline: 'nearest' });
                    }, 100);
                }
            } else if (href && currentPath === href) {
                link.classList.add('active');
                activeFound = true;
                const sidebar = link.closest('.nav-sidebar, .sidebar');
                if (sidebar) {
                    setTimeout(() => {
                        link.scrollIntoView({ block: 'center', behavior: 'smooth', inline: 'nearest' });
                    }, 100);
                }
            } else {
                link.classList.remove('active');
            }
        });
        // If no active link found (e.g., on login page), do nothing.
    }

    // ─── Prevent page auto‑scroll on sidebar link clicks ───
    function preventPageAutoScroll() {
        // Save scroll position before navigation
        document.querySelectorAll('.nav-sidebar .nav-link, .sidebar .nav-link').forEach(link => {
            link.addEventListener('click', function() {
                sessionStorage.setItem('scrollY', window.scrollY);
            });
        });
        // Restore scroll position after page load
        window.addEventListener('load', function() {
            const saved = sessionStorage.getItem('scrollY');
            if (saved && parseInt(saved) > 0) {
                window.scrollTo(0, parseInt(saved));
                sessionStorage.removeItem('scrollY');
            }
        });
    }

    // ─── Run on DOM ready ───
    document.addEventListener('DOMContentLoaded', function() {
        highlightActiveLink();
        preventPageAutoScroll();
    });

})();
// This file is minimal; the main logic is in base_site.html.
// It exists only to satisfy the static file reference.
(function() {
  // The logic is already present in base_site.html.
})();