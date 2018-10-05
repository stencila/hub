var app

var project
var checkout
var dar
var host
var session

const PATH = '/edit/textilla'

window.addEventListener('load', () => {
  project = substance.getQueryStringParam('project') || '';
  checkout = substance.getQueryStringParam('checkout');
  dar = substance.getQueryStringParam('dar') || 'default';
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
    archiveId: dar,
    storageType: 'fs',
    storageUrl: `${PATH}/dars`
  }, window.document.body);

  // Set the project name
  var projectEl = document.getElementById('project')
  projectEl.innerHTML = project

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

  // Close button
  var closeBtn = document.getElementById('close');
  closeBtn.addEventListener('click', () => {
    closeBtn.disabled = true;
    close().then(() => {
      // Redirect page to the host
      // window.close() does not actually close the tab (on Chrome at least)
      window.location = window.location.origin
    })
  })
});

window.addEventListener('beforeunload', () => {
  // Save changes when window closed
  close()
})


function save () {
  return app._save().then(() => {
    fetch(`${checkout}save/`, {
      method: 'POST',
      credentials: 'same-origin',
      mode: 'no-cors'
    })
  })
}

function close () {
  return app._save().then(() => {
    fetch(`${checkout}close/`, {
      method: 'POST',
      credentials: 'same-origin',
      mode: 'no-cors'
    })
  })
}
