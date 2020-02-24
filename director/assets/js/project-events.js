let g_projectEventTypeLookup = null

function getProjectEventDescription(shortType) {
  if (g_projectEventTypeLookup === null) {
    g_projectEventTypeLookup = {}
    g_projectEventTypes.forEach((typeAndDescription) => {
      g_projectEventTypeLookup[typeAndDescription[0]] = typeAndDescription[1]
    })
  }

  return g_projectEventTypeLookup[shortType]
}

Vue.component('event-row', {
  props: {
    event: {
      type: Object,
      required: true,
    }
  },
  computed: {
    successIcon: function () {
      const isSuccess = this.event.success
      if (isSuccess === null)
        return '&mdash;'

      const iconClass = isSuccess ? 'check' : 'cross'
      const colorClass = isSuccess ? '' : 'has-text-danger'

      return `<span class="icon ${colorClass}">` +
        `<i class="fas fa-${iconClass}-circle"></i>` +
        '</span>'
    }
  },
  filters: {
    eventDescription: function (shortType) {
      return getProjectEventDescription(shortType)
    },
    longDate: function (dateString) {
        if(dateString === null)
          return '—'

      return moment(dateString).format('YYYY-MM-DD HH:mm:ssZ')
    },

  },
  template: '' +
    '<tr>' +
    '  <td>{{ event.event_type | eventDescription }}</td>' +
    '  <td>{{ event.started  | longDate }}</td>' +
    '  <td>{{ event.finished | longDate }}</td>' +
    '  <td class="has-text-centered" v-html="successIcon"></td>' +
    '  <td>{{ event.message }}</td>' +
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
    successFilter: ''

  },
  methods: {
    loadEvents () {
      if (this.fetchInProgress)
        return

      const filters = {}

      if (this.eventFilter !== '') {
        filters['event_type'] = this.eventFilter
      }

      if (this.successFilter !== '') {
        filters['success'] = this.successFilter
      }

      const queryString = Object.keys(filters).map((key) => {
        return encodeURIComponent(key) + '=' + encodeURIComponent(filters[key])
      }).join('&')

      this.fetchInProgress = true
      fetch(`${this.currentUrl}?${queryString}`).then((response) => {
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
    loadPrevious() {
      this.currentUrl = this.previousUrl
      this.loadEvents()
    },
    loadNext() {
      this.currentUrl = this.nextUrl
      this.loadEvents()
    },
  },
  mounted (){
    this.loadEvents()
  },
  template: '' +
    '<div>' +
    '<div class="columns">' +
    '  <div class="column">' +
    '   <div class="field">' +
    '     <label class="label">Event Type</label>' +
    '     <div class="control">' +
    '       <select @change="loadEvents()" class="select" v-model="eventFilter">' +
    '         <option value="">All</option>' +
    '         <option :key="index" v-for="(item, index) in projectEventTypes" :value="item[0]">{{ item[1] }}</option>' +
    '       </select>' +
    '     </div>' +
    '   </div>' +
    '  </div>' +
    '  <div class="column">' +
    '   <div class="field">' +
    '     <label class="label">Successful</label>' +
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
    '<table class="table is-fullwidth is-bordered">' +
    '  <thead>' +
    '    <tr>' +
    '      <th>Type</th>' +
    '      <th>Started</th>' +
    '      <th>Finished</th>' +
    '      <th>Success</th>' +
    '      <th>Message</th>' +
    '    </tr>' +
    '  </thead>' +
    '  <tbody>' +
    '  <event-row v-for="event in events" :key="event.pk" :event="event"/>' +
    '  <tr v-if="fetchInProgress || events.length === 0">' +
    '    <td colspan="5">' +
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