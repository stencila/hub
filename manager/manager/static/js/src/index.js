// These are available as `manager.Toast` etc
export { File } from "@vizuaalog/bulmajs/src/plugins/file";
export { Navbar } from "@vizuaalog/bulmajs/src/plugins/navbar";
export { toast as Toast } from "bulma-toast";
// `htmx` is available globally
import "htmx.org";
import "htmx.org/dist/ext/include-vals";
import "htmx.org/dist/ext/json-enc";
import "./htmx-extensions.js";

import { initDropdowns } from "./dropdowns";
import { initModals } from "./modals";
import { enrichHTMXButtons } from "./buttons";

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
};

onReady(attachAllEventHandlers);

// =============================================================================
// HTMX Event handlers
// =============================================================================

// Ensure that dynamically added DOM elements have dropdown event handlers
htmx.on("load.htmx", () => {
  attachAllEventHandlers();
});
