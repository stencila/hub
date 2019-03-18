Vue.component('delete-confirm-modal', {
    template: '<b-modal :active.sync="deleteModalVisible" :width="640" scroll="keep">\n' +
        '            <header class="modal-card-head">\n' +
        '                <p class="modal-card-title"><slot name="title"></slot></p>\n' +
        '            </header>\n' +
        '            <section class="modal-card-body">\n' +
        '                <slot name="body"></slot>' +
        '            </section>\n' +
        '            <footer class="modal-card-foot">\n' +
        '                <form class="form" method="POST" :action="formAction">\n' +
        '                    <slot name="csrf_token"></slot>\n' +
        '                    <input type="hidden" :name="deleteIdName" value="" v-model="deleteIdValue">\n' +
        '                    <button class="button is-danger is-rounded" type="submit" name="action" :value="deleteAction">\n' +
        '                        [[ deleteButtonLabel ]]\n' +
        '                    </button>\n' +
        '                    <a class="button is-rounded call-to-action" href="#" @click.prevent="hideDeleteModal()">Cancel</a>\n' +
        '                </form>\n' +
        '            </footer>\n' +
        '        </b-modal>',
    delimiters: ['[[', ']]'],
    data() {
        return {
            formAction: ''
        }
    },
    props: {
        deleteModalVisible: {
            required: true,
            type: Boolean
        },
        deleteAction: {
            required: true,
            type: String
        },
        deleteButtonLabel: {
            required: true,
            type: String
        },
        deleteIdName: {
            required: true,
            type: String
        },
        deleteIdValue: {
            required: true
        },
        formAction: {
            required: false,
            type: String
        }
    },
    methods: {
        hideDeleteModal() {
           this.$emit('modal-hide')
        }
    }
})