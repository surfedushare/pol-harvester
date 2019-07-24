<template>
    <div id="app">
        <div class="navbar">
            <auth></auth>
            <div class="flex items-center">
                <div v-if="freezeSuccess" class="mr-5">
                    <span>Freeze: <b class="text-green-500">{{freezeName}}</b></span>
                </div>
                <div v-if="freezeError" class="mr-5">
                    <span class="text-red-500 font-bold">Freeze "{{freezeName}}" not found</span>
                </div>
                <img src="./assets/logo.svg">
            </div>
        </div>
        <router-view v-if="freezeSuccess"/>
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

        },
        computed: {
            freezeSuccess() {
                return this.$store.getters['freeze/currentStatus'] === 'success'
            },
            freezeError() {
                return this.$store.getters['freeze/currentStatus'] === 'error'
            },
            freezeName() {
                return this.$store.getters['freeze/currentName']
            }
        }
    }
</script>
