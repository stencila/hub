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
    callback(jsonBody.success, jsonBody.error)
  }, error => {
    callback(false, 'An unknown error occurred.')
  }).catch(error => {
    callback(false, error)
  })
}

function extensionFromType (type) {
  if (type === 'markdown') {
    return '.md'
  }

  if (type === 'html') {
    return '.html'
  }

  if (type === 'docx') {
    return '.docx'
  }

  if (type === 'jats') {
    return '.jats.xml'
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
    allowDesktopLaunch: {
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
    fileType: {
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
    },
    allowMainFileSet: {
      type: Boolean,
      required: false,
      default: false
    }
  },
  data () {
    return {
      active: false
    }
  },
  mounted () {
    this.$root.$on('menu-hide', () => {
      this.active = false
    })
  },
  computed: {
    allowDownload () {
      return this.downloadUrl !== ''
    },
    hasOpenActions () {
      return this.allowEdit || this.allowDesktopLaunch
    },
    hasConvertActions () {
      return this.hasEditPermission && this.convertTargets.length > 0
    },
    hasFileManageActions () {
      return this.allowDelete || this.allowRename || this.allowDownload || this.allowUnlink || this.allowMainFileSet
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
    convertTargets () {
      if(!this.hasEditPermission) {
        return []
      }

      const convertibleDefinitions = [
        ['application/vnd.google-apps.document', 'gdoc', 'Google Docs'],
        ['text/html', 'html', 'HTML'],
        ['text/xml+jats', 'jats', 'JATS'],
        ['text/markdown', 'markdown', 'Markdown'],
        ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'docx', 'Microsoft Word']
      ]

      const convertibleMimetypes = convertibleDefinitions.map(typeDef => typeDef[0])

      if (convertibleMimetypes.indexOf(this.fileType) === -1)
        return []

      return convertibleDefinitions.filter(typeDefinition => typeDefinition[0] !== this.fileType).map(typeDefinition => typeDefinition.slice(1))
    }
  },
  methods: {
    toggle () {
      if (this.active) {
        this.active = false
      } else {
        this.$root.$emit('menu-hide')
        this.active = true
      }
    },
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
    launchDesktopEditor () {
      sessionWaitController.launchDesktopEditor(this.absolutePath)
    },
    startConvert (targetType, targetTypeName) {
      this.$root.$emit('convert-modal-show', targetType, targetTypeName, this.sourceIdentifier, this.fileName, this.absolutePath)
    },
    setAsMainFile () {
      this.$root.$emit('set-main-file', this.absolutePath, this.sourceIdentifier)
    }
  },
  template: '' +
    '<div v-if="shouldDisplay" class="dropdown item-actions-dropdown" @click="toggle()" :class="{ \'is-active\':active }">' +
    '  <div class="dropdown-trigger">' +
    '    <a aria-haspopup="true" :aria-controls="\'item-actions-menu-\' + index"><i class="fa fa-ellipsis-h"></i></a>' +
    '  </div>' +
    '  <div class="dropdown-menu" id="\'item-actions-menu-\' + index" role="menu">' +
    '    <div class="dropdown-content">' +
    '      <a v-if="allowEdit" :href="editorUrl" class="dropdown-item">{{ editMenuText }}</a>' +
    '      <a v-if="allowDesktopLaunch" href="#" class="dropdown-item" @click.prevent="launchDesktopEditor()">Open in Stencila Desktop</a>' +
    '      <hr v-if="shouldDisplayOpenConvertDivider" class="dropdown-divider">' +
    '      <a v-for="convertTarget in convertTargets" href="#" class="dropdown-item" @click.prevent="startConvert(convertTarget[0], convertTarget[1])">Save as {{ convertTarget[1] }}&hellip;</a>' +
    '      <hr v-if="shouldDisplayConvertFileManageDivider" class="dropdown-divider">' +
    '      <a v-if="allowDownload" :href="downloadUrl" class="dropdown-item">Download</a>' +
    '      <a v-if="allowRename" href="#" class="dropdown-item" @click.prevent="showRenameModal()">Rename&hellip;</a>' +
    '      <a v-if="allowDelete" href="#" class="dropdown-item" @click.prevent="showRemoveModal()">Delete&hellip;</a>' +
    '      <a v-if="allowUnlink" href="#" class="dropdown-item" @click.prevent="showUnlinkModal()">Unlink&hellip;</a>' +
    '      <a v-if="allowMainFileSet" href="#" class="dropdown-item" @click.prevent="setAsMainFile()">Set as Main File</a>' +
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
    '      <p class="modal-card-title"><i class="fa fa-trash"></i> Delete <em>{{ itemName }}</em>?</p>' +
    '      <button class="delete" aria-label="close" @click="hide()"></button>' +
    '    </header>' +
    '    <section class="modal-card-body">' +
    '        <p>Are you sure you want to delete <em>{{ itemName }}</em>?</p>' +
    '        <p v-if="errorMessage != null" class="has-text-danger">{{ errorMessage }}</p>' +
    '    </section>' +
    '    <footer class="modal-card-foot">' +
    '      <button class="button is-rounded is-danger" @click.prevent="performDelete()" :disabled="inProgress"  :class="{\'is-loading\': inProgress}">Delete</button>' +
    '      <button class="button is-rounded" :disabled="inProgress" @click.prevent="hide()">Cancel</button>' +
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
    '      <p class="modal-card-title"><i class="fa fa-pencil-alt"></i> {{ action }} {{ itemType }}</p>' +
    '      <button class="delete" aria-label="close" @click="hide()"></button>' +
    '    </header>' +
    '    <section class="modal-card-body">' +
    '      <div class="control">' +
    '        <label class="label">{{ action }} <em>{{ currentPath }}</em> to</label>' +
    '        <input class="input is-medium" type="text" :placeholder="action + \' To\'" v-model="destination">' +
    '        <p v-if="errorMessage != null" class="has-text-danger">{{ errorMessage }}</p>' +
    '      </div>' +
    '    </section>' +
    '    <footer class="modal-card-foot">' +
    '      <button class="button is-primary is-rounded" @click.prevent="performRename()" :disabled="inProgress"  :class="{\'is-loading\': inProgress}">{{ action }}</button>' +
    '      <button class="button is-rounded" :disabled="inProgress" @click.prevent="hide()">Cancel</button>' +
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
    '                    <button class="button is-primary is-rounded" @click.prevent="create()" :disabled="createInProgress"  :class="{\'is-loading\': createInProgress}">Create</button>' +
    '                    <button class="button is-rounded" :disabled="createInProgress" @click.prevent="hide()">Cancel</button>' +
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
      targetName: '',
      convertInProgress: false,
      confirmExistingFileOverwrite: false,
      errorMessage: null
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
    this.$root.$on('convert-modal-show', (targetType, targetTypeName, sourceIdentifier, sourceName, sourcePath) => {
      this.sourceIdentifier = sourceIdentifier
      this.sourceName = sourceName
      this.sourcePath = sourcePath
      const sourceNameAndExt = splitExt(sourceName)
      this.targetName = sourceNameAndExt[0] + extensionFromType(targetType)
      this.targetType = targetType
      this.targetTypeName = targetTypeName
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
      this.errorMessage = null
      this.confirmExistingFileOverwrite = false
    }
  },
  template: '' +
    '<div class="modal" :class="{\'is-active\': visible}">' +
    '  <div class="modal-background"></div>' +
    '  <div class="modal-card">' +
    '    <header class="modal-card-head">' +
    '      <p class="modal-card-title">Save as {{ targetTypeName }}</p>' +
    '      <button class="delete" aria-label="close" @click="hide()"></button>' +
    '    </header>' +
    '    <section class="modal-card-body">' +
    '      <div class="content-container">' +
    '        <p>File <em>{{ sourceName }}</em> will be saved as {{ targetTypeName }}. The original file will be preserved.</p>' +
    '      </div>' +
    '      <div class="field">' +
    '        <div class="control">' +
    '          <label class="label">Enter a name for the converted file</label>' +
    '          <input class="input is-medium" type="text" placeholder="Converted File Name" v-model="targetName" @keypress="nameChange()">' +
    '          <p v-if="errorMessage != null" class="has-text-danger">{{ errorMessage }}</p>' +
    '        </div>' +
    '      </div>' +
    '      <transition name="fade">' +
    '        <article class="message is-warning" v-if="hasFilenameConflict">' +
    '          <div class="message-header"><p><em>{{ targetName }}</em> already exists</p></div>' +
    '          <div class="message-body">' +
    '            <div class="content-container">' +
    '              <p>Please choose a different name, or check <strong>Confirm Existing File Overwrite</strong></p>' +
    '            </div>' +
    '            <div class="field">' +
    '              <div class="control">' +
    '                <label class="checkbox">' +
    '                  <input type="checkbox" v-model="confirmExistingFileOverwrite">Confirm Existing File Overwrite' +
    '                </label>' +
    '              </div>' +
    '            </div>' +
    '          </div>' +
    '        </article>' +
    '      </transition>' +
    '    </section>' +
    '    <footer class="modal-card-foot">' +
    '      <button class="button is-primary is-rounded" @click.prevent="convert()" :disabled="convertButtonDisabled"  :class="{\'is-loading\': convertInProgress}">Convert</button>' +
    '      <button class="button is-rounded" :disabled="convertInProgress" @click.prevent="hide()">Cancel</button>' +
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
    '      <button class="button is-primary is-rounded" @click.prevent="hide()" :disabled="uploadInProgress"  :class="{\'is-loading\': uploadInProgress}">Done</button>' +
    '    </footer>' +
    '  </div>' +
    '</div>'
})

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
      jsonFetch(this.sourceLinkUrl, {
        document_id: this.docIdOrUrl,
        source_type: 'gdoc',
        directory: this.directory
      }, (success, errorMessage) => {
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
    '      <button class="button is-primary is-rounded" @click.prevent="performLink()" :disabled="inProgress"  :class="{\'is-loading\': inProgress}">Link</button>' +
    '      <button class="button is-rounded" :disabled="inProgress" @click.prevent="hide()">Cancel</button>' +
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
    pullFiles () {
      this.pullInProgress = true
      fetch(this.filePullUrl, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'X-CSRFToken': utils.cookie('csrftoken'),
        },
        credentials: 'same-origin'
      }).then(
        response => {
          this.pullInProgress = false
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
    showLinkModal (providerTypeId, linkType) {
      if (g_supportedSocialProviders[providerTypeId] !== true) {

        let providerTypeName = ''

        if (providerTypeId === 'google') {
          providerTypeName = 'Google'
        }

        fileBrowser.$root.$emit('unsupported-social-provider-modal-show', providerTypeName)
        return
      }

      if (linkType === 'gdoc') {
        fileBrowser.$root.$emit('googledocs-link-modal-show')
      }
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
      }while((el = el.parentNode) != null)
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

