var PATH = '/desktop'

var app

window.addEventListener('load', () => {
  // The path of the Dar to edit
  var path = substance.getQueryStringParam('path') || 'default/main.dar';
  // The URL of the execution session to use
  var session = substance.getQueryStringParam('session');

  // If a session is provided then connect to it
  if (session) {
    window.STENCILA_HOSTS = session;
  }

  // Set the path in the top bar
  var pathEl = document.getElementById('path')
  pathEl.innerHTML = path


  // Initialize the editor session
  fetch(PATH + '/init/' + path).then(response => {
    return response.text()
  }).then(dar => {
    // Mount the app
    substance.substanceGlobals.DEBUG_RENDERING = substance.platform.devtools;
    app = stencila.StencilaWebApp.mount({
      archiveId: dar,
      storageType: 'fs',
      storageUrl: PATH + '/dars'
    }, window.document.body);

    // Remove the loading
    var loading = document.getElementById('loading');
    loading.parentNode.removeChild(loading)

    // Initialize the save button
    var saveBtn = document.getElementById('save');
    saveBtn.addEventListener('click', () => {
      saveBtn.disabled = true;
      app._save().then(() => {
        saveBtn.disabled = false;
      })
    })
  })

});

window.addEventListener('beforeunload', () => {
  // Save changes when window is closed
  app._save();
})
