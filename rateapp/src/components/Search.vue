<template>
    <div class="search">
        <h2 v-if="!isSubQuery" class="text-2xl px-4 pt-4 font-bold">Zoeken</h2>
        <div v-if="!isSubQuery && hasRatingQuery && isLoggedIn"
             class="px-4">
            Je bent een ranking aan het maken voor:
            "<b class="text-xl">{{ratingQuery}}</b>"
            <button @click="reset()" class="btn px-2 py-0 bg-red-600">X</button>
        </div>
        <div v-else>
            <div class="flex flex-1 p-4">
                <input v-model="query"
                       v-on:keyup.enter="search"
                       class="input mr-2"
                       type="email" :placeholder="placeholder">
                <button @click="search" class="btn">Zoeken</button>
                <select v-if="!isSubQuery && isLoggedIn" class="ml-2 w-1/5 input"
                        @change="selectQuery($event)">
                    <option value="" disabled selected hidden>Vorige zoektermen</option>
                    <option v-for="query in ratedQueries" :key="query">{{query}}</option>
                </select>
            </div>
            <div class="bg-white p-4 results"
                 :class="isSubQuery ? 'results-sub' : ''">
                <loader v-if="isLoading"></loader>
                <span v-if="searchStatus === 'success'" class="inline-block font-semibold mb-3">{{totalResults}} zoekresultaten gevonden voor "{{currentQuery}}"</span>
                <drag v-for="result in searchResults"
                      class="drag card"
                      :key="result._index + ':' + result._id"
                      :transfer-data="result"
                      :class="matchRating(result._id)">
                    <h6 class="font-bold">{{result._source.title}}</h6>
                    <a :href="result._source.url" target="_blank">{{result._source.url}}</a>
                    <div class="snippit" v-if="result.highlight">
                        <span :key="highlight" v-for="highlight in result.highlight.text">
                            <span v-html="highlight"></span>...
                        </span>
                    </div>
                    <div>
                        <span v-for="keyword in result._source.keywords" :key="keyword" class="pill">{{keyword}} </span>
                    </div>
                    <div class="meta-info">
                        <span>Type: {{result._source.file_type}}</span>
                        <span>Collection: {{result._source.arrangement_collection_name}}</span>
                    </div>
                </drag>
                <div v-if="searchStatus === 'success'">
                    <paginate
                            v-model="page"
                            :page-count="Math.ceil(totalResults / 10)"
                            :page-range="3"
                            :click-handler="search"
                            :prev-text="'Prev'"
                            :next-text="'Next'"
                            :container-class="'pagination'"
                            :page-class="'page-item'">
                    </paginate>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import {Drag} from "vue-drag-drop";
    import {mapGetters} from "vuex";
    import Loader from "@/components/Loader.vue"

    export default {
        name: "Search",
        components: {
            Drag,
            Loader
        },
        props: {
            subquery: {
                type: Boolean,
                default: false
            }
        },
        data() {
            return {
                query: "",
                page: 1,
                list: {}
            }
        },
        mounted() {
            if (this.$route.query.query) {
                this.query = this.$route.query.query;
            }
        },
        methods: {
            search() {
                let query = this.query;
                if (this.query.length > 0) {
                    let from = (this.page - 1) * 10;
                    this.$store.dispatch("search/get", {search_string: query, from: from});
                    if (this.$store.getters["auth/isLoggedIn"]) {
                        if (this.page === 1 && !this.subquery) {
                            this.$store.dispatch("rating/setQuery", query);
                            this.$store.dispatch("rating/setSubquery", query);
                        } else {
                            this.$store.dispatch("rating/setSubquery", query);
                        }

                        if (this.$route.name === "find") {
                            if (this.$route.query.freeze) {
                                this.$router.push({
                                    name: "rate",
                                    query: {freeze: this.$route.query.freeze, query: query}
                                });
                            } else {
                                this.$router.push({name: "rate", query: {query: query}});
                            }
                        } else {
                            this.$router.push({name: "rate", query: {query: query}});
                        }
                    }


                } else {
                    this.$store.dispatch("search/reset");
                }
            },
            selectQuery(event) {
                this.query = event.target.value;
                this.search();
            },
            reset() {
                this.$store.dispatch("resetModuleState", "rating");
                this.$store.dispatch("resetModuleState", "search");
                this.$router.push({name: "find"});
            },
            matchRating(id) {
                let rating = this.ratingList[id];
                let styling_class = "gray";
                switch (rating) {
                    case 3:
                        styling_class = "orange";
                        break;
                    case 4:
                        styling_class = "blue";
                        break;
                    case 5:
                        styling_class = "green";
                        break;
                }

                return styling_class;
            },
        },
        computed: {
            ...mapGetters("search", ["searchStatus", "searchResults", "totalResults", "currentQuery"]),
            ...mapGetters("rating", ["ratingList", "ratingQuery", "ratedQueries"]),
            ...mapGetters("auth", ["isLoggedIn"]),
            placeholder() {
                let placeholder = "Voer je zoekterm in";
                if (this.subquery) {
                    placeholder = "Verfijn je zoekresultaten"
                }
                return placeholder;
            },
            isLoading() {
                return this.searchStatus === "loading"
            },
            hasRatingQuery() {
                return this.$store.getters["rating/ratingQuery"].length > 0
            },
            isSubQuery() {
                return this.subquery
            }
        },
        watch: {
            query() {
                this.page = 1;
            }
        }
    }
</script>
