<template>
    <div id="app">
        <div class="flex content-center justify-between border-b border-black px-4 py-2">
            <auth></auth>
            <div class="flex items-center">
                <div class="mr-5">Freeze: <b>{{this.$store.getters['freeze/currentFreeze'].name}}</b></div>
                <img src="./assets/logo.svg">
            </div>
        </div>
        <router-view/>
    </div>
</template>

<script>
    import URI from 'urijs';
    import Auth from "@/components/Auth.vue";

    export default {
        name: 'App',
        components: {
            Auth
        },
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
