class App extends substance.Component {

  didMount() {
    let storage = new substance.HttpStorageClient(window.STENCILA_STORAGE);
    let buffer = new substance.InMemoryDarBuffer();
    let archive = new stencila.StencilaArchive(storage, buffer);
    archive.load(window.STENCILA_PROJECT).then(() => {
      return stencila.setupStencilaContext(archive)
    }).then(({host, functionManager, engine}) => {
      window.host = host
      this.setState({archive, functionManager, engine, host});
    })
    .catch(error => {
      console.error(error);
      this.setState({error});
    });
  }

  dispose() {
    substance.DefaultDOMElement.getBrowserWindow().off(this);
  }

  getInitialState() {
    return {
      archive: undefined,
      error: undefined
    }
  }

  render($$) {
    let el = $$('div').addClass('sc-app');
    let { archive, host, functionManager, engine, error } = this.state;

    if (archive) {
      el.append(
        $$(stencila.Project, {
          documentArchive: archive,
          host,
          functionManager,
          engine
        })
      );
    } else if (error) {
      if (error.type === 'jats-import-error') {
        el.append(
          $$(substanceTexture.JATSImportDialog, { errors: error.detail })
        );
      } else {
        el.append(
          'ERROR:',
          error.message
        );
      }
    } else {
      el.append('LOADING')
    }
    return el
  }
}

window.addEventListener('load', () => {
  App.mount({}, window.document.body);
});
