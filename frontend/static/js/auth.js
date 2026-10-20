document.addEventListener("DOMContentLoaded", () => {
  const authCard = document.getElementById("authCard");
  const toSignUp = document.getElementById("toSignUp");
  const toSignIn = document.getElementById("toSignIn");

  // ==========================================
  // 1. SLIDING CARD & HASH ROUTING LOGIC
  // ==========================================

  // Sync card position with URL hash (#register vs default login)
  function syncViewWithHash() {
    if (!authCard) return;
    if (window.location.hash === "#register") {
      authCard.classList.add("sign-up-mode");
    } else {
      authCard.classList.remove("sign-up-mode");
    }
  }

  // Run on initial page load and when URL hash changes
  syncViewWithHash();
  window.addEventListener("hashchange", syncViewWithHash);

  // Switch button click triggers
  if (toSignUp) {
    toSignUp.addEventListener("click", () => {
      window.location.hash = "register";
    });
  }

  if (toSignIn) {
    toSignIn.addEventListener("click", () => {
      window.location.hash = "";
    });
  }

  // ==========================================
  // 2. EYE ICON PASSWORD VISIBILITY TOGGLE
  // ==========================================
  const toggleButtons = document.querySelectorAll(".password-toggle");

  toggleButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const targetId = button.getAttribute("data-target");
      const input = document.getElementById(targetId);
      const icon = button.querySelector("i");

      if (input) {
        const isPassword = input.type === "password";
        input.type = isPassword ? "text" : "password";
        icon.className = isPassword ? "bi bi-eye-slash" : "bi bi-eye";
      }
    });
  });

  // ==========================================
  // 3. PASSWORD CONFIRMATION CHECK
  // ==========================================
  const registerForm = document.getElementById("registerForm");
  const messageBox = document.getElementById("registerMessage");

  if (registerForm) {
    registerForm.addEventListener("submit", (e) => {
      const password = document.getElementById("regPassword")?.value;
      const confirmPassword = document.getElementById("confirmPassword")?.value;

      if (password && confirmPassword && password !== confirmPassword) {
        e.preventDefault();
        if (messageBox) {
          messageBox.textContent = "Passwords do not match.";
          messageBox.style.color = "#c95345";
        }
      }
    });
  }
});
