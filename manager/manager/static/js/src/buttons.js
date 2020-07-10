// Improve feedback UX for async interactions with HTMX buttons by showing a spinner on user click.
const findHTMXButtons = () =>
  document.querySelectorAll(`
    .button[hx-delete],
    .button[hx-get],
    .button[hx-patch],
    .button[hx-post],
    .button[hx-put]
`);

const attachClickHandler = (button) => {
  button.addEventListener("click", () => {
    button.classList.add("is-loading");
  });
};

// Form event handlers need to account for native browser validation which short-circuits the event logic,
// preventing HTMX events from ever firing.
const findForms = () =>
  document.querySelectorAll(`
    form[hx-delete],
    form[hx-get],
    form[hx-patch],
    form[hx-post],
    form[hx-put],
    form[action]
`);

const attachFormHandlers = (formEl) => {
  const submitButton = formEl.querySelector('button[type="submit"]');
  formEl.querySelectorAll("input").forEach((input) => {
    input.oninvalid = () => {
      // Add a delay before resetting the button to communicate to the user that the form is indeed working
      window.setTimeout(() => submitButton.classList.remove("is-loading"), 500);
    };
  });

  attachClickHandler(submitButton);
};

/**
 * Find all buttons on the current page and attach handlers to show a spinner when clicking on the button or submitting
 * a form.
 */
export const enrichHTMXButtons = () => {
  findHTMXButtons().forEach(attachClickHandler);
  findForms().forEach(attachFormHandlers);

  // Remove `loading` state from buttons after a request has been completed.
  htmx.on("htmx:afterRequest", (e) => {
    if (e.target instanceof HTMLButtonElement) {
      e.target.classList.remove("is-loading");
    } else if (e.target instanceof HTMLFormElement) {
      const button = document.querySelector("button.is-loading");
      if (button) button.classList.remove("is-loading");
    }
  });
};
