<template>
    <div class="home">
        <auth></auth>

        <div class="flex h-screen">
            <search class="flex-1 w-1/2"></search>
            <rating></rating>
        </div>
    </div>
</template>

<script>
    import Search from "@/components/Search.vue";
    import Rating from "@/components/Rating.vue";
    import Auth from "@/components/Auth.vue";

    export default {
        name: "home",
        components: {
            Search,
            Rating,
            Auth
        },
        data() {
            return {}
        },
        methods: {}
    }
</script>
