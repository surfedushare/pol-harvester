<template>
    <div class="rate">
        <div v-if="this.$store.getters['rating/ratingQuery'].length === 0">
            <search class="flex-1"></search>
        </div>
        <div v-if="this.$store.getters['rating/ratingQuery'].length > 0" class="flex">
            <div class="w-2/5">
                <search class="flex-1"></search>
                <search :subquery="true" class="flex-1"></search>
            </div>
            <rating class="flex w-3/5"></rating>
        </div>
    </div>
</template>

<script>
    import Search from "@/components/Search.vue";
    import Rating from "@/components/Rating.vue";

    export default {
        name: "rate",
        components: {
            Search,
            Rating
        },
        data() {
            return {}
        },
        methods: {}
    }
</script>
