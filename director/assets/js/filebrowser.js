function rootPathJoin (directory, fileName) {
  let joiner = ''

  if (directory.length !== 0 && directory.substring(directory.length - 1, 1) !== '/') {
    joiner = '/'
  }
  return '/' + directory + joiner + fileName
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
    editorPath: {
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
      return this.allowDelete || this.allowRename
    },
    shouldDisplayDivider () {
      return (this.allowDesktopLaunch || this.allowEdit) && (this.allowDelete || this.allowRename)
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
    launchCodeEditor () {
      if (this.editorPath !== '') {
        window.location = this.editorPath
      }
    },
    launchDesktopEditor () {
      sessionWaitController.launchDesktopEditor(this.absolutePath)
    }
  },
  template: '' +
    '<div v-if="shouldDisplay" class="dropdown item-actions-dropdown" @click="toggle()" :class="{ \'is-active\':active }">' +
    '  <div class="dropdown-trigger">' +
    '    <a aria-haspopup="true" :aria-controls="\'item-actions-menu-\' + index"><i class="fa fa-ellipsis-h"></i></a>' +
    '  </div>' +
    '  <div class="dropdown-menu" id="\'item-actions-menu-\' + index" role="menu">' +
    '    <div class="dropdown-content">' +
    '      <a v-if="allowEdit" href="#" class="dropdown-item" @click.prevent="launchCodeEditor()">Open in Code Editor</a>' +
    '      <a v-if="allowDesktopLaunch" href="#" class="dropdown-item" @click.prevent="launchDesktopEditor()">Open in Stencila Desktop</a>' +
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
    renameItemVisible: false
  },
  mounted () {
    this.filePullUrl = this.$refs['file-browser-root'].getAttribute('data-file-pull-url')
    this.itemCreateUrl = this.$refs['file-browser-root'].getAttribute('data-item-create-url')
    this.itemRenameUrl = this.$refs['file-browser-root'].getAttribute('data-item-rename-url')
    this.itemRemoveUrl = this.$refs['file-browser-root'].getAttribute('data-item-remove-url')
  },
  created () {
    let jsonFetch = (url, body, callback) => {
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