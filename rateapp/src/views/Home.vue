<template>
    <div class="home">
        <search></search>
        <input type="text" id="username" v-model="username">
        <input type="password" id="password" v-model="password">

        <button @click="login()" class="btn btn-blue">
            Button
        </button>
    </div>
</template>

<script>
    import Search from "@/components/Search.vue";

    export default {
        name: "home",
        components: {
            Search
        },
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
                this.$store.dispatch("auth/login", {username, password})
                    .then(() => this.$router.push("/"))
                    .catch(err => console.log(err))
            },
            logout: function () {
                this.$store.dispatch("logout")
                    .then(() => {
                        this.$router.push("/")
                    })
            }
        }
    }
</script>
