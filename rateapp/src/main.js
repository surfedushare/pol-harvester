import Vue from "vue";
import App from "./App.vue";

import router from "./router";
import {store} from "./store";
import Paginate from "vuejs-paginate";


import "./css/main.css";

Vue.config.productionTip = false;

Vue.component("paginate", Paginate);

new Vue({
    router,
    store,
    render: h => h(App)
}).$mount("#app");
