/**
 * A custom HTMX extension for doing things we need to do
 */
htmx.defineExtension('stencila', {
  /**
   * Encode parameters as JSON
   * 
   * Based on https://github.com/bigskysoftware/htmx/blob/master/src/ext/json-enc.js
   * 
   * - Has the problematic `setRequestHeader` line removed
   *   See https://github.com/bigskysoftware/htmx/issues/74.
   * 
   * - Sets the `X-CSRFToken` header.
   *   See https://docs.djangoproject.com/en/3.0/ref/csrf/#ajax
   * 
   * - Sets the `Accept` header so that we get HTML back from the API
   *   instead of JSON
   * 
   * - Looks for the closest `stencila-template` attribute and sends it as `X-Template`
   *   Akin to https://github.com/bigskysoftware/htmx/blob/master/src/ext/client-side-templates.js
   *   but server-side.
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

    xhr.setRequestHeader("Accept", 'text/html');

    var stencilaTemplate = htmx.closest(elt, "[stencila-template]");
    if (stencilaTemplate) {
      var templateName = stencilaTemplate.getAttribute('stencila-template');
      xhr.setRequestHeader("X-Template", templateName);
    }

    return JSON.stringify(parameters);
  }
})
