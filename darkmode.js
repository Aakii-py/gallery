function toggleDarkMode() {
    const htmlTag = document.documentElement;
    if (htmlTag.getAttribute('data-theme') === 'dark') {
        htmlTag.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
    } else {
        htmlTag.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
    }
}

// Load the saved theme
window.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
    }
});
