Vue.component('user-autocomplete', {
    template: '<b-field>\n' +
        '            <b-autocomplete\n' +
        '                    v-model.lazy="nameSearch"\n' +
        '                    :data="data"\n' +
        '                    placeholder="Begin typing name"\n' +
        '                    icon="magnify"\n' +
        '                    name="name"\n' +
        '                    @select="usernameSelected()"\n' +
        '                    @input="usernameSelected()">\n' +
        '                <template slot="empty">[[ noResultsMessage ]]</template>\n' +
        '            </b-autocomplete>\n' +
        '        </b-field>',
    delimiters: ['[[', ']]'],
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
            fetch(`/api/v1/users/search?q=${query}`).then(response => {
                return response.json()
            }, (response) => {
                console.error(response)
            }).then(data => {
                this.data = data.map((item) => {
                    return item.username
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