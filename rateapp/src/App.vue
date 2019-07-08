<template>
    <div id="app">
        <router-view/>
    </div>
</template>

<script>
    import URI from 'urijs';

    export default {
        name: 'App',
        created() {
            let username = localStorage.getItem("username");
            let token = localStorage.getItem("token");

            if (token) {
                this.$store.dispatch('auth/storeCredentials', {username: username, token: token});
                this.$store.dispatch("rating/getRatingData");
            }

            // Get freeze from URI
            let uri = new URI();
            let freeze = uri.search(true).freeze ? uri.search(true).freeze : process.env.VUE_APP_DEFAULT_FREEZE;
            this.$store.dispatch("freeze/setFreeze", freeze);

        }
    }
</script>
