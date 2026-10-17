const navbarToggle = document.getElementById("navbarToggle");
const navbarMenu = document.getElementById("navbarMenu");
const navigationLinks = navbarMenu.querySelectorAll("a");

navbarToggle.addEventListener("click", function () {
  navbarToggle.classList.toggle("active");
  navbarMenu.classList.toggle("active");
  document.body.classList.toggle("menu-open");

  const menuIsOpen = navbarMenu.classList.contains("active");

  navbarToggle.setAttribute("aria-expanded", menuIsOpen);

  if (menuIsOpen) {
    navbarToggle.setAttribute("aria-label", "Close navigation menu");
  } else {
    navbarToggle.setAttribute("aria-label", "Open navigation menu");
  }
});

/* Close the menu when a navigation link is selected */

navigationLinks.forEach(function (link) {
  link.addEventListener("click", function () {
    navbarToggle.classList.remove("active");
    navbarMenu.classList.remove("active");
    document.body.classList.remove("menu-open");

    navbarToggle.setAttribute("aria-expanded", "false");
    navbarToggle.setAttribute("aria-label", "Open navigation menu");
  });
});

/* Prevent the temporary search form from refreshing the page */

const recipeSearch = document.getElementById("recipeSearch");

recipeSearch.addEventListener("submit", function (event) {
  event.preventDefault();
});
