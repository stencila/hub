// This is the entry file for custom JS
import { enrichHTMXButtons } from "./buttons";
import { initDropdowns } from "./dropdowns";
import { initModals } from "./modals";
import { readMoreToggle } from "./readMore";

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
  initModals();
  enrichHTMXButtons();
  readMoreToggle()
};

onReady(attachAllEventHandlers);

// =============================================================================
// HTMX Event handlers
// =============================================================================

// Ensure that dynamically added DOM elements have dropdown event handlers
htmx.on("htmx:load", () => {
  attachAllEventHandlers();
});
