// This is a simple attempt to handle Javascript errors in the `@stencila/components` package
// when reading an executable document.
// The handler attempts to reload the article once, showing a message to the user, and raising an
// exception for error reporting, if it continues to fail.

const reloadSessionKey = "DOCUMENT_RELOAD_ATTEMPTED";
let reloadAttempted;
try {
  reloadAttempted = window.sessionStorage.getItem(reloadSessionKey) === "true";
} catch {
  reloadAttempted = true;
}

// Attempt to reload the document once
const tryAgain = () => {
  window.sessionStorage.setItem(reloadSessionKey, "true");
  window.location.reload();
};

// If the components fail to initialize after reloading the document, show an alert message to the reader
let alertShown = false;
const showAlert = () => {
  window.sessionStorage.removeItem(reloadSessionKey);
  if (!alertShown) {
    alertShown = true;
    alert(
      "Unfortunately we are having problems loading the document. Please try visiting this page from different browser."
    );

    // throw a custom error to track in Sentry
    throw new Error("Article initialization failed after reload");
  }
};

// Multiple errors can occur on a single page load.
// This prevents the error handling logic from running for each error.
let errorHandled = false;

const handleError = () => {
  if (!errorHandled) {
    errorHandled = true;
    if (reloadAttempted) {
      showAlert();
    } else {
      tryAgain();
    }
  }
};

window.addEventListener("unhandledrejection", (err) => {
  if (
    typeof err.reason.fileName === "string" &&
    err.reason.fileName.includes("/dist/stencila-components/")
  ) {
    handleError();
  }
});
