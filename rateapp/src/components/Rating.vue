<template>
    <div class="flex w-1/2">
        <list class="w-1/3 bg-green-500" :list="filteredRating(3)" :rating="3"></list>
        <list class="w-1/3 bg-yellow-500" :list="filteredRating(4)" :rating="4"></list>
        <list class="w-1/3 bg-red-500" :list="filteredRating(5)" :rating="5"></list>
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
        methods: {
            filteredRating(rating_number) {
                let rankings = this.ratingResults.rankings;
                let list = [];
                _.forEach(rankings, function (ranking) {
                    _.forOwn(ranking.ranking, function (value, key) {
                        if (value === rating_number) {
                            list.push(key);
                        }
                    });
                });

                return list;
            }
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
