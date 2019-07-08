<template>
    <div>
        <input v-model="query"
               class="bg-white focus:outline-0 focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal"
               type="email" placeholder="Enter your search query">
        <button @click="search" class="btn btn-blue">Search</button>
        <drag v-for="result in searchResults"
              class="drag"
              :key="result._id"
              :transfer-data="result">
            {{result._source.title}}
        </drag>
        <div v-if="searchStatus === 'success'">
            <b>total: {{totalResults}}</b>
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
</template>

<script>
    import {Drag} from 'vue-drag-drop';
    import {mapGetters} from "vuex";

    export default {
        name: "Search",
        components: {
            Drag
        },
        data() {
            return {
                query: "",
                page: 1
            }
        },
        methods: {
            search() {
                // TODO: Differentiate between MAIN search and SUB search
                // TODO: FORCE PAGE 1 IF NEW SEARCH
                let query = this.query;
                let from = (this.page - 1) * 10;
                this.$store.dispatch("search/get", {search_string: query, from: from});
                if (this.page === 1) {
                    this.$store.dispatch('rating/setQuery', query);
                }
            },
            post() {
                this.$store.dispatch("rating/post");
            }
        },
        computed: {
            ...mapGetters("search", ["searchStatus", "searchResults", "totalResults"])
        }
    }
</script>
