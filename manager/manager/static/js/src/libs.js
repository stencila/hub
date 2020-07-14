// Third-party JS which is unlikely to change frequently and can be cached for longer periods of time
// These are available as `manager.Toast` etc
export { File } from "@vizuaalog/bulmajs/src/plugins/file";
export { Navbar } from "@vizuaalog/bulmajs/src/plugins/navbar";
export { toast as Toast } from "bulma-toast";
// `htmx` is available globally
import "htmx.org";
import "htmx.org/dist/ext/include-vals";
import "htmx.org/dist/ext/json-enc";
import "./htmx-extensions.js";
