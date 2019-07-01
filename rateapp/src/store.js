import Vue from "vue";
import Vuex from "vuex";

import auth from "./_store/auth";
import search from "./_store/search";
import freeze from "./_store/freeze";

Vue.use(Vuex);

export const store = new Vuex.Store({
    modules: {
        auth,
        search,
        freeze
    }
})
