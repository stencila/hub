Vue.component('user-autocomplete', {
    template: '<b-field>\n' +
        '            <b-autocomplete\n' +
        '                    v-model.lazy="nameSearch"\n' +
        '                    :data="data"\n' +
        '                    placeholder="Search for a user"\n' +
        '                    icon="search"\n' +
        '                    name="name"\n' +
        '                    @select="usernameSelected()"\n' +
        '                    @input="usernameSelected()">\n' +
        '                <template slot="empty">[[ noResultsMessage ]]</template>\n' +
        '            </b-autocomplete>\n' +
        '        </b-field>',
    delimiters: ['[[', ']]'],
    beforeMount() {
        this.$buefy.setOptions({defaultIconPack: 'fas'})
    },
    props: {
        'skipResults': {
            type: Array,
            required: false,
            default: function () {
              return []
            }
        }
    },
    data() {
        return {
            data: [],
            nameSearch: '',
            selected: null,
            searchTimeout: null,
            noResultsMessage: "No results found"
        }
    },
    watch: {
        nameSearch() {
            if (this.searchTimeout) {
                clearTimeout(this.searchTimeout)
            }

            if (this.nameSearch.length >= 3) {
                this.noResultsMessage = "No results found"
                let query = this.nameSearch
                this.searchTimeout = setTimeout(() => {
                    this.performSearch(query)
                }, 500)
            } else {
                this.noResultsMessage = "Please type at least 3 characters."
            }
        }
    },
    methods: {
        performSearch(query) {
            fetch(`/api/users?q=${query}`).then(response => {
                return response.json()
            }, (response) => {
                console.error(response)
            }).then(data => {
                this.data = data.results.map((item) => {
                    return item.username
                }).filter((username) => {
                    return this.skipResults.indexOf(username) === -1;
                })
            })
        },
        usernameSelected(username) {
            if (typeof username === "undefined")
                username = this.nameSearch
            this.$emit('username-selected', username)
        }
    }
})