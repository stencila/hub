// These are available as `manager.Toast` etc
export { File } from "@vizuaalog/bulmajs/src/plugins/file";
export { Navbar } from "@vizuaalog/bulmajs/src/plugins/navbar";
export { toast as Toast } from "bulma-toast";
import "./dropdowns";
import { initDropdowns } from "./dropdowns";
// `htmx` is available globally
import "htmx.org";
import "htmx.org/dist/ext/json-enc";
import "htmx.org/dist/ext/include-vals";
import "./htmx-extensions.js";

// =============================================================================
// Modal container logic
// =============================================================================
const openModal = () => {
  const modalTarget = document.querySelector("#modal-target");
  if (modalTarget) {
    modalTarget.classList.add("is-active");
  }
};

const closeModal = () => {
  const modalTarget = document.querySelector("#modal-target");
  if (modalTarget) {
    modalTarget.classList.remove("is-active");
  }
};

const handleModalClose = () => {
  const modalBackground = document.querySelector(".modal-background");
  if (modalBackground) {
    modalBackground.addEventListener("click", () => {
      closeModal();
      // Remove HTMX inserted content
      let nextSibling;
      while(nextSibling = modalBackground.nextElementSibling) {
        nextSibling.remove();
      }
    });
  }
}

// ==============================================================================

/**
 * Wait for document to be ready before calling the callback function.
 * Ensures that page is ready, and all elements present before performing any logic.
 */
const onReady = (cb) => {
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
};

const attachAllEventHandlers = () => {
  initDropdowns();
  handleModalClose()
};

onReady(attachAllEventHandlers);

// =============================================================================
// HTMX Event handlers
// =============================================================================
htmx.on("afterSwap.htmx", (e) => {
  // Activate the modal container when inserteing elements into it
  if (e.detail.target.id.includes("modal-target")) {
    openModal();
  }
});

// Ensure that dynamically added DOM elements have dropdown event handlers
htmx.on("load.htmx", () => {
  attachAllEventHandlers()
});

