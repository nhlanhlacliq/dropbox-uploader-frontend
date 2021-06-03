// Utilize Greensock animation plugin
let controller = new ScrollMagic.Controller();
let timeline = new TimelineMax();

// Animations timeline
timeline
    .to('.fg', 3, {y: -420, x: 0})
    .fromTo('.mg', 3, {y:50}, {y: -75, x: 0}, '-=3')
    .fromTo('.bg', 3, {y:-50}, {y: 0, x: 0}, '-=3')
    .to('.cloud1', 3, {y: -400, x: 100}, '-=3')
    .fromTo('.cloud1_2', 3, {y: 0, x: 100}, {y: -450, x: -100}, '-=3')
    .fromTo('.cloud1_3', 3, {y: 10, x: -200}, {y: -140, x: -500}, '-=3')
    .to('.cloud2', 3, {y: -100, x: -140}, '-=3')
    .to('.cloud3', 3, {y: -100, x: 200}, '-=3')
    .to('.cloud-mask', 3, {y: 0, x: 0}, '-=3')
    .to('.content', 3, {top:'0%'}, '-=3')
    .fromTo(".content-images", { opacity: 0 }, { opacity: 1, duration: 1 }, '-=1')
    .fromTo(".text-header", { opacity: 0 }, { opacity: 1, duration: 1 }, '-=1.5')
    .fromTo(".text", { opacity: 0 }, { opacity: 1, duration: 1 }, '-=1');

// Scroll trigger
let scene = new ScrollMagic.Scene({
    triggerElement: "section",
    duration: '200%',
    triggerHook: 0,
})
    .setTween(timeline)
    .setPin("section")
    .addTo(controller);