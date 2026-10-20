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
