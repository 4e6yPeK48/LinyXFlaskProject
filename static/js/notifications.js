document.addEventListener('DOMContentLoaded', function () {
    function showPopup() {
        const popup = document.querySelector('.popup');
        popup.style.display = 'block';

        setTimeout(function () {
            popup.style.display = 'none';
        }, 3000);
    }

    const messages = document.querySelectorAll('.popup');
    if (messages.length > 0) {
        showPopup();
    }
});
