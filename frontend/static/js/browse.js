// ================================
// HOME PAGE RECIPE SEARCH
// ================================

const recipeSearch = document.getElementById("recipeSearch");
const searchInput = document.getElementById("searchInput");
const recipeCards = document.querySelectorAll(".recipe-card");

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
      searchMessage.textContent = "";
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

    searchInput.value = link.textContent.trim();
    recipeSearch.requestSubmit();

    const recipeSection = document.querySelector(".popular-recipes-section");

    if (recipeSection) {
      recipeSection.scrollIntoView({ behavior: "smooth" });
    }
  });
});

// ================================
// VIEW ALL RECIPES
// ================================

const viewAllRecipes = document.getElementById("viewAllRecipes");

if (viewAllRecipes && searchInput) {
  viewAllRecipes.addEventListener("click", function (event) {
    event.preventDefault();

    searchInput.value = "";

    recipeCards.forEach(function (card) {
      card.classList.remove("is-hidden");
    });

    const searchMessage = document.querySelector(".search-message");

    if (searchMessage) {
      searchMessage.textContent = "";
    }

    const recipeSection = document.querySelector(".popular-recipes-section");

    if (recipeSection) {
      recipeSection.scrollIntoView({ behavior: "smooth" });
    }
  });
}

// ================================
// ACTIVE HOME NAVIGATION LINK
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

if (pageSections.length > 0) {
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
}
