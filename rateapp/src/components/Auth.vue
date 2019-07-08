<template>
    <div>
        <input type="text" id="username" v-model="username">
        <input type="password" id="password" v-model="password">
        <button @click="login()" class="btn btn-blue">
            Button
        </button>
        <div v-if="authStatus === 'success'">
            <span>Logged in as: {{authUsername}}</span>
        </div>
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
                this.$store.dispatch("auth/login", {username: username, password: password});
            },
            logout: function () {
                this.$store.dispatch("logout")
                    .then(() => {
                        this.$router.push("/")
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
