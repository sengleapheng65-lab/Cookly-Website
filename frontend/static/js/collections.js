// ================================
// COLLECTIONS PAGE TABS
// ================================

const collectionTabs = document.querySelectorAll(".collection-tab");
const collectionEmptyIcon = document.getElementById("collectionEmptyIcon");
const collectionEmptyTitle = document.getElementById("collectionEmptyTitle");
const collectionEmptyText = document.getElementById("collectionEmptyText");
const collectionEmptyLink = document.getElementById("collectionEmptyLink");

collectionTabs.forEach(function (tab) {
  tab.addEventListener("click", function () {
    const collectionType = tab.dataset.collection;

    collectionTabs.forEach(function (otherTab) {
      otherTab.classList.remove("active");
    });

    tab.classList.add("active");

    if (collectionType === "created") {
      collectionEmptyIcon.innerHTML =
        '<i class="bi bi-journal-plus" aria-hidden="true"></i>';

      collectionEmptyTitle.textContent = "No recipes created yet";

      collectionEmptyText.textContent =
        "Share your first recipe with the Cookly community.";

      collectionEmptyLink.href = "add-recipe.html";

      collectionEmptyLink.innerHTML =
        'Add a recipe <i class="bi bi-arrow-right" aria-hidden="true"></i>';
    } else {
      collectionEmptyIcon.innerHTML =
        '<i class="bi bi-heart" aria-hidden="true"></i>';

      collectionEmptyTitle.textContent = "No saved recipes yet";

      collectionEmptyText.textContent =
        "When you find a recipe you love, save it and it will appear here.";

      collectionEmptyLink.href = "browse.html";

      collectionEmptyLink.innerHTML =
        'Explore recipes <i class="bi bi-arrow-right" aria-hidden="true"></i>';
    }
  });
});
