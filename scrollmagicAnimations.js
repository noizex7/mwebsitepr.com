// init controller
var controller = new ScrollMagic.Controller();

// create a scene
var scene = new ScrollMagic.Scene({
  triggerElement: '.groguSvg'
})
  .setClassToggle(".groguSvg", "fadeOutAnimation")
  .addTo(controller); // assign the scene to the controller