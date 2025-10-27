// init controller
var controller = new ScrollMagic.Controller();

// create a scene
var aboutMeSection = document.getElementById('aboutMeSection');

if (aboutMeSection) {
  new ScrollMagic.Scene({
    triggerElement: aboutMeSection,
    triggerHook: 0.6,
    duration: function () {
      return aboutMeSection.offsetHeight;
    }
  })
    .setClassToggle('.groguSvg', 'slideInFromRight')
    .addTo(controller);
}
