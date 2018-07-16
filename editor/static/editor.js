var app

var checkout
var key
var host
var session

window.addEventListener('load', () => {
  checkout = substance.getQueryStringParam('checkout');
  key = substance.getQueryStringParam('key');
  host = substance.getQueryStringParam('host');
  session = substance.getQueryStringParam('session');

  // If a session is provided then connect directly to that host
  // otherwise use the top level v0 API to create a new session
  if (host && session) {
    window.STENCILA_HOSTS = `${host}/v1/sessions!/${session}`;
  } else if (host) {
    window.STENCILA_HOSTS = `${host}/v0`;
  }

  // Mount the app
  substance.substanceGlobals.DEBUG_RENDERING = substance.platform.devtools;
  app = stencila.StencilaWebApp.mount({
    archiveId: key,
    storageType: 'fs',
    storageUrl: '/edit/storage'
  }, window.document.body);

  // Remove the loading
  var loading = document.getElementById('loading');
  loading.parentNode.removeChild(loading)

  // Commit button
  var commitBtn = document.getElementById('commit');
  commitBtn.addEventListener('click', () => {
    commitBtn.disabled = true;
    commit().then(() => {
      commitBtn.disabled = false;
    })
  })
});

window.addEventListener('beforeunload', () => {
  // Commit changes when window closed
  commit()
})


function commit () {
  return app._save().then(() => {
    fetch(`/checkouts/${checkout}/save/`, {
      method: 'POST',
      credentials: 'same-origin'
    })
  })
}
