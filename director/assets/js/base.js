window.utils = {
  /// Get a query string parameter
  param: function(name) {
    var url = window.location.href;
    name = name.replace(/[\[\]]/g, '\\$&');
    var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, ' '));
  },

  // Get a cookie. Usually used for getting the csrftoken cookie
  // for aysnc fetch requests
  cookie: function(name) {
    var value = "; " + document.cookie
    var parts = value.split("; " + name + "=")
    if (parts.length == 2) return parts.pop().split(";").shift()
  }
}
