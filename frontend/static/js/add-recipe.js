// ================================
// ADD RECIPE FORM
// ================================

const addRecipeForm = document.getElementById("addRecipeForm");

if (addRecipeForm) {
  const formMessage = document.createElement("p");

  formMessage.className = "form-message";
  formMessage.setAttribute("aria-live", "polite");

  addRecipeForm.appendChild(formMessage);

  addRecipeForm.addEventListener("submit", function (event) {
    event.preventDefault();

    formMessage.textContent =
      "Recipe submitted! It will be saved when the Cookly backend is connected.";

    formMessage.classList.add("success");

    addRecipeForm.reset();
  });
}
