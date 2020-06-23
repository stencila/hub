/**
 * A custom HTMX extension for doing things we need to do
 */
htmx.defineExtension('stencila', {
  onEvent : function(name, evt) {
    if (name === 'configRequest.htmx') {
      /**
       * This event is triggered after htmx has collected parameters for inclusion in the request.
       * It can be used to include or update the parameters that htmx will send.
       *
       * - Sets the `Accept` header so that we get HTML back from the API
       *   instead of JSON
       * 
       * - Sets the `X-CSRFToken` header.
       *   See https://docs.djangoproject.com/en/3.0/ref/csrf/#ajax
       * 
       * - Looks for the closest `stencila-template` attribute and sends it as `X-Template`
       *   Akin to https://github.com/bigskysoftware/htmx/blob/master/src/ext/client-side-templates.js
       *   but server-side.
       */
      var verb = evt.detail.verb;
      var headers = evt.detail.headers;
      var elt = evt.detail.elt;

      headers['Accept'] = 'text/html';

      if (verb !== "get") {
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
        headers['X-CSRFToken'] = getCookie('csrftoken');
      }

      var serverTemplate = htmx.closest(elt, '[hx-template]');
      if (serverTemplate) {
        var templateName = serverTemplate.getAttribute('hx-template');
        headers['X-HX-Template'] = templateName;
      }

      var extraContent = htmx.closest(elt, '[hx-extra-context]');
      if (extraContent) {
        var extraContentNames = extraContent.getAttribute('hx-extra-context');
        headers['X-HX-Extra-Context'] = extraContentNames;
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
