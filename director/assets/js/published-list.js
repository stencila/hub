Vue.component('published-action-menu', {
  props: {
    index: {
      type: String,
      required: true
    },
    urlPath: {
      type: String,
      required: true
    },
    itemPk: {
      type: String,
      required: true
    },
    deleteAction: {
      type: String,
      required: true
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
  methods: {
    toggle () {
      if (this.active) {
        this.active = false
      } else {
        this.$root.$emit('menu-hide')
        this.active = true
      }
    },
    showDeleteModal () {
      this.$root.$emit('delete-modal-show', this.itemPk, this.urlPath, this.deleteAction)
    }
  },

  template: '' +
    '<div class="dropdown item-actions-dropdown" @click="toggle()" :class="{ \'is-active\':active }">' +
    '  <div class="dropdown-trigger">' +
    '    <a aria-haspopup="true" :aria-controls="\'item-actions-menu-\' + index"><i class="fa fa-ellipsis-h"></i></a>' +
    '  </div>' +
    '  <div class="dropdown-menu" id="\'item-actions-menu-\' + index" role="menu">' +
    '    <div class="dropdown-content">' +
    '      <a class="dropdown-item" href="#" @click.prevent="showDeleteModal()">Unpublish&hellip;</a> ' +
    '    </div>' +
    '  </div>' +
    '</div>'
})

var publishedItem = new Vue({
  el: '#published-items',
  delimiters: ['[[', ']]'],
  data: {
    deleteItemPk: null,
    deleteModalVisible: false,
    publishedItemDescription: '',
    deleteFormAction: ''
  },
  created() {
    this.$root.$on('delete-modal-show', (publishedItemPk, publishedItemDescription, deleteAction) => {
      this.deleteItemPk = publishedItemPk
      this.publishedItemDescription = publishedItemDescription
      this.deleteModalVisible = true
      this.deleteFormAction = deleteAction
    })
  },
  methods: {
    hideDeleteModal() {
      this.deleteModalVisible = false
    },
    unpublishComplete: function (request) {
      if (request.status >= 200 && request.status < 300)
        window.location.reload()
    }
  }
})