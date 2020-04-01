Vue.component('snapshot-item-action-menu', {
  mixins: [g_fileActionsCommon],
  props: {
    downloadUrl: {
      type: String,
      required: false,
      default: ''
    },
    viewUrl: {
      type: String,
      required: false,
      default: ''
    },
    index: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      active: false
    }
  },
  template: '' +
    '<div class="dropdown item-actions-dropdown" @click="toggle()" :class="{ \'is-active\':active }">' +
    '  <div class="dropdown-trigger">' +
    '    <a aria-haspopup="true" :aria-controls="\'item-actions-menu-\' + index"><i class="fa fa-ellipsis-h"></i></a>' +
    '  </div>' +
    '  <div class="dropdown-menu" id="\'item-actions-menu-\' + index" role="menu">' +
    '    <div class="dropdown-content">' +
    '      <a v-if="downloadUrl != \'\'" :href="downloadUrl" class="dropdown-item"><span class="icon"><i class="fas fa-download"></i></span>Download</a>' +
    '      <a v-if="viewUrl != \'\'" :href="viewUrl" class="dropdown-item"><span class="icon"><i class="fas fa-external-link-alt"></i></span>Open</a>' +
    '      <a v-if="allowPreview" :href="previewUrl" class="dropdown-item" target="_blank" rel="noopener"><span class="icon"><i class="fas fa-eye"></i></span>Preview</a>' +
    '    </div>' +
    '  </div>' +
    '</div>'
})

const snapshotFileBrowser = new Vue({
  el: '#snapshot-file-browser'
})