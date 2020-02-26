let g_projectEventTypeLookup = null

function getProjectEventDescription (shortType) {
  if (g_projectEventTypeLookup === null) {
    g_projectEventTypeLookup = {}
    g_projectEventTypes.forEach((typeAndDescription) => {
      g_projectEventTypeLookup[typeAndDescription[0]] = typeAndDescription[1]
    })
  }

  return g_projectEventTypeLookup[shortType]
}

function longDate(dateString) {
  return moment(dateString).format('YYYY-MM-DD HH:mm:ssZ')
}

Vue.component('event-log-message', {
  props: {
    message: {
      required: false
    }
  },
  filters: {

  },
  computed: {
    tag () {
      if (!this.message.tag)
        return ''

      return this.message.tag
    },
    time () {
      if (!this.message.time)
        return ''

      return longDate(this.message.time)
    },
    messageBody () {
      if (Array.isArray(this.message)) {
        let output = ''

        this.message.forEach((v) => {
          if (typeof v === 'string')
            output += v
          else
            output += JSON.stringify(v)
        })
        return output
      }

      if(typeof this.message === 'string')
        return this.message

      if (!this.message.message)
        return ''

      return this.message.message
    },
    level () {
      if (this.message.level === undefined)
        return 2

      return this.message.level
    },
    levelClass () {
      const c = ['is-danger', 'is-warning', 'is-info', 'is-success'][this.level]
      return {[c]: true}
    }
  },
  template: '' +
    '<article class="message is-small" :class="levelClass">' +
    '  <div class="message-header">' +
    '    <p><strong>{{ this.tag }}</strong> {{ this.time }}</p>' +
    '  </div>' +
    '  <div class="message-body">' +
    '    {{ this.messageBody }}' +
    '  </div>' +
    '</article>'
})

Vue.component('event-detail-modal', {
  props: {
    visible: {
      type: Boolean,
      required: true
    },
    event: {
      type: Object,
      required: false,
      default: {}
    }
  },
  methods: {
    hideDetailModal () {
      this.$root.$emit('hide-detail-modal')
    }
  },
  computed: {
    log () {
      if (!this.event.log)
        return []

      if (typeof this.event.log === 'string')
        return [this.event.log]

      return this.event.log
    }
  },
  template: '' +
    '<b-modal :active="visible" :width="640" scroll="keep" :can-cancel="[\'escape\', \'outside\']" @close="hideDetailModal()">' +
    '  <header class="modal-card-head">' +
    '    <p class="modal-card-title"><slot name="title"></slot></p>' +
    '    <button class="delete" aria-label="close" @click="hideDetailModal()"></button>' +
    '  </header>' +
    '  <section class="modal-card-body">' +
    '    <h5 class="title is-5">Message</h5>' +
    '    <p class="has-bottom-margin">{{ event.message }}</p>' +
    '    <h5 v-if="log.length" class="title is-5">Log Messages</h5>' +
    '    <event-log-message :key="index" v-for="(message, index) in log" :message="message"></event-log-message>' +
    '  </section>' +
    '  <footer class="modal-card-foot">' +
    '    <a class="button" href="#" @click.prevent="hideDetailModal()">Close</a>' +
    '  </footer>' +
    '</b-modal>',
})

Vue.component('event-row', {
  props: {
    event: {
      type: Object,
      required: true,
    },
    displayProjectColumn: {
      type: Boolean,
      required: false,
      default: false
    }
  },
  computed: {
    successIcon: function () {
      const isSuccess = this.event.success
      if (isSuccess === null)
        return '&mdash;'

      const iconClass = isSuccess ? 'check' : 'times'
      const colorClass = isSuccess ? '' : 'has-text-danger'

      return `<span class="icon ${colorClass}">` +
        `<i class="fas fa-${iconClass}-circle"></i>` +
        '</span>'
    },
    hasLog() {
      return Object.keys(this.event.log).length > 0
    }
  },
  filters: {
    eventDescription: function (shortType) {
      return getProjectEventDescription(shortType)
    },
    longDate: function (dateString) {
      if (dateString === null)
        return '—'

      return longDate(dateString)
    },
    eventMessage (message) {
      if (message === null)
        return '-'
      const originalLength = message.length
      message = message.substring(0, 100)
      message = message.split(' ').slice(0, 10).join(' ')
      if (message.length < originalLength)
        message += '…'
      return message
    }
  },
  methods: {
    showMessageModal () {
      this.$emit('show-detail-modal', event)
    }
  },
  template: '' +
    '<tr>' +
    '  <td v-if="displayProjectColumn">{{ event.project.name }}</td>' +
    '  <td>{{ event.event_type | eventDescription }}</td>' +
    '  <td>{{ event.started  | longDate }}</td>' +
    '  <td>{{ event.finished | longDate }}</td>' +
    '  <td class="has-text-centered" v-html="successIcon"></td>' +
    '  <td>{{ event.message | eventMessage }}' +
    '   <br/><a v-if="(event.message && event.message.length) || hasLog" @click="showMessageModal()">Details</a></td>' +
    '</tr>'
})

const projectEventList = new Vue({
  el: '#project-activity-view',
  data: {
    events: [],
    currentUrl: g_eventApiUrl,
    nextUrl: null,
    previousUrl: null,
    fetchInProgress: false,
    projectEventTypes: g_projectEventTypes,
    eventFilter: '',
    successFilter: '',
    detailModalVisible: false,
    detailModalEvent: {},
    displayProjectColumn: g_displayProjectColumn,
    originalUrl: ''
  },
  methods: {
    loadEvents (isFilterChange) {
      if (this.fetchInProgress)
        return

      const splitUrl = this.currentUrl.split('?')

      let params
      if(splitUrl.length > 1)
        params = new URLSearchParams(splitUrl[1])
      else
        params = new URLSearchParams()

      if (isFilterChange) {
        if (params.has('limit'))
          params.delete('limit')

        if (params.has('offset'))
          params.delete('offset')
      }

      if (this.eventFilter !== '') {
        params.set('event_type', this.eventFilter)
      } else if (params.has('event_type')) {
        params.delete('event_type')
      }

      if (this.successFilter !== '') {
        params.set('success', this.eventFilter)
      } else if (params.has('success')) {
        params.delete('success')
      }

      this.fetchInProgress = true
      fetch(`${this.originalUrl}?${params.toString()}`).then((response) => {
        this.fetchInProgress = false
        return response.json()
      }).then((data) => {
        this.events = data.results
        this.nextUrl = data.next
        this.previousUrl = data.previous
      }).catch(() => {
        this.fetchInProgress = false
      })
    },
    loadPrevious () {
      this.currentUrl = this.previousUrl
      this.loadEvents()
    },
    loadNext () {
      this.currentUrl = this.nextUrl
      this.loadEvents()
    },
    showDetailModal (event) {
      this.detailModalEvent = event
      this.detailModalVisible = true
    },
    hideDetailModal () {
      this.detailModalVisible = false
    },
  },
  computed: {
     loadingColspan() {
      return this.displayProjectColumn ? 6: 5
    }
  },
  mounted () {
    this.originalUrl = this.currentUrl
    this.loadEvents()
    this.$root.$on('hide-detail-modal', () => {
      this.hideDetailModal()
    })
  },
  template: '' +
    '<div>' +
    '<event-detail-modal :visible.sync="detailModalVisible" :event="detailModalEvent"></event-detail-modal>' +
    '<div class="columns">' +
    '  <div class="column">' +
    '   <div class="field">' +
    '     <label class="label">Event Type</label>' +
    '     <div class="control">' +
    '       <select @change="loadEvents(true)" class="select" v-model="eventFilter">' +
    '         <option value="">All</option>' +
    '         <option :key="index" v-for="(item, index) in projectEventTypes" :value="item[0]">{{ item[1] }}</option>' +
    '       </select>' +
    '     </div>' +
    '   </div>' +
    '  </div>' +
    '  <div class="column">' +
    '   <div class="field">' +
    '     <label class="label">Success</label>' +
    '     <div class="control">' +
    '       <select @change="loadEvents()" class="select" v-model="successFilter">' +
    '         <option value="">Any</option>' +
    '         <option value="true">Yes</option>' +
    '         <option value="false">No</option>' +
    '         <option value="null">Unfinished</option>' +
    '       </select>' +
    '     </div>' +
    '   </div>' +
    '  </div>' +
    '</div>' +
    '<table class="table is-fullwidth is-bordered is-striped">' +
    '  <thead>' +
    '    <tr>' +
    '      <th v-if="displayProjectColumn">Project</th>' +
    '      <th>Type</th>' +
    '      <th>Started</th>' +
    '      <th>Finished</th>' +
    '      <th>Success</th>' +
    '      <th>Message</th>' +
    '    </tr>' +
    '  </thead>' +
    '  <tbody>' +
    '  <event-row v-if="!fetchInProgress" v-for="event in events" :key="event.pk" :event="event" ' +
    '   :display-project-column="displayProjectColumn" v-on:show-detail-modal="showDetailModal(event)" ' +
    '   v-on:hide-detail-modal="hideDetailModal()"/>' +
    '  <tr v-if="fetchInProgress || events.length === 0">' +
    '    <td :colspan="loadingColspan">' +
    '      <span v-if="!fetchInProgress">No events found.</span>' +
    '      <span v-if="fetchInProgress">Loading events.</span>' +
    '    </td>' +
    '  </tr>' +
    '  </tbody>' +
    '</table>' +
    '<button class="button" @click="loadPrevious" :disabled="fetchInProgress || previousUrl === null">Previous</button>' +
    '<button class="button is-pulled-right" @click="loadNext" :disabled="fetchInProgress || nextUrl === null">Next</button>' +
    '</div>'
})