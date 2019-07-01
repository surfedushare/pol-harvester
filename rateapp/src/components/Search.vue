<template>
    <div>
        <input v-model="query"
               class="bg-white focus:outline-0 focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal"
               type="email" placeholder="Enter your search query">
        <button @click="search" class="btn btn-blue">Search</button>
        <div :key="result._id" v-for="result in searchResults">
            <span>{{result._source.title}}</span>

        </div>
        <span v-if="searchStatus === 'success'">
            <b>total: {{totalResults}}</b>
            </span>
    </div>
</template>

<script>
    import {mapGetters} from "vuex";

    export default {
        name: "Search",
        data() {
            return {
                query: ""
            }
        },
        methods: {
            search() {
                let query = this.query;
                this.$store.dispatch("search/search", query)
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
