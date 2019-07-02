<template>
    <div class="home">
        <div class="flex">
            <search class="flex-1"></search>
        </div>
        <auth></auth>
    </div>
</template>

<script>
    import Search from "@/components/Search.vue";
    import Auth from "@/components/Auth.vue";

    export default {
        name: "home",
        components: {
            Search,
            Auth
        },
        data() {
            return {}
        },
        methods: {}
    }
</script>
