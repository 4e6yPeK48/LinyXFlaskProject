const bodyElement = document.querySelector("body");

function updateTheme(isDark) {
    bodyElement.classList.add("toggle");

    setTimeout(() => {
        bodyElement.classList.toggle("dark", isDark);
        bodyElement.classList.toggle("light", !isDark);

        const changeColorElements = document.querySelectorAll(".change-color");
        changeColorElements.forEach(element => {
            element.classList.toggle("btn-outline-dark", !isDark);
            element.classList.toggle("btn-outline-light", isDark);
        });

        setTimeout(() => {
            bodyElement.classList.remove("toggle");
        }, 10);
    }, 5);
    localStorage.setItem('darkMode', isDark);

}

document.addEventListener('DOMContentLoaded', function () {
    const toggleCheckbox = document.querySelector(".day-night input");

    const isDarkMode = localStorage.getItem('darkMode') === 'true';

    window.addEventListener('pageshow', function (event) {
        if (event.persisted || isDarkMode) {
            updateTheme(isDarkMode);
        }
    });

    updateTheme(isDarkMode);

    toggleCheckbox.addEventListener("change", () => {
        const newMode = toggleCheckbox.checked;
        updateTheme(newMode);

        localStorage.setItem('darkMode', newMode);

        const iframe = document.getElementById('productIframe');
        if (iframe) {
            iframe.contentWindow.postMessage({darkMode: newMode}, '*');
        }
    });

});