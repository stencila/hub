Vue.component('event-row', {
  props: {
    event: {
      type: Object,
      required: true
    }
  },
  template: '' +
    '<tr>' +
    '  <td>{{ event.event_type }}</td>' +
    '  <td>{{ event.started }}</td>' +
    '  <td>{{ event.finished }}</td>' +
    '  <td>{{ event.success }}</td>' +
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
    fetchInProgress: false
  },
  methods: {
    loadEvents () {
      if (this.fetchInProgress)
        return;
      this.fetchInProgress = true
      fetch(this.currentUrl).then((response) => {
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
    }
  },
  mounted (){
    this.loadEvents()
  },
  template: '' +
    '<div>' +
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
    '  <tr v-if="events.length === 0">' +
    '    <td colspan="5">No events found.</td>' +
    '  </tr>' +
    '  </tbody>' +
    '</table>' +
    '<button class="button" @click="loadPrevious" :disabled="fetchInProgress || previousUrl === null">Previous</button>' +
    '<button class="button is-pulled-right" @click="loadNext" :disabled="fetchInProgress || nextUrl === null">Next</button>' +
    '</div>'
})