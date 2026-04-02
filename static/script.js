
const nameRegex = /^[A-Za-z ]{2,}$/;
const emailRegex = /^[\w\.-]+@[\w\.-]+\.\w+$/;
const phoneRegex = /^\d{10}$/;
const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$/;

function showError(message) {
  let el = document.getElementById("formError");
  if (!el) {
    el = document.createElement("div");
    el.id = "formError";
    el.className = "bg-red-100 text-red-700 p-2 rounded mb-4 text-center";
    const card = document.querySelector(".bg-white");
    if (card) card.insertBefore(el, card.firstChild);
  }
  el.textContent = message;
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("signupForm");
  if (!form) return;

  form.addEventListener("submit", (e) => {
    const name = form.elements["name"]?.value?.trim() ?? "";
    const email = form.elements["email"]?.value?.trim() ?? "";
    const phone = form.elements["phone"]?.value?.trim() ?? "";
    const password = form.elements["password"]?.value ?? "";

    if (!nameRegex.test(name)) {
      e.preventDefault();
      showError("Invalid Name");
      return;
    }
    if (!emailRegex.test(email)) {
      e.preventDefault();
      showError("Invalid Email");
      return;
    }
    if (!phoneRegex.test(phone)) {
      e.preventDefault();
      showError("Invalid Phone");
      return;
    }
    if (!passwordRegex.test(password)) {
      e.preventDefault();
      showError("Weak Password");
      return;
    }
  });
});

