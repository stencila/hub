// These are available as `manager.Toast` etc
export { Navbar } from "@vizuaalog/bulmajs/src/plugins/navbar";
export { toast as Toast } from "bulma-toast";
import "./dropdowns";
import { initDropdowns } from "./dropdowns";
// `htmx` is available globally
import "./htmx";
import "./htmx-extensions.js";

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

onReady(() => {
  initDropdowns();

  // Ensure that dynamically added DOM elements have dropdown event handlers
  htmx.on("afterSwap.htmx", () => {
    initDropdowns();
  });
});
