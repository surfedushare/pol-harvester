<template>
    <div id="app">
        <router-view/>
    </div>
</template>

<script>
    import URI from 'urijs';
    import axios from 'axios';

    export default {
        name: 'App',
        created() {
            let token = localStorage.getItem("token");
            if (token) {
                axios.defaults.headers.common["Authorization"] = "Token " + token;
                this.$store.dispatch("rating/getRatingData");
            }

            // Get freeze from URI
            let uri = new URI();
            if (uri.search(true).freeze) {
                this.$store.dispatch("freeze/setFreeze", uri.search(true).freeze);
            }
        }
    }
</script>
