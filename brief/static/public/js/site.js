(function () {
  var toggle = document.querySelector("[data-nav-toggle]");
  var nav = document.getElementById("site-nav");
  if (!toggle || !nav) {
    return;
  }

  var desktopQuery = window.matchMedia("(min-width: 48rem)");

  function setOpen(isOpen) {
    if (desktopQuery.matches) {
      toggle.setAttribute("aria-expanded", "false");
      nav.classList.remove("is-open");
      return;
    }
    toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    nav.classList.toggle("is-open", isOpen);
  }

  toggle.addEventListener("click", function () {
    var isOpen = toggle.getAttribute("aria-expanded") === "true";
    setOpen(!isOpen);
  });

  nav.addEventListener("click", function (event) {
    if (event.target instanceof HTMLAnchorElement && !desktopQuery.matches) {
      setOpen(false);
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      setOpen(false);
    }
  });

  desktopQuery.addEventListener("change", function () {
    setOpen(false);
  });
})();
