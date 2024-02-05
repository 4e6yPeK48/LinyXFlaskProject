console.clear();

gsap.registerPlugin(ScrollTrigger, ScrollToPlugin);

const sections = document.querySelectorAll(".section");

const scrolling = {
    enabled: true,
    events: "scroll,wheel,touchmove,pointermove".split(","),
    prevent: e => e.preventDefault(),
    disable() {
        if (scrolling.enabled) {
            scrolling.enabled = false;
            window.addEventListener("scroll", gsap.ticker.tick, {passive: true});
            scrolling.events.forEach((e, i) => (i ? document : window).addEventListener(e, scrolling.prevent, {passive: false}));
        }
    },
    enable() {
        if (!scrolling.enabled) {
            scrolling.enabled = true;
            window.removeEventListener("scroll", gsap.ticker.tick);
            scrolling.events.forEach((e, i) => (i ? document : window).removeEventListener(e, scrolling.prevent));
        }
    }
};


function goToSection(section, anim, _) {
    if (scrolling.enabled) {
        scrolling.disable();
        gsap.to(window, {
            scrollTo: {y: section, autoKill: false},
            onComplete: scrolling.enable,
            duration: 1
        });

        anim && anim.restart();
    }
}

sections.forEach((section, _) => {
    const intoAnim = gsap.from(section.querySelector(".section"), {yPercent: 50, duration: 1, paused: true});

    ScrollTrigger.create({
        trigger: section,
        start: "top bottom-=1",
        end: "bottom top+=1",
        onEnter: () => goToSection(section, intoAnim),
        onEnterBack: () => goToSection(section)
    });
});