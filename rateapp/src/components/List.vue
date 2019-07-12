<template>
    <div>
        <h3>
            <span class="heading">{{this.header_string}}</span><br/>
            <span>zoekresultaten</span>
        </h3>
        <drop class="drop h-full p-3" @drop="handleDrop(filteredRating(ratingResults), ...arguments)">
            <drag v-for="result in filteredRating(ratingResults)"
                  class="drag card card-small"
                  :key="result.id"
                  :transfer-data="getDocumentData(result.reference)">
                <div @click="remove(result.id)" class="remove">x</div>
                <h6 class="font-bold">{{getDocumentData(result.reference) ? getDocumentData(result.reference)._source.title : result.id}}</h6>
                <div v-if="getDocumentData(result.reference)">
                    <a :href="getDocumentData(result.reference)._source.url" target="_blank">{{getDocumentData(result.reference)._source.url}}</a>
                </div>
                <div class="meta-info">
                    <span>Type: {{getDocumentData(result.reference)._source.mime_type}}</span>
                    <span>Collection: {{getDocumentData(result.reference)._source.arrangement_collection_name}}</span>
                </div>
            </drag>
        </drop>
    </div>
</template>

<script>
    import {Drag, Drop} from 'vue-drag-drop';
    import {mapGetters} from 'vuex';
    import _ from 'lodash';

    export default {
        name: 'List',
        components: {Drag, Drop},
        props: {
            rating: {
                type: Number,
                required: true
            },
            header_string: {
                type: String,
                required: true
            }
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
                            let split = key.split(":");
                            let index = split[0];
                            let reference = split[1];

                            list.push({
                                id: key,
                                index: index,
                                reference: reference
                            });
                        }
                    });
                });

                return list;
            },
            remove(id) {
                this.$store.dispatch('rating/removeRating', id);
                this.$nextTick(this.$forceUpdate());
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
