import { createPopper } from "@popperjs/core";

const attachDropdownHandlers = (dropdown) => {
  const trigger =
    dropdown.querySelector(".dropdown-trigger") || dropdown.querySelector("a");
  const targetEl =
    dropdown.querySelector(".dropdown-menu") ||
    dropdown.querySelector(".navbar-dropdown");

  if (!trigger || !targetEl) return

  let popperInstance = null;
  let destroyTimeout = null;

  const create = (placement) => {
    popperInstance = createPopper(trigger, targetEl, {
      placement: placement || "bottom-start",
      modifiers: [
        {
          name: "preventOverflow",
        },
        {
          name: "flip",
        },
      ],
    });
  };

  const destroy = () => {
    if (popperInstance) {
      popperInstance.destroy();
      popperInstance = null;
    }
  };

  const cancelDestruction = () => {
    window.clearTimeout(destroyTimeout);
  };

  const show = () => {
    dropdown.classList.add("is-active");
    const placement = dropdown.getAttribute("data-placement");
    create(placement);
  };

  const hide = () => {
    destroyTimeout = window.setTimeout(() => {
      dropdown.classList.remove("is-active");
      destroy();
    }, 100);
  };

  const showEvents = ["click", "mouseenter", "focus"];
  const hideEvents = ["mouseleave", "blur"];

  showEvents.forEach((event) => {
    trigger.addEventListener(event, show);
    targetEl.addEventListener(event, cancelDestruction);
    dropdown.setAttribute("data-dropdown-hydrated", "true");
  });

  hideEvents.forEach((event) => {
    dropdown.addEventListener(event, hide);
  });
};

/**
 * Find dropdown elements in the document and attach event handlers to them.
 * This is done using JavaScript to ensure that the dropdowns are not go outside the viewport.
 * After the handlers are attached, a `data-dropdown-hydrated="true"` attribute is set. This allows us to run the
 * function multiple times without creating duplicate event listeners.
 *
 * By default the dropdown will be placed below the trigger element, and will try to align the left edges. You can
 * override the dropdown position by setting a `data-placement` attribute with one of the values found at the following
 * link https://popper.js.org/docs/v2/constructors/#options
 */
export const initDropdowns = () => {
  document
    .querySelectorAll(
      ".has-dropdown:not([data-dropdown-hydrated]), .dropdown:not([data-dropdown-hydrated])"
    )
    .forEach(attachDropdownHandlers);
};
