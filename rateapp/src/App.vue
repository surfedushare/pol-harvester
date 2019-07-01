<template>
    <div id="app">
        <router-view/>
    </div>
</template>

<script>
    import URI from 'urijs';

    export default {
        name: 'App',
        created() {
            let uri = new URI();
            uri.search(true);

            if (uri.search(true).freeze) {
                this.$store.dispatch("freeze/setFreeze", uri.search(true).freeze)
                    .then(() => {})
                    .catch(err => console.log(err))
            }
        }
    }
</script>
