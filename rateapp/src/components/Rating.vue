<template>
    <div class="rating">
        <list class="w-1/3 list orange" :rating="3" :header_string="'Minst relevante'"></list>
        <list class="w-1/3 list blue" :rating="4" :header_string="'Relevante'"></list>
        <list class="w-1/3 list green" :rating="5" :header_string="'Meest relevante'"></list>
    </div>
</template>

<script>
    import List from "@/components/List.vue";
    import {mapGetters} from 'vuex';
    import _ from 'lodash';

    export default {
        name: 'rating',
        components: {
            List
        },
        data() {
            return {}
        },
        computed: {
            ...mapGetters("rating",
                [
                    "ratingStatus",
                    "ratingDocumentStatus",
                    "ratingQuery",
                    "ratingSubquery",
                    "ratingResults",
                    "ratingDocuments"
                ]),
        }
    }
</script>
