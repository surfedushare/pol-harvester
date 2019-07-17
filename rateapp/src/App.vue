<template>
    <div id="app">
        <div class="navbar">
            <auth></auth>
            <div class="flex items-center">
                <div v-if="this.$store.getters['freeze/currentStatus'] === 'success' " class="mr-5">
                    <span>Freeze: <b class="text-green-500">{{this.$store.getters['freeze/currentName']}}</b></span>
                </div>
                <div v-if="this.$store.getters['freeze/currentStatus'] === 'error' " class="mr-5">
                    <span class="text-red-500 font-bold">Freeze "{{this.$store.getters['freeze/currentName']}}" not found</span>
                </div>
                <img src="./assets/logo.svg">
            </div>
        </div>
        <router-view v-if="this.$store.getters['freeze/currentStatus'] === 'success'"/>
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
