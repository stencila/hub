/**
 * Converts a <form> to a JSON object.
 *
 * Hat tip to https://www.learnwithjason.dev/blog/get-form-values-as-json/
 *
 * @param  {HTMLFormControlsCollection} form  the form elements
 * @return {Object}                               form data as an object literal
 */
function formToJSON(form) {
  const data = [].reduce.call(
    form,
    (data, element) => {
      // Make sure the element has the required properties and should be added.
      if (
        element.name &&
        element.name !== "csrfmiddlewaretoken" &&
        element.value !== undefined &&
        (!["checkbox", "radio"].includes(element.type) || element.checked)
      ) {
        /*
         * Some fields allow for more than one value, so we need to check if this
         * is one of those fields and, if so, store the values as an array.
         */
        if (element.type === "checkbox") {
          data[element.name] = JSON.parse(element.value);
        } else if (element.options && element.multiple) {
          data[element.name] = element.options.reduce(
            (values, option) =>
              option.selected ? values.concat(option.value) : values,
            []
          );
        } else {
          data[element.name] = element.value;
        }
      }
      return data;
    },
    {}
  );
  return JSON.stringify(data);
}

/**
 * Redirect to another URL.
 *
 * @param {*} form     The form that was submitted
 * @param {*} response The response from the API
 */
function onFormSuccess(form, response, successUrl) {
  if (successUrl === "self") {
    window.location.reload();
  } else if (successUrl !== null) {
    response
      .json()
      .then(json => {
        window.location = successUrl.replace(/\$\{(\w+)\}/g, (match, name) => {
          return json[name];
        });
      })
      .catch(() => {
        window.location = successUrl;
      });
  }
}

/**
 * Display form errors in the form.
 *
 * @param {*} form     The form that was submitted
 * @param {*} response The response from the API
 */
function onFormError(form, response) {
  response.json().then(json => {
    const messages = [json.message || ""];
    if (json.errors) {
      for (const { field, message } of json.errors) {
        const input = form.querySelector(`[name=${field}]`);
        if (input !== null) {
          const help = document.createElement("span");
          help.classList = "help is-danger is-error";
          help.innerText = message;
          input.parentNode.insertBefore(help, input.nextSibling);
        } else {
          messages.push(message);
        }
      }
    }
    if (messages.length) {
      const help = document.createElement("span");
      help.classList = "help is-danger is-error";
      help.innerText = messages.join(" ");
      form.appendChild(help);
    }
  });
}

/**
 * Handle the submission and updating of a form via the API
 *
 * @param {*} isUpdate The form action updates the object
 * @param {*} successUrl The URL to redirect to if successful
 */
function handleForm(isUpdate = false, successUrl = null) {
  const form = document.currentScript.parentElement;
  if (form.tagName !== "FORM")
    throw new Error(
      "handleForm() should be used within a <script>, within a <form>"
    );

  const button = form.querySelector("button[type=submit]");

  if (isUpdate) {
    if (button) {
      button.disabled = true;
      button.classList.add("is-disabled");
    }
    form.addEventListener("change", function() {
      button.disabled = false;
      button.classList.remove("is-disabled");
    });
  }

  form.addEventListener("submit", function(event) {
    event.preventDefault();

    form.querySelectorAll(".is-error").forEach(elem => elem.remove());

    if (button !== null) button.classList.add("is-loading");

    fetch(form.getAttribute("action"), {
      method: form.getAttribute("method"),
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": form.querySelector("[name=csrfmiddlewaretoken]").value
      },
      body: formToJSON(form)
    }).then(response => {
      if (button !== null) {
        button.classList.remove("is-loading");
        if (isUpdate) {
          button.disabled = true;
          button.classList.add("is-disabled");
        }
      }
      if (response.ok) onFormSuccess(form, response, successUrl);
      else onFormError(form, response);
    });

    return false;
  });
}
