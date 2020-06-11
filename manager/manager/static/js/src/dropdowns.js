import { createPopper } from "@popperjs/core";

const attachDropdownHandlers = (dropdown) => {
  const trigger = dropdown.querySelector('.dropdown-trigger') || dropdown.querySelector("a");
  const targetEl = dropdown.querySelector('.dropdown-menu') || dropdown.querySelector(".navbar-dropdown");

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
    window.clearTimeout(destroyTimeout)
  }

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

  const showEvents = ["mouseenter", "focus"];
  const hideEvents = ["mouseleave", "blur"];

  showEvents.forEach((event) => {
    trigger.addEventListener(event, show);
  });

  showEvents.forEach((event) => {
    targetEl.addEventListener(event, cancelDestruction);
  });

  hideEvents.forEach((event) => {
    dropdown.addEventListener(event, hide);
  });
}

export const ready = (cb) => {
  // see if DOM is already available
  if (
    document.readyState === "complete" ||
    document.readyState === "interactive"
  ) {
    // call on next available tick
    setTimeout(cb, 1);
  } else {
    document.addEventListener("DOMContentLoaded", cb);
  }
}


ready(() => {
  const dropdowns = document.querySelectorAll('.has-dropdown, .dropdown')
  dropdowns.forEach(attachDropdownHandlers)
});
