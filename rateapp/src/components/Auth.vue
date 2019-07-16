<template>
    <div class="flex items-center relative">
        <template v-if="authStatus !== 'success'">
            <div class="inline-block mr-2 w-1/3">
                <input v-model="username" id="username"
                       class="input"
                       type="text" placeholder="Username"></div>
            <div class="inline-block mr-2 w-1/3">
                <input v-model="password" id="password"
                       class="input"
                       type="password" placeholder="Password"></div>
            <div class="inline-block">
                <button @click="login()" class="btn">
                    Inloggen
                </button>
            </div>
        </template>
        <small v-if="authStatus === 'error'" class="input-error">Inloggegevens onjuist</small>
        <template v-if="authStatus === 'success'">
            <div class="inline-block mr-5 text-gray-500">Welkom, <span class="text-black">{{authUsername}}</span></div>
            <button @click="logout()" class="btn">
                Uitloggen
            </button>
        </template>
    </div>
</template>

<script>
    import {mapGetters} from 'vuex';

    export default {
        name: "auth",
        data() {
            return {
                username: "",
                password: ""
            }
        },
        methods: {
            login() {
                let username = this.username;
                let password = this.password;
                this.$store.dispatch("auth/login", {username: username, password: password}).then(() => {
                    this.$store.dispatch('rating/getRatingData').then(() => {
                        if (this.$store.getters['rating/ratingQuery'].length > 0) {
                            this.$store.dispatch('rating/setQuery', this.$store.getters['rating/ratingQuery']);
                            if(this.$route.query.freeze) {
                                this.$router.push({name: 'rate', query: { freeze: this.$route.query.freeze}});
                            } else {
                                this.$router.push({name: 'rate'});
                            }
                        }
                    });
                });
                this.username = "";
                this.password = "";
            },
            logout() {
                this.$store.dispatch("auth/logout")
                    .then(() => {
                        if (this.$route.query.freeze) {
                            this.$router.push({name: 'find', query: { freeze: this.$route.query.freeze}})
                        } else {
                            this.$router.push({name: 'find'});
                        }
                    })
            }
        },
        computed: {
            ...mapGetters('auth', [
                'authToken',
                'authStatus',
                'authUsername'
            ])
        }
    }
</script>
