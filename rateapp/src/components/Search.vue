<template>
    <div>
        <input v-model="query"
               class="bg-white focus:outline-0 focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal"
               type="email" placeholder="Enter your search query">
        <button @click="search" class="btn btn-blue">Search</button>
        <div :key="result._id" v-for="result in searchResults">
            <span>{{result._source.title}}</span>

        </div>
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
    import {mapGetters} from "vuex";

    export default {
        name: "Search",
        data() {
            return {
                query: "",
                page: 1
            }
        },
        methods: {
            search() {
                let query = this.query;
                let from = (this.page - 1) * 10;
                this.$store.dispatch("search/search", {search_string: query, from: from})
                    .then(() => {
                    })
                    .catch(err => console.log(err))
            },
        },
        computed: {
            ...mapGetters("search", ["searchStatus", "searchResults", "totalResults"])
        }
    }
</script>
