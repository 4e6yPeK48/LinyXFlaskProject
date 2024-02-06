document.addEventListener("scroll", function () {
    const parallax = document.querySelector(".parallax");
    const scrollPosition = window.scrollY;
    if (parallax) {
        parallax.style.backgroundPositionY = -scrollPosition * 0.5 + "px";
    }
});