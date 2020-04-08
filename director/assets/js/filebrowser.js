const UPLOAD_STATUS = {
  WAITING: 0,
  IN_PROGRESS: 1,
  COMPLETED_SUCCESS: 2,
  COMPLETED_FAILURE: 3
}

const SOURCE_TYPE_NAME_LOOKUP = {
  'googledocssource': 'Google Docs',
  'githubsource': 'Github'
}

function rootPathJoin (directory, fileName) {
  let joiner = ''

  if (directory.length !== 0 && directory.substring(directory.length - 1, 1) !== '/') {
    joiner = '/'
  }
  return '/' + directory + joiner + fileName
}

function jsonFetch (url, body, callback) {
  fetch(url, {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': utils.cookie('csrftoken'),
    },
    credentials: 'same-origin',
    body: JSON.stringify(body)
  }).then(response => {
    return response.json()
  }).then(jsonBody => {
    const errors = jsonBody.errors !== undefined ? jsonBody.errors : jsonBody.error
    callback(jsonBody.success, errors)
  }, error => {
    callback(false, 'An unknown error occurred.')
  }).catch(error => {
    callback(false, error)
  })
}

function extensionFromType (type) {
  if (type === 'jats') {
    return '.jats.xml'
  }

  if (['md', 'html', 'docx', 'rmd', 'ipynb', 'jsonld', 'gdoc'].indexOf(type) !== -1) {
    return `.${type}`
  }

  return ''
}

function splitExt (fileName) {
  const extIndex = fileName.lastIndexOf('.')

  if (extIndex <= 0)
    return [fileName, '']

  return [fileName.substring(0, extIndex), fileName.sub(extIndex)]
}

Vue.component('item-action-menu', {
  mixins: [g_fileActionsCommon],
  props: {
    hasEditPermission: {
      type: Boolean,
      required: true
    },
    absolutePath: {
      type: String,
      required: true
    },
    fileName: {
      type: String,
      required: true
    },
    index: {
      type: String,
      required: true
    },
    allowDelete: {
      type: Boolean,
      required: false,
      default: false
    },
    allowUnlink: {
      type: Boolean,
      required: false,
      default: false
    },
    allowRename: {
      type: Boolean,
      required: false,
      default: false
    },
    allowEdit: {
      type: Boolean,
      required: false,
      default: false
    },
    editorUrl: {
      type: String,
      required: false,
      default: ''
    },
    downloadUrl: {
      type: String,
      required: false,
      default: ''
    },
    editMenuText: {
      type: String,
      required: false,
      default: ''
    },

    sourceIdentifier: {
      type: String,
      required: false,
      default: null
    },
    sourceType: {
      type: String,
      required: false,
      default: ''
    },
    sourceDescription: {
      type: String,
      required: false,
      default: ''
    }
  },
  data () {
    return {
      active: false
    }
  },
  computed: {
    editTarget () {
      return this.fileType === 'application/vnd.google-apps.document' ? '_blank' : ''
    },
    allowDownload () {
      return this.downloadUrl !== ''
    },
    hasOpenActions () {
      return this.allowEdit
    },
    hasConvertActions () {
      return this.hasEditPermission && this.convertTargets.length > 0
    },
    isConvertible () {
      return this.hasEditPermission && this.hasConvertTargets()
    },
    hasFileManageActions () {
      return this.allowDelete || this.allowRename || this.allowDownload || this.allowUnlink
    },
    shouldDisplay () {
      return this.hasOpenActions || this.hasConvertActions || this.hasFileManageActions
    },
    shouldDisplayOpenConvertDivider () {
      return this.hasOpenActions && (this.hasConvertActions || this.hasFileManageActions)
    },
    shouldDisplayConvertFileManageDivider () {
      return this.hasConvertActions && this.hasFileManageActions
    },
  },
  methods: {
    showRenameModal () {
      const itemType = this.fileType === 'directory' ? 'Directory' : 'File'
      this.$root.$emit('rename-modal-show', this.fileName, 'Rename', itemType)
    },
    showRemoveModal () {
      this.$root.$emit('remove-modal-show', this.fileName)
    },
    showUnlinkModal () {
      this.$root.$emit('unlink-modal-show', this.sourceType, this.sourceIdentifier, this.sourceDescription)
    },
    startConvert (targetType) {
      this.$root.$emit('convert-modal-show', targetType, this.convertTargets, this.sourceIdentifier, this.fileName, this.absolutePath)
    },
  },
  template: '' +
    '<div v-if="shouldDisplay" class="dropdown item-actions-dropdown" @click="toggle()" :class="{ \'is-active\':active }">' +
    '  <div class="dropdown-trigger">' +
    '    <a aria-haspopup="true" :aria-controls="\'item-actions-menu-\' + index"><i class="fa fa-ellipsis-h"></i></a>' +
    '  </div>' +
    '  <div class="dropdown-menu" id="\'item-actions-menu-\' + index" role="menu">' +
    '    <div class="dropdown-content">' +
    '      <a :href="editorUrl" target="_blank" rel="noopener" class="dropdown-item"><span class="icon"><i class="fas fa-external-link-alt"></i></span>Open</a>' +
    '      <hr v-if="shouldDisplayOpenConvertDivider" class="dropdown-divider">' +
    '      <span v-if="convertTargets.length" class="dropdown-item grouping-header"><span class="icon"><i class="fas fa-file-export"></i></span>Save As</span>' +
    '      <a v-for="convertTarget in mainConvertTargets" href="#" class="dropdown-item indent" @click.prevent="startConvert(convertTarget[0])">{{ convertTarget[1] }}&hellip;</a>' +
    '      <a v-if="convertTargets.length" href="#" class="dropdown-item indent" @click.prevent="startConvert(\'\')">Other&hellip;</a>' +
    '      <hr v-if="shouldDisplayConvertFileManageDivider" class="dropdown-divider">' +
    '      <a v-if="allowRename" href="#" class="dropdown-item" @click.prevent="showRenameModal()"><span class="icon"><i class="fas fa-i-cursor"></i></span>Rename&hellip;</a>' +
    '      <a v-if="allowDelete" href="#" class="dropdown-item" @click.prevent="showRemoveModal()"><span class="icon"><i class="fas fa-trash"></i></span>Delete&hellip;</a>' +
    '      <a v-if="allowUnlink" href="#" class="dropdown-item" @click.prevent="showUnlinkModal()"><span class="icon"><i class="fas fa-unlink"></i></span>Unlink&hellip;</a>' +
    '      <hr v-if="shouldDisplayConvertFileManageDivider" class="dropdown-divider">' +
    '      <a v-if="allowPreview" :href="previewUrl" class="dropdown-item" target="_blank" rel="noopener"><span class="icon"><i class="fas fa-eye"></i></span>Preview</a>' +
    '      <a v-if="allowDownload" :href="downloadUrl" class="dropdown-item"><span class="icon"><i class="fas fa-download"></i></i></span>Download</a>' +
    '    </div>' +
    '  </div>' +
    '</div>'
})

Vue.component('remove-item-modal', {
  props: {
    directoryPath: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      itemName: '',
      errorMessage: null,
      inProgress: false,
      visible: false
    }
  },
  computed: {
    currentPath () {
      return rootPathJoin(this.directoryPath, this.itemName)
    }
  },
  methods: {
    hide () {
      if (this.inProgress) {
        return
      }

      this.visible = false
    },
    performDelete () {
      this.errorMessage = null

      this.inProgress = true

      this.$root.$emit('remove-item', this.currentPath.substring(1), (success, message) => {
        if (success) {
          location.reload()
        } else {
          this.inProgress = false
          this.errorMessage = message
        }
      })

    }
  },
  mounted () {
    this.$root.$on('remove-modal-show', (itemName) => {
      this.itemName = itemName
      this.visible = true
    })

    this.$root.$on('modal-hide', () => {
      this.hide()
    })
  },
  template: '' +
    '<div class="modal" :class="{\'is-active\': visible}">' +
    '  <div class="modal-background"></div>' +
    '  <div class="modal-card">' +
    '    <header class="modal-card-head">' +
    '      <p class="modal-card-title"><i class="fa fa-trash"></i> Delete&nbsp;<em>{{ itemName }}</em></p>' +
    '      <button class="delete" aria-label="close" @click="hide()"></button>' +
    '    </header>' +
    '    <section class="modal-card-body">' +
    '        <p>Are you sure you want to delete <em>{{ itemName }}</em>?</p>' +
    '        <p v-if="errorMessage != null" class="has-text-danger">{{ errorMessage }}</p>' +
    '    </section>' +
    '    <footer class="modal-card-foot">' +
    '      <button class="button is-danger" @click.prevent="performDelete()" :disabled="inProgress"  :class="{\'is-loading\': inProgress}">Delete</button>' +
    '      <button class="button" :disabled="inProgress" @click.prevent="hide()">Cancel</button>' +
    '    </footer>' +
    '  </div> ' +
    '</div>'
})

Vue.component('rename-item-modal', {
  props: {
    directoryPath: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      visible: false,
      itemName: '',
      itemType: '',
      action: '',
      destination: '',
      errorMessage: null,
      inProgress: false
    }
  },
  computed: {
    currentPath () {
      return rootPathJoin(this.directoryPath, this.itemName)
    }
  },
  methods: {
    hide () {
      if (this.inProgress) {
        return
      }

      this.visible = false
    },
    performRename () {
      this.errorMessage = null

      if (this.destination === '') {
        this.errorMessage = 'Name must not be empty.'
        return
      }

      if (this.destination.substring(0, 1) !== '/') {
        this.destination = '/' + this.destination
      }

      this.inProgress = true

      this.$root.$emit('rename-item', this.currentPath.substring(1), this.destination.substring(1), (success, message) => {
        if (success) {
          location.reload()
        } else {
          this.inProgress = false
          this.errorMessage = message
        }
      })

    }
  },
  mounted () {
    this.$root.$on('rename-modal-show', (itemName, action, itemType) => {
      this.itemName = itemName
      this.itemType = itemType
      this.action = action
      this.destination = this.currentPath
      this.visible = true
    })

    this.$root.$on('modal-hide', () => {
      this.hide()
    })
  },
  template: '' +
    '<div class="modal" :class="{\'is-active\': visible}">' +
    '  <div class="modal-background"></div>' +
    '  <div class="modal-card">' +
    '    <header class="modal-card-head">' +
    '      <p class="modal-card-title"><i class="fa fa-pencil-alt"></i> {{ action }}&nbsp;<em>{{ itemName }}</em></p>' +
    '      <button class="delete" aria-label="close" @click="hide()"></button>' +
    '    </header>' +
    '    <section class="modal-card-body">' +
    '      <div class="control">' +
    '        <input class="input is-medium" type="text" :placeholder="action + \' To\'" v-model="destination">' +
    '        <p v-if="errorMessage != null" class="has-text-danger">{{ errorMessage }}</p>' +
    '      </div>' +
    '    </section>' +
    '    <footer class="modal-card-foot">' +
    '      <button class="button is-primary" @click.prevent="performRename()" :disabled="inProgress" :class="{\'is-loading\': inProgress}">{{ action }}</button>' +
    '      <button class="button" :disabled="inProgress" @click.prevent="hide()">Cancel</button>' +
    '    </footer>' +
    '  </div> ' +
    '</div>'
})

Vue.component('add-item-modal', {
  props: {
    directoryPath: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      visible: false,
      itemName: '',
      itemType: '',
      createInProgress: false,
      errorMessage: null
    }
  },
  mounted () {
    this.$root.$on('add-item-modal-show', this.show)

    this.$root.$on('modal-hide', () => {
      this.hide()
    })
  },
  computed: {
    fullPath () {
      return rootPathJoin(this.directoryPath, this.itemName)
    }
  },
  methods: {
    show (itemType) {
      this.visible = true
      this.itemType = itemType
      this.itemName = ''
    },
    hide () {
      if (this.createInProgress) {
        return
      }

      this.errorMessage = null
      this.visible = false
      this.itemName = ''
    },
    create () {
      this.errorMessage = null

      if (this.itemName === '') {
        this.errorMessage = 'Name must not be empty.'
        return
      }

      if (this.itemName.indexOf('/') !== -1) {
        this.errorMessage = 'Name must not contain "/".'
        return
      }

      if (this.itemName === '..' || this.itemName === '.') {
        this.errorMessage = 'Name must not be "." or "..".'
        return
      }

      this.createInProgress = true
      this.$root.$emit('create-item', this.itemType.toLowerCase(), this.fullPath.substring(1), (success, message) => {
        if (success) {
          location.reload()
        } else {
          this.createInProgress = false
          this.errorMessage = message
        }
      })
    }
  },
  template: '<div class="modal" :class="{\'is-active\': visible}">' +
    '            <div class="modal-background"></div>' +
    '            <div class="modal-card">' +
    '                <header class="modal-card-head">' +
    '                    <p class="modal-card-title"><i class="fa" :class="{\'fa-file\': itemType == \'File\', \'fa-folder\': itemType == \'Folder\'}"></i> New {{ itemType }}</p>' +
    '                    <button class="delete" aria-label="close" @click.prevent="hide()"></button>' +
    '                </header>' +
    '                <section class="modal-card-body">' +
    '                    <div class="field">' +
    '                        <div class="control">' +
    '                            <label class="label">{{ itemType }} Name</label>' +
    '                            <input class="input is-medium" type="text" :placeholder="itemType + \' Name\'" ' +
    '                               v-model="itemName">' +
    '                        </div>' +
    '                    </div>' +
    '                    <div>Full path: <em>{{ fullPath }}</em></div>' +
    '                    <p v-if="errorMessage != null" class="has-text-danger">{{ errorMessage }}</p>' +
    '                </section>' +
    '                <footer class="modal-card-foot">' +
    '                    <button class="button is-primary" @click.prevent="create()" :disabled="createInProgress"  :class="{\'is-loading\': createInProgress}">Create</button>' +
    '                    <button class="button" :disabled="createInProgress" @click.prevent="hide()">Cancel</button>' +
    '                </footer>' +
    '            </div>' +
    '        </div>'
})

Vue.component('convert-modal', {
  props: {
    sourceConvertUrl: {
      type: String,
      required: true
    },
    existingFiles: {
      type: Array,
      required: true
    }
  },
  data () {
    return {
      visible: false,
      sourceIdentifier: '',
      sourceName: '',
      sourcePath: '',
      targetTypeName: '',
      targetType: '',
      convertTargets: [],
      targetName: '',
      convertInProgress: false,
      confirmExistingFileOverwrite: false,
      errorMessage: null,
      manualNameChange: false
    }
  },
  computed: {
    hasFilenameConflict () {
      return this.existingFiles.indexOf(this.targetName) !== -1
    },
    convertButtonDisabled () {
      return this.convertInProgress || (this.hasFilenameConflict && !this.confirmExistingFileOverwrite)
    }
  },
  mounted () {
    this.$root.$on('convert-modal-show', (targetType, convertTargets, sourceIdentifier, sourceName, sourcePath) => {
      this.sourceIdentifier = sourceIdentifier
      this.sourceName = sourceName
      this.sourcePath = sourcePath

      if (targetType === '')
        this.targetType = convertTargets[0][0]
      else
        this.targetType = targetType
      this.generateTargetName()

      this.convertTargets = convertTargets

      this.manualNameChange = false

      this.visible = true
    })

    this.$root.$on('modal-hide', () => {
      this.hide()
    })
  },
  methods: {
    hide () {
      if (this.convertInProgress) {
        return
      }

      this.visible = false
    },
    convert () {
      if (this.targetName.indexOf('/') !== -1) {
        this.errorMessage = 'Name must not contain /'
        return
      }
      this.convertInProgress = true

      jsonFetch(this.sourceConvertUrl, {
        source_id: this.sourceIdentifier,
        source_path: this.sourcePath,
        target_name: this.targetName,
        target_type: this.targetType
      }, (success, errorMessage) => {
        this.convertInProgress = false
        if (success) {
          location.reload()
        } else {
          this.errorMessage = errorMessage
        }
      })
    },
    nameChange () {
      this.manualNameChange = true
      this.errorMessage = null
      this.confirmExistingFileOverwrite = false
    },
    generateTargetName() {
      const sourceNameAndExt = splitExt(this.sourceName)
      this.targetName = sourceNameAndExt[0] + extensionFromType(this.targetType)
    },
    targetTypeChange() {
      if (!this.manualNameChange) {
        this.generateTargetName()
      }
    }
  },
  template: '' +
    '<div class="modal" :class="{\'is-active\': visible}">' +
    '  <div class="modal-background"></div>' +
    '  <div class="modal-card">' +
    '    <header class="modal-card-head">' +
    '      <p class="modal-card-title"><i class="fas fa-file-export"></i>Save&nbsp;<em>{{ sourceName }}</em>&nbsp;as</p>' +
    '      <button class="delete" aria-label="close" @click="hide()"></button>' +
    '    </header>' +
    '    <section class="modal-card-body">' +
    '      <div class="field has-addons">' +
    '        <div class="control">' +
    '          <div class="select is-medium">' +
    '            <select @change="targetTypeChange" v-model="targetType">' +
    '              <option v-for="convertTarget in convertTargets" :value="convertTarget[0]">{{ convertTarget[1] }}</option>' +
    '            </select>' +
    '          </div>' +
    '        </div>' +
    '        <div class="control">' +
    '          <input class="input is-medium" type="text" placeholder="Converted File Name" v-model="targetName" @keypress="nameChange()">' +
    '          <p v-if="errorMessage != null" class="has-text-danger">{{ errorMessage }}</p>' +
    '        </div>' +
    '      </div>' +
    '      <transition v-if="hasFilenameConflict" name="fade">' +
    '         <p>' +
    '          <span class="icon has-text-warning"><i class="fas fa-exclamation-triangle"></i></span><em>{{ targetName }}</em> already exists.<br>' +
    '          Please use a different name, or confirm you want to replace it: ' +
    '          <span class="control"><input type="checkbox" v-model="confirmExistingFileOverwrite"></span>' +
    '        </p>' +
    '      </transition>' +
    '    </section>' +
    '    <footer class="modal-card-foot">' +
    '      <button class="button is-primary" @click.prevent="convert()" :disabled="convertButtonDisabled"  :class="{\'is-loading\': convertInProgress}">Save</button>' +
    '      <button class="button" :disabled="convertInProgress" @click.prevent="hide()">Cancel</button>' +
    '    </footer>' +
    '  </div>' +
    '</div>'
})

Vue.component('publish-modal', {
  props: {
    publishUrl: {
      type: String,
      required: true
    },
    projectUrl: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      visible: false,
      sourceName: '',
      publishInProgress: false,
      sourceId: null,
      path: null,
      urlError: null,
      errorMessage: '',
      urlPath: ''
    }
  },
  computed: {
    publishedUrl () {
      return this.projectUrl + this.urlPath
    }
  },
  methods: {
    publishDisabled () {
      return this.urlPath === '' || this.publishInProgress
    },
    show (sourceId, path) {
      this.sourceId = sourceId
      this.path = path
      this.visible = true
    },
    hide () {
      if (this.publishInProgress)
        return

      this.visible = false
    },
    publish () {
      this.publishInProgress = true
      fetch(this.publishUrl, {
        method: 'POST',
        body: JSON.stringify({
          'source_id': this.sourceId,
          'source_path': this.path,
          'url_path': this.urlPath
        }),
        headers: {
          'X-CSRFToken': utils.cookie('csrftoken'),
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      }).then((response) => {
        return response.json()
      }).then(data => {
        const success = data.success
        if (success) {
          window.location.reload()
          return
        } else {
          if (data.errors.url) {
            this.urlError = ''
            const urlErrors = data.errors.url.map(errorDict => {
              return errorDict.mean
            })
            this.urlError = urlErrors.join(' ')
          } else {
            alert('An error occurred during publish, please check the console.')
            console.error(data.errors)
          }
        }
        this.publishInProgress = false
      }).catch(error => {
        this.publishInProgress = false
      })
    }
  },
  mounted () {
    this.$root.$on('publish-modal-show', (sourceId, path) => {
      this.show(sourceId, path)
    })
  },
  template: '' +
    '<div class="modal" :class="{\'is-active\': visible}">' +
    '  <div class="modal-background"></div>' +
    '  <div class="modal-card">' +
    '    <header class="modal-card-head">' +
    '      <p class="modal-card-title">Publish</p>' +
    '      <button class="delete" aria-label="close" @click="hide()"></button>' +
    '    </header>' +
    '    <section class="modal-card-body">' +
    '      <div class="content-container">' +
    '        <p>' +
    '          File <em>{{ sourceName }}</em> will be converted to HTML and published for this project.' +
    '        </p>' +
    '      </div>' +
    '      <div class="field">' +
    '        <div class="control">' +
    '          <label class="label">URL Path</label>' +
    '          <input class="input is-medium" type="text" placeholder="Path" v-model="urlPath">' +
    '          <p class="help">The relative path of the published item URL, which is appended to this Project\'s URL</p>' +
    '          <p class="help">URL after publishing: <strong>{{ publishedUrl }}</strong></p>' +
    '          <p v-if="urlError != null" class="has-text-danger">{{ urlError }}</p>' +
    '        </div>' +
    '      </div>' +
    '    </section>' +
    '    <footer class="modal-card-foot">' +
    '      <button class="button is-primary" @click.prevent="publish()" :disabled="publishDisabled()"  :class="{\'is-loading\': publishInProgress}">Publish</button>' +
    '      <button class="button" :disabled="publishInProgress" @click.prevent="hide()">Cancel</button>' +
    '    </footer>' +
    '  </div>' +
    '</div>'
})

Vue.component('upload-progress-row', {
  data () {
    return {
      UPLOAD_STATUS: UPLOAD_STATUS
    }
  },
  props: {
    item: {
      type: Object,
      required: true
    }
  },
  template: '' +
    '<tr>' +
    '  <td>{{ item.name }}</td>' +
    '  <td>' +
    '    <i class="fas fa-circle-notch fa-spin" v-if="item.uploadStatus === UPLOAD_STATUS.IN_PROGRESS"></i>' +
    '    <i class="fas fa-times" v-if="item.uploadStatus === UPLOAD_STATUS.COMPLETED_FAILURE"></i>' +
    '    <i class="fas fa-check" v-if="item.uploadStatus === UPLOAD_STATUS.COMPLETED_SUCCESS"></i>' +
    '  </td>' +
    '  <td>' +
    '    <span v-if="item.uploadStatus === UPLOAD_STATUS.WAITING">Waiting</span>' +
    '    <span v-if="item.uploadStatus === UPLOAD_STATUS.IN_PROGRESS">In progress</span>' +
    '    <span v-if="item.uploadStatus === UPLOAD_STATUS.COMPLETED_SUCCESS">Completed</span>' +
    '    <span class="has-text-danger" v-if="item.uploadStatus === UPLOAD_STATUS.COMPLETED_FAILURE">Failed: {{ item.error }}</span>' +
    '  </td>' +
    '</tr>'
})

Vue.component('upload-progress-modal', {
  props: {
    uploadUrl: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      uploadInProgress: false,
      itemsWereUploaded: false,
      visible: false,
      items: []
    }
  },
  mounted () {
    this.$root.$on('upload-progress-modal-show', this.show)

    this.$root.$on('modal-hide', () => {
      this.hide()
    })
  },
  methods: {
    show (uploads) {
      this.visible = uploads.length !== 0
      this.items = uploads
      this.processUploadQueue()
    },
    hide () {
      if (this.uploadInProgress) {
        return
      }

      if (this.itemsWereUploaded) {
        location.reload()
      }

      this.visible = false
    },
    processUploadQueue () {
      let item = null
      for (let i = 0; i < this.items.length; ++i) {
        if (this.items[i].uploadStatus === UPLOAD_STATUS.WAITING) {
          item = this.items[i]
          break
        }
      }

      if (item === null) {
        this.uploadInProgress = false
        return
      }

      this.uploadItem(item)
    },
    uploadItem (item) {
      this.uploadInProgress = true

      Vue.set(item, 'uploadStatus', UPLOAD_STATUS.IN_PROGRESS)

      const formData = new FormData()
      formData.append('file', item.file)

      fetch(this.uploadUrl, {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': utils.cookie('csrftoken'),
          'Accept': 'application/json'
        }
      }).then((response) => {
        return response.json()
      }).then(data => {
        const uploadSuccess = data.success

        if (uploadSuccess)
          this.itemsWereUploaded = true

        Vue.set(item, 'uploadStatus', uploadSuccess ? UPLOAD_STATUS.COMPLETED_SUCCESS : UPLOAD_STATUS.COMPLETED_FAILURE)
        Vue.set(item, 'error', data.error)
        this.processUploadQueue()
      }).catch(error => {
        Vue.set(item, 'uploadStatus', UPLOAD_STATUS.COMPLETED_FAILURE)
        Vue.set(item, 'error', error)
        this.processUploadQueue()
      })
    }
  },
  template: '' +
    '<div class="modal" :class="{\'is-active\': visible}">' +
    '  <div class="modal-background"></div>' +
    '  <div class="modal-card">' +
    '    <header class="modal-card-head">' +
    '      <p class="modal-card-title"><i class="fa fa-upload"></i> File upload</p>' +
    '    </header>' +
    '    <section class="modal-card-body">' +
    '      <table class="table is-fullwidth">' +
    '        <thead>' +
    '          <tr>' +
    '            <th class="title-caption">Name</th>' +
    '            <th class="title-caption">Status</th>' +
    '            <th></th>' +
    '          </tr>' +
    '        </thead>' +
    '        <tbody>' +
    '          <upload-progress-row v-for="item in items" v-bind:key="item.id" :item="item"></upload-progress-row>' +
    '        </tbody>' +
    '      </table>' +
    '    </section>' +
    '    <footer class="modal-card-foot">' +
    '      <button class="button is-primary" @click.prevent="hide()" :disabled="uploadInProgress"  :class="{\'is-loading\': uploadInProgress}">Done</button>' +
    '    </footer>' +
    '  </div>' +
    '</div>'
})

function linkSource (sourceLinkUrl, sourceType, directory, postParameters, callback) {
  postParameters['source_type'] = sourceType
  postParameters['directory'] = directory
  jsonFetch(sourceLinkUrl, postParameters, callback)
}

Vue.component('googledocs-link-modal', {
  props: {
    directory: {
      type: String,
      required: true
    },
    sourceLinkUrl: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      docIdOrUrl: '',
      errorMessage: null,
      inProgress: false,
      visible: false
    }
  },
  methods: {
    show () {
      this.visible = true
    },
    hide () {
      if (this.inProgress) {
        return
      }

      this.visible = false
    },
    performLink () {
      this.errorMessage = null

      if (this.destination === '') {
        this.errorMessage = 'ID or URL must not be empty.'
        return
      }

      this.inProgress = true
      linkSource(this.sourceLinkUrl, 'gdoc', this.directory, {document_id: this.docIdOrUrl}, (success, errorMessage) => {
        this.inProgress = false
        if (success) {
          location.reload()
        } else {
          this.errorMessage = errorMessage
        }
      })
    }
  },
  mounted () {
    this.$root.$on('googledocs-link-modal-show', this.show)

    this.$root.$on('modal-hide', () => {
      this.hide()
    })
  },
  template: '' +
    '<div class="modal" :class="{\'is-active\': visible}">' +
    '  <div class="modal-background"></div>' +
    '  <div class="modal-card">' +
    '    <header class="modal-card-head">' +
    '      <p class="modal-card-title"><i class="fa fa-link"></i> Link Google Doc</p>' +
    '      <button class="delete" aria-label="close" @click="hide()"></button>' +
    '    </header>' +
    '    <section class="modal-card-body">' +
    '      <div class="control">' +
    '        <label class="label">Document ID or URL</label>' +
    '        <input class="input is-medium" type="text" placeholder="Document ID or URL" v-model="docIdOrUrl">' +
    '        <p v-if="errorMessage != null" class="has-text-danger">{{ errorMessage }}</p>' +
    '      </div>' +
    '      <p class="help">For example, <em>https://docs.google.com/document/d/[document id]/</em></p>' +
    '    </section>' +
    '    <footer class="modal-card-foot">' +
    '      <button class="button is-primary" @click.prevent="performLink()" :disabled="inProgress"  :class="{\'is-loading\': inProgress}">Link</button>' +
    '      <button class="button" :disabled="inProgress" @click.prevent="hide()">Cancel</button>' +
    '    </footer>' +
    '  </div> ' +
    '</div>'
})

Vue.component('url-link-modal', {
  props: {
    directory: {
      type: String,
      required: true
    },
    sourceLinkUrl: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      url: '',
      urlErrorMessage: null,
      filenameErrorMessage: null,
      inProgress: false,
      visible: false,
      autoFilename: true,
      filename: ''
    }
  },
  methods: {
    show () {
      this.autoFilename = true
      this.visible = true
      this.filename = ''
      this.urlErrorMessage = null
      this.filenameErrorMessage = null
    },
    hide () {
      if (this.inProgress) {
        return
      }

      this.visible = false
    },
    filenameChange () {
      this.autoFilename = false
      this.filenameErrorMessage = null
    },
    generateFilename () {
      if (!this.autoFilename)
        return

      this.filename = this.url.replace(/^https?:\/\//, '').replace(/\/|=|\?|\.\\/g, '-')
    },
    performLink () {
      this.urlErrorMessage = null
      this.filenameErrorMessage = null

      if (this.destination === '') {
        this.urlErrorMessage = 'URL must not be empty.'
        return
      }

      if (this.filename === '') {
        this.filenameErrorMessage = 'Filename must not be empty.'
      }

      if (this.filename.indexOf('/') !== -1 || this.filename.indexOf(':') !== -1 || this.filename.indexOf('\\') !== -1 || this.filename.indexOf(';') !== -1) {
        this.filenameErrorMessage = 'The filename must not contain the characters: /, :, \\ or ;.'
      }

      if (this.urlErrorMessage !== null || this.filenameErrorMessage !== null) {
        return
      }

      this.inProgress = true
      linkSource(this.sourceLinkUrl, 'url', this.directory, {
        url: this.url, filename: this.filename
      }, (success, errorMessages) => {
        this.inProgress = false
        if (success) {
          location.reload()
        } else {
          this.urlErrorMessage = errorMessages['url']
          this.filenameErrorMessage = errorMessages['filename']
        }
      })
    }
  },
  mounted () {
    this.$root.$on('url-link-modal-show', this.show)

    this.$root.$on('modal-hide', () => {
      this.hide()
    })
  },
  template: '' +
    '<div class="modal" :class="{\'is-active\': visible}">' +
    '  <div class="modal-background"></div>' +
    '  <div class="modal-card">' +
    '    <header class="modal-card-head">' +
    '      <p class="modal-card-title"><i class="fa fa-link"></i> Link URL</p>' +
    '      <button class="delete" aria-label="close" @click="hide()"></button>' +
    '    </header>' +
    '    <section class="modal-card-body">' +
    '      <div class="control">' +
    '        <label class="label">URL</label>' +
    '        <input class="input is-medium" type="text" placeholder="URL" v-model="url" @keyup="generateFilename()" @change="generateFilename()">' +
    '        <p v-if="urlErrorMessage != null" class="has-text-danger">{{ urlErrorMessage }}</p>' +
    '      </div>' +
    '      <p class="help">For example, <em>https://hackmd.io/[document_id]</document_id></em></p>' +
    '      <div class="control">' +
    '        <label class="label">Filename</label>' +
    '        <input class="input is-medium" type="text" placeholder="Filename" v-model="filename" @keyup="filenameChange()">' +
    '        <p v-if="filenameErrorMessage != null" class="has-text-danger">{{ filenameErrorMessage }}</p>' +
    '      </div>' +
    '    </section>' +
    '    <footer class="modal-card-foot">' +
    '      <button class="button is-primary" @click.prevent="performLink()" :disabled="inProgress"  :class="{\'is-loading\': inProgress}">Link</button>' +
    '      <button class="button" :disabled="inProgress" @click.prevent="hide()">Cancel</button>' +
    '    </footer>' +
    '  </div> ' +
    '</div>'
})

Vue.component('unsupported-social-provider-modal', {
  props: {
    accountConnectionsUrl: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      visible: false,
      providerType: ''
    }
  },
  methods: {
    hide () {
      this.visible = false
    },
    show (providerType) {
      this.providerType = providerType
      this.visible = true
    }
  },
  mounted () {
    this.$root.$on('unsupported-social-provider-modal-show', this.show)

    this.$root.$on('modal-hide', () => {
      this.hide()
    })
  },
  template: '' +
    '<div class="modal" :class="{\'is-active\': visible}">' +
    '  <div class="modal-background"></div>' +
    '  <div class="modal-card">' +
    '    <header class="modal-card-head">' +
    '      <p class="modal-card-title">{{ providerType }} Account Not Connected</p>' +
    '      <button class="delete" aria-label="close" @click="hide()"></button>' +
    '    </header>' +
    '    <section class="modal-card-body">' +
    '      <p>A source of this type can not be linked as there is no {{ providerType }} account connected to your Stencila Hub account.</p>' +
    '      <p>You connect one on the <a :href="accountConnectionsUrl">Account Connections</a> page.</p>' +
    '    </section>' +
    '    <footer class="modal-card-foot">' +
    '      <button class="button is-primary" @click.prevent="hide()">OK</button>' +
    '    </footer>' +
    '  </div>' +
    '</div>'
})

Vue.component('snapshot-modal', {
  props: {
    snapshotCreateUrl: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      visible: false,
      tag: '',
      snapshotInProgress: false,
      snapshotComplete: false,
      snapshotError: ''
    }
  },
  computed: {
    actionButtonText () {
      if (this.snapshotInProgress) {
        return 'Snapshot In Progress'
      }
      if (this.snapshotComplete) {
        return 'Snapshot Complete'
      }
      return 'Snapshot'
    }
  },
  methods: {
    hide () {
      this.visible = false
    },
    show () {
      this.visible = true
      this.tag = ''
    },
    snapshot () {
      this.snapshotInProgress = true
      this.snapshotError = ''
      fetch(this.snapshotCreateUrl, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-CSRFToken': utils.cookie('csrftoken')
        },
        credentials: 'same-origin',
        body: JSON.stringify({tag: this.tag})
      }).then(
        response => {
          this.snapshotInProgress = false
          response.json().then(data => {
            if (response.status >= 400)
              this.snapshotError = data.message
            else
              this.snapshotComplete = true
          })
        },
        failureResponse => {
          this.snapshotInProgress = false
          this.snapshotComplete =  true
          this.snapshotError = failureResponse
        })
    }
  },
  mounted () {
    this.$root.$on('snapshot-modal-show', this.show)

    this.$root.$on('modal-hide', () => {
      this.hide()
    })
  },
  template: '' +
    '<div class="modal" :class="{\'is-active\': visible}">' +
    '  <div class="modal-background"></div>' +
    '  <div class="modal-card">' +
    '    <header class="modal-card-head">' +
    '      <p class="modal-card-title">Snapshot Project</p>' +
    '      <button class="delete" aria-label="close" @click="hide()"></button>' +
    '    </header>' +
    '    <section class="modal-card-body" v-if="!snapshotComplete">' +
    '      <p>A snapshot is an immutable copy of all this Project\'s files and sources at the current time.</p>' +
    '      <p>All content in linked sources will be downloaded to disk and saved as regular files.</p>' +
    '      <div class="field">' +
    '        <label class="label" for="id_snapshot_tag">Tag</label>' +
    '        <div class="control">' +
    '          <input class="input" type="text" id="id_snapshot_tag" v-model="tag" placeholder="Tag (Optional)">' +
    '          <p class="help">A tag is optional but can help identify snapshots later. It must be unique for each snapshot in this project.</p>' +
    '        </div>' +
    '      </div>' +
    '      <p v-if="snapshotError !== \'\'" class="has-text-danger">' +
    '        {{ snapshotError }}' +
    '      </p>' +
    '    </section>' +
    '    <section class="modal-card-body" v-if="snapshotComplete">' +
    '     <div class="notification">' +
    '       The snapshot was created successfully.' +
  '       </div>' +
    '    </section>' +
    '    <footer class="modal-card-foot" style="justify-content: space-between">' +
    '      <button class="button is-primary" @click.prevent="snapshot()" :disabled="snapshotInProgress || snapshotComplete">{{ actionButtonText }}</button>' +
    '    </footer>' +
    '  </div>' +
    '</div>'
})

var fileBrowser = new Vue({
  el: '#file-browser',
  delimiters: ['[[', ']]'],
  data: {
    itemCreateUrl: null,
    itemRenameUrl: null,
    itemRemoveUrl: null,
    filePullUrl: null,
    createItemVisible: false,
    fileList: g_fileList,
    unlinkSourceId: null,
    unlinkModalVisible: false,
    unlinkSourceDescription: '',
    unlinkSourceType: '',
    isUnlinkMulti: false,
    SOURCE_TYPE_NAME_LOOKUP: SOURCE_TYPE_NAME_LOOKUP
  },
  mounted () {
    this.filePullUrl = this.$refs['file-browser-root'].getAttribute('data-file-pull-url')
    this.itemCreateUrl = this.$refs['file-browser-root'].getAttribute('data-item-create-url')
    this.itemRenameUrl = this.$refs['file-browser-root'].getAttribute('data-item-rename-url')
    this.itemRemoveUrl = this.$refs['file-browser-root'].getAttribute('data-item-remove-url')
    document.addEventListener('keyup', this.handleKeyUp)
  },
  beforeDestroy () {
    document.removeEventListener('keyup', this.handleKeyUp)
  },
  created () {
    this.$root.$on('create-item', (type, path, callback) => {
      jsonFetch(this.itemCreateUrl, {
        path: path,
        type: type
      }, callback)
    })

    this.$root.$on('rename-item', (source, destination, callback) => {
      jsonFetch(this.itemRenameUrl, {source, destination}, callback)
    })

    this.$root.$on('remove-item', (path, callback) => {
      jsonFetch(this.itemRemoveUrl, {path}, callback)
    })

    this.$root.$on('unlink-modal-show', (sourceType, sourceIdentifier, sourceDescription) => {
      this.isUnlinkMulti = sourceType === 'githubsource'
      this.unlinkSourceType = sourceType
      this.unlinkSourceId = sourceIdentifier
      this.unlinkSourceDescription = sourceDescription
      this.unlinkModalVisible = true
    })

    this.$root.$on('set-main-file', (absolutePath, sourceIdentifier) => {
      jsonFetch(g_projectUpdateUrl, {
        'main_file_path': absolutePath,
        'main_file_source_id': sourceIdentifier
      }, (success, errorMessage) => {
        if (success) {
          location.reload()
        } else {
          alert(errorMessage)
        }
      })
    })
  },
  methods: {
    handleKeyUp (event) {
      if (event.key === 'Escape') {
        this.$root.$emit('modal-hide')
      }
    },
    hideUnlinkModal () {
      this.unlinkModalVisible = false
    }
  }
})

const g_actionBar = new Vue({
  el: '#file-action-bar',
  delimiters: ['[[', ']]'],
  data: {
    newMenuVisible: false,
    linkMenuVisible: false,
    pullInProgress: false,
    deleteModalVisible: false,
    unlinkSourceId: null,
    unlinkSourceDescription: ''
  },
  methods: {
    showFileUploadSelect () {
      this.$refs['file-upload'].click()
    },
    snapshotProject () {
      fileBrowser.$root.$emit('snapshot-modal-show')
      return
    },
    pullFiles () {
      if (this.pullInProgress)
        return
      this.pullInProgress = true
      fetch(g_filePullUrl, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'X-CSRFToken': utils.cookie('csrftoken'),
        },
        credentials: 'same-origin'
      }).then(
        response => {
          this.pullInProgress = false
          response.json().then(data => {
            if (data.success === true && data.reload === true)
              window.location = window.location
          })
        },
        failureResponse => {
          this.pullInProgress = false
          alert(failureResponse)
        })
    },
    createFile () {
      fileBrowser.$root.$emit('add-item-modal-show', 'File')
    },
    createFolder () {
      fileBrowser.$root.$emit('add-item-modal-show', 'Folder')
    },
    showLinkModal ($event, providerTypeId, linkType) {
      if (providerTypeId !== 'url' && g_supportedSocialProviders[providerTypeId] !== true) {
        $event.preventDefault()

        let providerTypeName = ''

        if (providerTypeId === 'google') {
          providerTypeName = 'Google'
        } else if (providerTypeId === 'github') {
          providerTypeName = 'Github'
        }

        fileBrowser.$root.$emit('unsupported-social-provider-modal-show', providerTypeName)
        return false
      }

      if (linkType === 'gdoc') {
        $event.preventDefault()
        fileBrowser.$root.$emit('googledocs-link-modal-show')
      } else if (linkType === 'url') {
        $event.preventDefault()
        fileBrowser.$root.$emit('url-link-modal-show')
      } else {
        return true
      }

      return false
    },
    showUnlinkModal (sourceDescription, sourceId) {
      this.unlinkSourceDescription = sourceDescription
      this.unlinkSourceId = sourceId
      fileBrowser.deleteModalVisible = true
    },
    toggleLinkMenu () {
      const newLinkMenuVisible = !this.linkMenuVisible
      this.resetMenus()
      this.linkMenuVisible = newLinkMenuVisible
    },
    toggleNewMenu () {
      const newNewMenuVisible = !this.newMenuVisible
      this.resetMenus()
      this.newMenuVisible = newNewMenuVisible
    },
    resetMenus () {
      fileBrowser.$root.$emit('menu-hide')
      this.linkMenuVisible = false
      this.newMenuVisible = false
    },
    hideDeleteModal () {
      this.deleteModalVisible = false
    },
    handleFileUpload (event) {
      const uploadList = []
      const files = event.target.files

      for (let i = 0; i < files.length; ++i) {
        uploadList.push({
            id: i,
            name: files[i].name,
            file: files[i],
            uploadStatus: UPLOAD_STATUS.WAITING,
            error: null
          }
        )
      }

      fileBrowser.$root.$emit('upload-progress-modal-show', uploadList)
    },
    bodyClick (event) {
      let el = event.target
      do {
        if (el.tagName === 'BUTTON' || (typeof el.classList !== 'undefined' && el.classList.contains('dropdown-trigger'))) {
          return
        }
      } while ((el = el.parentNode) != null)
      this.resetMenus()
    }
  },
  mounted () {
    document.addEventListener('click', this.bodyClick)
  },
  beforeDestroy () {
    document.removeEventListener('click', this.bodyClick)
  }
})

