// SAVE / FAVORITE RECIPE BUTTONS
const saveForms = document.querySelectorAll(".save-form");

saveForms.forEach(function (form) {
  form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const button = form.querySelector(".save-recipe");
    const icon = button.querySelector("i");
    const card = form.closest(".recipe-card, .detail-card");
    const wasSaved = form.dataset.saved === "true";
    const nextSaved = !wasSaved;
    const nextAction = wasSaved ? "/unsave" : "/save";
    const baseAction = form.action.replace(/\/(?:save|unsave)$/, "");

    button.disabled = true;

    try {
      const response = await fetch(baseAction + nextAction, {
        method: "POST",
        credentials: "same-origin",
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });

      if (!response.ok) throw new Error("Unable to update favorite");

      form.dataset.saved = String(nextSaved);
      button.classList.toggle("saved", nextSaved);
      button.setAttribute("aria-pressed", String(nextSaved));
      button.setAttribute("aria-label", nextSaved ? "Remove from favorites" : "Add to favorites");
      icon.classList.toggle("bi-heart-fill", nextSaved);
      icon.classList.toggle("bi-heart", !nextSaved);
      card.classList.toggle("recipe-saved", nextSaved);
    } catch (error) {
      console.error(error);
    } finally {
      button.disabled = false;
    }
  });
});

// LIKE RECIPE BUTTONS
const likeForms = document.querySelectorAll(".like-form");

likeForms.forEach(function (form) {
  form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const button = form.querySelector(".like-recipe");
    const icon = button.querySelector("i");
    const card = form.closest(".recipe-card, .detail-card");
    const count = card.querySelector(".like-count-value");
    const wasLiked = form.dataset.liked === "true";
    const nextLiked = !wasLiked;
    const nextAction = wasLiked ? "/unlike" : "/like";
    const baseAction = form.action.replace(/\/(?:like|unlike)$/, "");

    button.disabled = true;

    try {
      const response = await fetch(baseAction + nextAction, {
        method: "POST",
        credentials: "same-origin",
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });

      if (!response.ok) throw new Error("Unable to update like");

      form.dataset.liked = String(nextLiked);
      button.classList.toggle("liked", nextLiked);
      button.setAttribute("aria-pressed", String(nextLiked));
      button.setAttribute("aria-label", nextLiked ? "Unlike recipe" : "Like recipe");
      icon.classList.toggle("bi-hand-thumbs-up-fill", nextLiked);
      icon.classList.toggle("bi-hand-thumbs-up", !nextLiked);
      count.textContent = String(Math.max(0, Number(count.textContent) + (nextLiked ? 1 : -1)));
    } catch (error) {
      console.error(error);
    } finally {
      button.disabled = false;
    }
  });
});

// ADD COMMENT WITHOUT RELOADING THE RECIPE PAGE
const commentForms = document.querySelectorAll(".comment-form");

commentForms.forEach(function (form) {
  form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const submitButton = form.querySelector("button[type='submit']");
    const textarea = form.querySelector("textarea");
    const list = document.querySelector("#commentList");
    const count = document.querySelector(".comment-count-value");
    submitButton.disabled = true;

    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        credentials: "same-origin",
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      if (!response.ok) throw new Error("Unable to add comment");

      const data = await response.json();
      const emptyMessage = list.querySelector(".comment-login");
      if (emptyMessage) emptyMessage.remove();

      const comment = document.createElement("article");
      comment.className = "comment";
      comment.innerHTML = `
        <a class="comment-avatar" href="/users/${data.user_id}" aria-label="View profile"></a>
        <div>
          <div class="comment-header"><a class="comment-author" href="/users/${data.user_id}"></a><time>Just now</time></div>
          <p class="comment-body"></p>
        </div>`;
      comment.querySelector(".comment-author").textContent = data.author_name;
      comment.querySelector(".comment-avatar").textContent = data.author_name.slice(0, 1).toUpperCase();
      comment.querySelector(".comment-body").textContent = data.body;
      list.prepend(comment);
      count.textContent = String(Number(count.textContent) + 1);
      textarea.value = "";
    } catch (error) {
      console.error(error);
    } finally {
      submitButton.disabled = false;
    }
  });
});
