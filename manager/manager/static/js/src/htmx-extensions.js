/**
 * A custom HTMX extension for doing things we need to do
 */
htmx.defineExtension('stencila', {
  /**
   * Encode parameters as JSON and add XHR headers prior to sending.
   * This is only used for POST, PATCH and PUT requests that have a body.
   * See below for how headers are set for all requests (including GET)
   * 
   * Based on https://github.com/bigskysoftware/htmx/blob/master/src/ext/json-enc.js
   * 
   * - Has the problematic `setRequestHeader` line removed
   *   See https://github.com/bigskysoftware/htmx/issues/74.
   * 
   * - Sets the `X-CSRFToken` header.
   *   See https://docs.djangoproject.com/en/3.0/ref/csrf/#ajax
   */
  encodeParameters : function(xhr, parameters, elt) {
    xhr.overrideMimeType('text/json');

    function getCookie(name) {
      var cookieValue = null;
      if (document.cookie && document.cookie !== '') {
          var cookies = document.cookie.split(';');
          for (var i = 0; i < cookies.length; i++) {
              var cookie = cookies[i].trim();
              if (cookie.substring(0, name.length + 1) === (name + '=')) {
                  cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));

    return JSON.stringify(parameters);
  },
  onEvent : function(name, evt) {
    if (name == 'beforeRequest.htmx') {
      /**
       * This event is triggered before an AJAX request is issued.
       * If the event is cancelled, no request will occur.
       *
       * - Sets the `Accept` header so that we get HTML back from the API
       *   instead of JSON
       * 
       * - Looks for the closest `stencila-template` attribute and sends it as `X-Template`
       *   Akin to https://github.com/bigskysoftware/htmx/blob/master/src/ext/client-side-templates.js
       *   but server-side.
       */
      var xhr = evt.detail.xhr;
      var elt = evt.detail.elt;

      xhr.setRequestHeader("Accept", 'text/html');

      var serverTemplate = htmx.closest(elt, "[hx-template]");
      if (serverTemplate) {
        var templateName = serverTemplate.getAttribute('hx-template');
        xhr.setRequestHeader("X-HX-Template", templateName);
      }

      var extraContent = htmx.closest(elt, "[hx-extra-context]");
      if (extraContent) {
        var extraContentNames = extraContent.getAttribute('hx-extra-context');
        xhr.setRequestHeader("X-HX-Extra-Context", extraContentNames);
      }
    }
    else if (name == 'beforeOnLoad.htmx') {
      // This event is triggered before any new content has been swapped
      // into the DOM.
      var xhr = evt.detail.xhr;
      var elt = evt.detail.elt;
      // If element has a `hx-redirect` attribute then redirect to the
      // location specified for the response status code (defaulting to 200).
      var redirect = htmx.closest(elt, "[hx-redirect]");
      if (redirect) {
        var redirectSpecs = redirect.getAttribute('hx-redirect').split(/\s/);
        for (var index = 0; index < redirectSpecs.length; index++ ){
          var redirectSpec = redirectSpecs[index];
          var redirectUrl;
          var codes = {
            'CREATED': 201,
            'RETRIEVED': 200,
            'UPDATED': 210,
            'DESTROYED': 211,
            'INVALID': 212
          }
          var match = /^(CREATED|RETRIEVED|UPDATED|DESTROYED|INVALID):(.+)/.exec(redirectSpec);
          if (match !== null) {
            var code = codes[match[1]]
            if (xhr.status === code) redirectUrl = match[2];
          } else if (xhr.status === 200) {
            redirectUrl = redirectSpec;
          }
          if (redirectUrl) {
            if (redirectUrl === 'Location') {
              var location = xhr.getResponseHeader("Location");
              window.location.href = location;
            }
            else window.location.href = redirectUrl;
            break;
          }
        }
      }
    }
  }
})
