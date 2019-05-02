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
  })
}

function extensionFromType (type) {
  if (type === 'markdown') {
    return '.md'
  }

  if (type === 'html') {
    return '.html'
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
      default: ''
    },
    sourceType: {
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
  mounted () {
    this.$root.$on('menu-hide', () => {
      this.active = false
    })
  },
  computed: {
    shouldDisplay () {
      return this.allowDelete || this.allowRename || this.allowEdit || this.convertTargets.length
    },
    shouldDisplayDivider () {
      return (this.allowDesktopLaunch || this.allowEdit || this.convertTargets.length) && (this.allowDelete || this.allowRename)
    },
    convertTargets () {
      if (this.fileType === 'text/html' || this.fileType === 'text/markdown') {
        return [
          ['googledocs', 'Google Docs']
        ]
      }

      if (this.fileType === 'application/vnd.google-apps.document') {
        return [
          ['html', 'HTML'],
          ['markdown', 'Markdown']
        ]
      }

      return []
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
      this.$root.$emit('rename-item-show', this.fileName, 'Rename')
    },
    showRemoveModal () {
      this.$root.$emit('remove-item-show', this.fileName)
    },
    launchDesktopEditor () {
      sessionWaitController.launchDesktopEditor(this.absolutePath)
    },
    startConvert (targetType, targetTypeName) {
      this.$root.$emit('convert-modal-show', targetType, targetTypeName, this.sourceIdentifier, this.fileName, this.absolutePath)
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
    '      <a v-for="convertTarget in convertTargets" href="#" class="dropdown-item" @click.prevent="startConvert(convertTarget[0], convertTarget[1])">Convert to {{ convertTarget[1] }}&hellip;</a>' +
    '      <hr v-if="shouldDisplayDivider" class="dropdown-divider">' +
    '      <a v-if="allowRename" href="#" class="dropdown-item" @click.prevent="showRenameModal()">Rename&hellip;</a>' +
    '      <a v-if="allowDelete" href="#" class="dropdown-item" @click.prevent="showRemoveModal()">Delete&hellip;</a>' +
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
    this.$root.$on('remove-item-show', (itemName) => {
      this.itemName = itemName
      this.visible = true
    })
  },
  template: '' +
    '<div class="modal" :class="{\'is-active\': visible}">' +
    '  <div class="modal-background"></div>' +
    '  <div class="modal-card">' +
    '    <header class="modal-card-head">' +
    '      <p class="modal-card-title">Delete <em>{{ itemName }}</em>?</p>' +
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
    },
    visible: {
      type: Boolean,
      required: true
    }
  },
  data () {
    return {
      itemName: '',
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
    this.$root.$on('rename-item-show', (itemName, action) => {
      this.itemName = itemName
      this.action = action
      this.destination = this.currentPath
      this.visible = true
    })
  },
  template: '' +
    '<div class="modal" :class="{\'is-active\': visible}">' +
    '  <div class="modal-background"></div>' +
    '  <div class="modal-card">' +
    '    <header class="modal-card-head">' +
    '      <p class="modal-card-title">{{ action }} Item</p>' +
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
    '      <button class="button is-primary" @click.prevent="performRename()" :disabled="inProgress"  :class="{\'is-loading\': inProgress}">{{ action }}</button>' +
    '      <button class="button" :disabled="inProgress" @click.prevent="hide()">Cancel</button>' +
    '    </footer>' +
    '  </div> ' +
    '</div>'
})

Vue.component('add-item-modal', {
  props: {
    itemType: {
      type: String,
      required: true,
    },
    directoryPath: {
      type: String,
      required: true
    },
  },
  data () {
    return {
      visible: false,
      itemName: '',
      createInProgress: false,
      errorMessage: null
    }
  },
  mounted () {
    this.$root.$on('add-item-show', this.show)
  },
  computed: {
    fullPath () {
      return rootPathJoin(this.directoryPath, this.itemName)
    }
  },
  methods: {
    show () {
      this.visible = true
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
    '                    <p class="modal-card-title">New {{ itemType }}</p>' +
    '                    <button class="delete" aria-label="close" @click="hide()"></button>' +
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
  },
  methods: {
    hide () {
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
          alert(errorMessage)
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
    '      <p class="modal-card-title">Convert to {{ targetTypeName }}</p>' +
    '      <button class="delete" aria-label="close" @click="hide()"></button>' +
    '    </header>' +
    '    <section class="modal-card-body">' +
    '      <div class="content-container">' +
    '        <p>File <em>{{ sourceName }}</em> will be converted to {{ targetTypeName }}. The original file will be preserved.</p>' +
    '      </div>' +
    '      <div class="field">' +
    '        <div class="control">' +
    '          <label class="label">Enter a name for the converted file</label>' +
    '          <input class="input is-medium" type="text" placeholder="Converted File Name" v-model="targetName" @keypress="nameChange()">' +
    '          <p v-if="errorMessage != null" class="has-text-danger">{{ errorMessage }}</p>' +
    '        </div>' +
    '      </div>' +
    '      <article class="message is-warning" v-if="hasFilenameConflict">' +
    '        <div class="message-header"><p><em>{{ targetName }}</em> already exists</p></div>' +
    '        <div class="message-body">' +
    '          <div class="content-container">' +
    '            <p>Please choose a different name, or check <strong>Confirm Existing File Overwrite</strong></p>' +
    '          </div>' +
    '          <div class="field">' +
    '            <div class="control">' +
    '              <label class="checkbox">' +
    '                <input type="checkbox" v-model="confirmExistingFileOverwrite">Confirm Existing File Overwrite' +
    '              </label>' +
    '            </div>' +
    '          </div>' +
    '        </div>' +
    '      </article>' +
    '    </section>' +
    '    <footer class="modal-card-foot">' +
    '      <button class="button is-primary" @click.prevent="convert()" :disabled="convertButtonDisabled"  :class="{\'is-loading\': convertInProgress}">Convert</button>' +
    '      <button class="button" :disabled="convertInProgress" @click.prevent="hide()">Cancel</button>' +
    '    </footer>' +
    '  </div>' +
    '</div>'
})

new Vue({
  el: '#file-browser',
  delimiters: ['[[', ']]'],
  data: {
    itemCreateUrl: null,
    itemRenameUrl: null,
    itemRemoveUrl: null,
    filePullUrl: null,
    newMenuVisible: false,
    linkMenuVisible: false,
    unlinkMenuVisible: false,
    deleteModalVisible: false,
    unlinkSourceId: null,
    unlinkSourceDescription: '',
    pullInProgress: false,
    createItemType: 'Folder',
    createItemVisible: false,
    renameItemVisible: false,
    fileList: g_fileList
  },
  mounted () {
    this.filePullUrl = this.$refs['file-browser-root'].getAttribute('data-file-pull-url')
    this.itemCreateUrl = this.$refs['file-browser-root'].getAttribute('data-item-create-url')
    this.itemRenameUrl = this.$refs['file-browser-root'].getAttribute('data-item-rename-url')
    this.itemRemoveUrl = this.$refs['file-browser-root'].getAttribute('data-item-remove-url')
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
  },
  methods: {
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
    resetMenus () {
      this.$root.$emit('menu-hide')
      this.linkMenuVisible = false
      this.unlinkMenuVisible = false
      this.newMenuVisible = false
    },
    createFile () {
      this.createItemType = 'File'
      this.createItemVisible = true
      this.$root.$emit('add-item-show')
    },
    createFolder () {
      this.createItemType = 'Folder'
      this.createItemVisible = true
      this.$root.$emit('add-item-show')
    },
    hideDeleteModal () {
      this.deleteModalVisible = false
    },
    showUnlinkModal (sourceDescription, sourceId) {
      this.unlinkSourceDescription = sourceDescription
      this.unlinkSourceId = sourceId
      this.deleteModalVisible = true
    }
  }
})