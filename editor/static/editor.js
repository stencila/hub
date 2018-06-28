window.addEventListener('load', () => {
  var project = substance.getQueryStringParam('project');
  var checkout = substance.getQueryStringParam('checkout');
  var host = substance.getQueryStringParam('host');
  var session = substance.getQueryStringParam('session');
  
  // If a session is provided then connect firectly to that host
  // otherwise use the top level v0 API to create a new session
  if (session) {
    window.STENCILA_HOSTS = `${host}/v1/sessions!/${session}`;
  } else {
    window.STENCILA_HOSTS = `${host}/v0`;
  }

  // Mount the app
  substance.substanceGlobals.DEBUG_RENDERING = substance.platform.devtools;
  var app = stencila.StencilaWebApp.mount({
    archiveId: checkout + '.dar',
    storageType: 'fs',
    storageUrl: '/edit/storage'
  }, window.document.body);

  // Remove the loading
  var loading = document.getElementById('loading');
  loading.parentNode.removeChild(loading)

  // Commit button
  var commit = document.getElementById('commit');
  commit.addEventListener('click', () => {
    commit.disabled = true;
    app._save().then(() => {
      fetch(`/checkouts/${checkout}/commit`, {
        credentials: 'same-origin'
      }).then(() => {
        commit.disabled = false;
      })
    })
  })
});

window.addEventListener('beforeunload', () => {
  // If a session was provided then ask for it to be destroyed
  // when leaving the page
  var session = substance.getQueryStringParam('session');
  if (session) {
    fetch(`${host}/v1/sessions/${session}`, {
      method: 'DELETE',
      credentials: 'same-origin'
    })
  }
})
