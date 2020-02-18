Vue.component('snapshot-item-action-menu', {
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
  mounted () {
    this.$root.$on('menu-hide', () => {
      this.active = false
    })
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
  },
  template: '' +
    '<div class="dropdown item-actions-dropdown" @click="toggle()" :class="{ \'is-active\':active }">' +
    '  <div class="dropdown-trigger">' +
    '    <a aria-haspopup="true" :aria-controls="\'item-actions-menu-\' + index"><i class="fa fa-ellipsis-h"></i></a>' +
    '  </div>' +
    '  <div class="dropdown-menu" id="\'item-actions-menu-\' + index" role="menu">' +
    '    <div class="dropdown-content">' +
    '      <a v-if="downloadUrl != \'\'" :href="downloadUrl" class="dropdown-item">Download</a>' +
    '      <a v-if="viewUrl != \'\'" :href="viewUrl" class="dropdown-item">View</a>' +
    '    </div>' +
    '  </div>' +
    '</div>'
})

const snapshotFileBrowser = new Vue({
  el: '#snapshot-file-browser'
})