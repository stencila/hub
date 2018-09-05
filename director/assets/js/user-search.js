Vue.component('user-autocomplete', {
    template: '<b-field>\n' +
        '            <b-autocomplete\n' +
        '                    v-model.lazy="nameSearch"\n' +
        '                    :data="data"\n' +
        '                    placeholder="Begin typing name"\n' +
        '                    icon="magnify"\n' +
        '                    name="name"\n' +
        '                    @select="option => selected = option">\n' +
        '                <template slot="empty">No results found</template>\n' +
        '            </b-autocomplete>\n' +
        '        </b-field>',
    delimiters: ['[[', ']]'],
    data() {
        return {
            data: [],
            nameSearch: '',
            selected: null,
            searchTimeout: null,
        }
    },
    watch: {
        nameSearch() {
            if (this.searchTimeout) {
                clearTimeout(this.searchTimeout)
            }

            if (this.nameSearch.length >= 3) {
                let query = this.nameSearch
                this.searchTimeout = setTimeout(() => {
                    this.performSearch(query)
                }, 500)
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
    }
})