(function() {
    'use strict';

    // ---- Toast system ----
    function showToast(message, type = 'success') {
        const container = document.getElementById('toast-container') || createToastContainer();
        const toast = document.createElement('div');
        toast.className = `toast-message ${type}`;
        let icon = 'fa-check-circle';
        if (type === 'error') icon = 'fa-exclamation-circle';
        else if (type === 'warning') icon = 'fa-exclamation-triangle';
        else if (type === 'info') icon = 'fa-info-circle';
        toast.innerHTML = `
            <i class="fas ${icon}"></i>
            <span>${message}</span>
            <span class="close-toast">&times;</span>
        `;
        container.appendChild(toast);
        setTimeout(() => { toast.remove(); }, 4000);
        toast.querySelector('.close-toast').addEventListener('click', function() {
            toast.remove();
        });
    }

    function createToastContainer() {
        const div = document.createElement('div');
        div.id = 'toast-container';
        div.className = 'toast-container';
        document.body.appendChild(div);
        return div;
    }

    // ---- Convert Django messages to toasts ----
    function convertMessagesToToasts() {
        const msgContainer = document.getElementById('django-messages');
        if (msgContainer) {
            const msgs = msgContainer.querySelectorAll('ul.messagelist li, .alert');
            msgs.forEach(el => {
                let type = 'success';
                if (el.classList.contains('error') || el.classList.contains('danger')) type = 'error';
                else if (el.classList.contains('warning')) type = 'warning';
                else if (el.classList.contains('info')) type = 'info';
                showToast(el.textContent.trim(), type);
                el.remove();
            });
            if (msgContainer.children.length === 0) msgContainer.remove();
        }
    }

    // ---- Confirm delete ----
    function addConfirmToDelete() {
        document.querySelectorAll('a.deletelink, .deletelink').forEach(link => {
            link.addEventListener('click', function(e) {
                if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                    e.preventDefault();
                }
            });
        });
    }

    // ---- Button feedback ----
    function addButtonFeedback() {
        document.querySelectorAll('.object-tools .addlink, .submit-row input[type="submit"]').forEach(btn => {
            btn.addEventListener('mousedown', function() { this.style.transform = 'scale(0.96)'; });
            btn.addEventListener('mouseup', function() { this.style.transform = 'scale(1)'; });
            btn.addEventListener('mouseleave', function() { this.style.transform = 'scale(1)'; });
        });
    }

    // ---- Run on load ----
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(convertMessagesToToasts, 100);
        addConfirmToDelete();
        addButtonFeedback();

        const urlParams = new URLSearchParams(window.location.search);
        const msg = urlParams.get('message');
        if (msg) {
            showToast(decodeURIComponent(msg), 'success');
            const newUrl = window.location.pathname + window.location.search.replace(/[?&]message=[^&]*/, '').replace(/^&/, '?');
            history.replaceState({}, '', newUrl);
        }
    });

})();