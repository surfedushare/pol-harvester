<template>
    <drop class="drop list" @drop="handleDrop(filteredRating(ratingResults), ...arguments)">
        <drag v-for="result in filteredRating(ratingResults)"
              class="drag"
              :key="result"
              :transfer-data="getDocumentData(result)">
            {{getDocumentData(result)._source.title}}
        </drag>
    </drop>
</template>

<script>
    import {Drag, Drop} from 'vue-drag-drop';
    import {mapGetters} from 'vuex';
    import _ from 'lodash';

    export default {
        name: 'List',
        components: {Drag, Drop},
        props: ['rating'],
        data() {
            return {
                list: []
            };
        },
        methods: {
            handleDrop(toList, document) {
                this.$store.dispatch('rating/addRating', {document: document, rating: this.rating});
                this.$nextTick(this.$forceUpdate());
            },
            getDocumentData(id) {
                let documents = this.ratingDocuments;
                return _.find(documents, {'_id': id});
            },
            filteredRating(rankings) {
                let rating = this.rating;
                let deep_rankings = rankings.rankings;
                let list = [];
                _.forEach(deep_rankings, function (ranking) {
                    _.forOwn(ranking.ranking, function (value, key) {
                        if (value === rating) {
                            list.push(key);
                        }
                    });
                });

                return list;
            }
        },
        computed: {
            ...mapGetters("rating", [
                "ratingDocuments",
                "ratingResults"
            ]),
        }
    };
</script>
