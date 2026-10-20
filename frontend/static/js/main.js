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

// ================================
// SAVE RECIPE BUTTONS
// ================================

const saveButtons = document.querySelectorAll(".save-recipe");

saveButtons.forEach(function (button) {
  button.addEventListener("click", function () {
    const icon = button.querySelector("i");
    const recipeCard = button.closest(".recipe-card");

    const isSaved = button.classList.toggle("saved");

    button.setAttribute("aria-pressed", isSaved);

    if (isSaved) {
      icon.classList.remove("bi-heart");
      icon.classList.add("bi-heart-fill");

      recipeCard.classList.add("recipe-saved");
    } else {
      icon.classList.remove("bi-heart-fill");
      icon.classList.add("bi-heart");

      recipeCard.classList.remove("recipe-saved");
    }
  });
});
