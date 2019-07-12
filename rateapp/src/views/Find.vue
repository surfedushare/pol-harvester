<template>
    <div class="home">
        <div class="flex h-screen">
            <search class="flex-1"></search>
        </div>
    </div>
</template>

<script>
    import Search from "@/components/Search.vue";

    export default {
        name: "find",
        components: {
            Search
        },
        data() {
            return {}
        },
        methods: {}
    }
</script>
