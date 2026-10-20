// ================================
// MOBILE NAVIGATION
// ================================

const navbarToggle = document.getElementById("navbarToggle");
const navbarMenu = document.getElementById("navbarMenu");

if (navbarToggle && navbarMenu) {
  const navigationLinks = navbarMenu.querySelectorAll("a");

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

  // Close the menu when a link is selected
  navigationLinks.forEach(function (link) {
    link.addEventListener("click", function () {
      navbarToggle.classList.remove("active");
      navbarMenu.classList.remove("active");
      document.body.classList.remove("menu-open");

      navbarToggle.setAttribute("aria-expanded", "false");
      navbarToggle.setAttribute("aria-label", "Open navigation menu");
    });
  });

  // Close the menu with the Escape key
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && navbarMenu.classList.contains("active")) {
      navbarToggle.classList.remove("active");
      navbarMenu.classList.remove("active");
      document.body.classList.remove("menu-open");

      navbarToggle.setAttribute("aria-expanded", "false");
      navbarToggle.setAttribute("aria-label", "Open navigation menu");
    }
  });

  // Close the menu when clicking outside it
  document.addEventListener("click", function (event) {
    const clickedOutsideMenu =
      !navbarMenu.contains(event.target) &&
      !navbarToggle.contains(event.target);

    if (clickedOutsideMenu && navbarMenu.classList.contains("active")) {
      navbarToggle.classList.remove("active");
      navbarMenu.classList.remove("active");
      document.body.classList.remove("menu-open");

      navbarToggle.setAttribute("aria-expanded", "false");
      navbarToggle.setAttribute("aria-label", "Open navigation menu");
    }
  });
}

// ================================
// RECIPE ELEMENTS
// ================================

const recipeSearch = document.getElementById("recipeSearch");
const searchInput = document.getElementById("searchInput");
const recipeCards = document.querySelectorAll(".recipe-card");

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

// ================================
// RECIPE SEARCH
// ================================

if (recipeSearch && searchInput && recipeCards.length > 0) {
  const searchMessage = document.createElement("p");

  searchMessage.className = "search-message";
  searchMessage.setAttribute("aria-live", "polite");

  recipeSearch.insertAdjacentElement("afterend", searchMessage);

  recipeSearch.addEventListener("submit", function (event) {
    event.preventDefault();

    const searchTerm = searchInput.value.trim().toLowerCase();
    let visibleRecipes = 0;

    recipeCards.forEach(function (card) {
      const recipeName = card.querySelector("h3").textContent.toLowerCase();

      const recipeCategory = card
        .querySelector(".recipe-category")
        .textContent.toLowerCase();

      const matchesSearch =
        searchTerm === "" ||
        recipeName.includes(searchTerm) ||
        recipeCategory.includes(searchTerm);

      card.classList.toggle("is-hidden", !matchesSearch);

      if (matchesSearch) {
        visibleRecipes++;
      }
    });

    if (searchTerm === "") {
      searchMessage.textContent = "";
    } else if (visibleRecipes === 0) {
      searchMessage.textContent =
        "No recipes found. Try pasta, healthy, or dinner.";
    } else {
      searchMessage.textContent = `${visibleRecipes} recipe${visibleRecipes === 1 ? "" : "s"} found.`;
    }
  });
}

// ================================
// POPULAR SEARCH TAGS
// ================================

const popularSearchLinks = document.querySelectorAll(".popular-searches a");

popularSearchLinks.forEach(function (link) {
  link.addEventListener("click", function (event) {
    event.preventDefault();

    if (!recipeSearch || !searchInput) {
      return;
    }

    // Put the selected word into the search input
    searchInput.value = link.textContent.trim();

    // Run the existing recipe search
    recipeSearch.requestSubmit();

    // Move the visitor to the filtered recipe cards
    document.querySelector(".popular-recipes-section").scrollIntoView({
      behavior: "smooth",
    });
  });
});

// ================================
// VIEW ALL RECIPES
// ================================

const viewAllRecipes = document.getElementById("viewAllRecipes");

if (viewAllRecipes) {
  viewAllRecipes.addEventListener("click", function (event) {
    event.preventDefault();

    // Clear the search input
    searchInput.value = "";

    // Show every recipe card again
    recipeCards.forEach(function (card) {
      card.classList.remove("is-hidden");
    });

    // Clear any search message
    const searchMessage = document.querySelector(".search-message");

    if (searchMessage) {
      searchMessage.textContent = "";
    }

    // Scroll to the recipe section
    document.querySelector(".popular-recipes-section").scrollIntoView({
      behavior: "smooth",
    });
  });
}

// ================================
// ACTIVE NAVIGATION LINK ON SCROLL
// ================================

const navSectionLinks = Array.from(
  document.querySelectorAll('.nav_link[href^="#"]'),
).filter(function (link) {
  return link.getAttribute("href") !== "#";
});

const pageSections = navSectionLinks
  .map(function (link) {
    return document.querySelector(link.getAttribute("href"));
  })
  .filter(Boolean);

const sectionObserver = new IntersectionObserver(
  function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) {
        return;
      }

      navSectionLinks.forEach(function (link) {
        link.classList.remove("active");
      });

      const matchingLink = document.querySelector(
        `.nav_link[href="#${entry.target.id}"]`,
      );

      if (matchingLink) {
        matchingLink.classList.add("active");
      }
    });
  },
  {
    rootMargin: "-35% 0px -55% 0px",
    threshold: 0,
  },
);

pageSections.forEach(function (section) {
  sectionObserver.observe(section);
});

// ================================
// BROWSE PAGE SEARCH AND FILTERS
// ================================

const browseSearchForm = document.querySelector(".browse-search-form");
const browseSearchInput = document.querySelector(".browse-search-form input");
const browseRecipeCards = document.querySelectorAll(
  ".browse-results-section .recipe-card",
);
const filterButtons = document.querySelectorAll(".recipe-filter");
const browseEmptyMessage = document.getElementById("browseEmptyMessage");

let selectedFilter = "all";

function filterBrowseRecipes() {
  const searchTerm = browseSearchInput.value.trim().toLowerCase();
  let visibleRecipes = 0;

  browseRecipeCards.forEach(function (card) {
    const recipeName = card.querySelector("h3").textContent.toLowerCase();
    const recipeCategory = card.dataset.category;

    const matchesSearch =
      recipeName.includes(searchTerm) || recipeCategory.includes(searchTerm);

    const matchesFilter =
      selectedFilter === "all" || recipeCategory === selectedFilter;

    const shouldShow = matchesFilter && (searchTerm === "" || matchesSearch);

    card.classList.toggle("is-hidden", !shouldShow);

    if (shouldShow) {
      visibleRecipes++;
    }
  });

  if (browseEmptyMessage) {
    browseEmptyMessage.hidden = visibleRecipes > 0;
  }
}

if (browseSearchForm && browseSearchInput) {
  browseSearchForm.addEventListener("submit", function (event) {
    event.preventDefault();
    filterBrowseRecipes();
  });
}

filterButtons.forEach(function (button) {
  button.addEventListener("click", function () {
    selectedFilter = button.dataset.filter;

    filterButtons.forEach(function (filterButton) {
      filterButton.classList.remove("active");
    });

    button.classList.add("active");
    filterBrowseRecipes();
  });
});

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
