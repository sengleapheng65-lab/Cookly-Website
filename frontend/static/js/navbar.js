// ================================
// MOBILE NAVIGATION
// ================================

const navbarToggle = document.getElementById("navbarToggle");
const navbarMenu = document.getElementById("navbarMenu");

if (navbarToggle && navbarMenu) {
  const navigationLinks = navbarMenu.querySelectorAll("a");

  function closeMenu() {
    navbarToggle.classList.remove("active");
    navbarMenu.classList.remove("active");
    document.body.classList.remove("menu-open");

    navbarToggle.setAttribute("aria-expanded", "false");
    navbarToggle.setAttribute("aria-label", "Open navigation menu");
  }

  navbarToggle.addEventListener("click", function () {
    navbarToggle.classList.toggle("active");
    navbarMenu.classList.toggle("active");
    document.body.classList.toggle("menu-open");

    const menuIsOpen = navbarMenu.classList.contains("active");

    navbarToggle.setAttribute("aria-expanded", menuIsOpen);
    navbarToggle.setAttribute(
      "aria-label",
      menuIsOpen ? "Close navigation menu" : "Open navigation menu",
    );
  });

  navigationLinks.forEach(function (link) {
    link.addEventListener("click", closeMenu);
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && navbarMenu.classList.contains("active")) {
      closeMenu();
    }
  });

  document.addEventListener("click", function (event) {
    const clickedOutsideMenu =
      !navbarMenu.contains(event.target) &&
      !navbarToggle.contains(event.target);

    if (clickedOutsideMenu && navbarMenu.classList.contains("active")) {
      closeMenu();
    }
  });
}

// Smooth directional slide transition between internal pages.
const savedDirection = sessionStorage.getItem("cookly-nav-direction") || "left";
sessionStorage.removeItem("cookly-nav-direction");
document.body.classList.add(`page-entering-${savedDirection}`);
window.setTimeout(function () {
  document.body.classList.remove("page-entering-left", "page-entering-right");
}, 360);

document.querySelectorAll("a[href]").forEach(function (link) {
  link.addEventListener("click", function (event) {
    const destination = new URL(link.href, window.location.href);
    const isInternalPage =
      destination.origin === window.location.origin &&
      destination.pathname !== window.location.pathname &&
      !link.target &&
      !event.ctrlKey &&
      !event.metaKey &&
      !event.shiftKey &&
      !event.altKey;

    if (!isInternalPage) return;

    event.preventDefault();
    const navigationLinks = Array.from(document.querySelectorAll(".navbar_menu .nav_link"));
    const currentIndex = navigationLinks.findIndex(function (item) {
      return new URL(item.href, window.location.href).pathname === window.location.pathname;
    });
    const clickedIndex = navigationLinks.indexOf(link);
    const direction = currentIndex >= 0 && clickedIndex >= 0 && clickedIndex < currentIndex ? "right" : "left";

    sessionStorage.setItem("cookly-nav-direction", direction);
    document.body.classList.add(`page-exiting-${direction}`);
    window.setTimeout(function () {
      window.location.href = destination.href;
    }, 180);
  });
});
