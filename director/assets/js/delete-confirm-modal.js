Vue.component('delete-confirm-modal', {
    template: '<b-modal :active.sync="deleteModalVisible" :width="640" scroll="keep">' +
        '            <header class="modal-card-head">' +
        '                <p class="modal-card-title"><slot name="title"></slot></p>' +
        '                <button class="delete" aria-label="close" @click="hideDeleteModal()"></button>' +
        '            </header>' +
        '            <section class="modal-card-body">' +
        '                <slot name="body"></slot>' +
        '            </section>' +
        '            <footer class="modal-card-foot">' +
        '                <form class="form" method="POST" :action="formAction">' +
        '                    <slot name="csrf_token"></slot>' +
        '                    <input type="hidden" :name="deleteIdName" value="" v-model="deleteIdValue">' +
        '                    <button class="button is-danger" type="submit" name="action" :value="deleteAction">' +
        '                        {{ deleteButtonLabel }}' +
        '                    </button>' +
        '                    <a class="button" href="#" @click.prevent="hideDeleteModal()">Cancel</a>' +
        '                </form>' +
        '            </footer>' +
        '        </b-modal>',
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
            type: String,
            default: ''
        }
    },
    methods: {
        hideDeleteModal() {
           this.$emit('modal-hide')
        }
    }
})