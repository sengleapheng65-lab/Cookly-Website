const collectionTabs = document.querySelectorAll(".collection-tab");
const savedCollection = document.getElementById("savedCollection");
const createdCollection = document.getElementById("createdCollection");

collectionTabs.forEach(function (tab) {
  tab.addEventListener("click", function () {
    const showCreated = tab.dataset.collection === "created";

    collectionTabs.forEach(function (otherTab) {
      otherTab.classList.remove("active");
    });

    tab.classList.add("active");
    savedCollection.hidden = showCreated;
    createdCollection.hidden = !showCreated;
  });
});
