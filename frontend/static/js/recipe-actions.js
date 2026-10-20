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
