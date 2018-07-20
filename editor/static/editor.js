var app

var project
var checkout
var key
var host
var session

window.addEventListener('load', () => {
  project = substance.getQueryStringParam('project');
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

  // Set the project name
  var projectEl = document.getElementById('project')
  projectEl.innerHTML = project || ''

  // Remove the loading
  var loading = document.getElementById('loading');
  loading.parentNode.removeChild(loading)

  // Save button
  var saveBtn = document.getElementById('save');
  saveBtn.addEventListener('click', () => {
    saveBtn.disabled = true;
    save().then(() => {
      saveBtn.disabled = false;
    })
  })
});

window.addEventListener('beforeunload', () => {
  // Save changes when window closed
  save()
})


function save () {
  return app._save().then(() => {
    fetch(`${checkout}save/`, {
      method: 'POST',
      credentials: 'same-origin'
    })
  })
}
