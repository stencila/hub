// Get a cookie. Usually used for getting the csrftoken cookie
// for aysnc fetch requests
function cookie(name) {
  var value = "; " + document.cookie
  var parts = value.split("; " + name + "=")
  if (parts.length == 2) return parts.pop().split(";").shift()
}
