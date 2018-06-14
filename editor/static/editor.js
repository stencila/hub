window.addEventListener('load', () => {
  // Mount the app
  substance.substanceGlobals.DEBUG_RENDERING = substance.platform.devtools;
  stencila.StencilaWebApp.mount({
    archiveId: substance.getQueryStringParam('project') + '.dar',
    storageType: 'fs',
    storageUrl: '/storage'
  }, window.document.body);

  // Remove the loading
  var loading = document.getElementById('loading');
  loading.parentNode.removeChild(loading)
});
