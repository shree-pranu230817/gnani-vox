/**
 * UZHAVAR AI - Main Client JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {
    // Mobile Navigation Toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', function () {
            navLinks.classList.toggle('open');
        });
    }

    // Language Dropdown Toggle
    const langBtn = document.querySelector('.lang-btn');
    const langMenu = document.querySelector('.lang-dropdown-menu');
    if (langBtn && langMenu) {
        langBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            langMenu.classList.toggle('show');
        });

        document.addEventListener('click', function () {
            langMenu.classList.remove('show');
        });
    }

    // Dismissible Flash Alerts
    const alertCloses = document.querySelectorAll('.alert-close');
    alertCloses.forEach(btn => {
        btn.addEventListener('click', function () {
            const alert = this.closest('.alert');
            if (alert) {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 250);
            }
        });
    });
});
