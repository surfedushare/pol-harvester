import Vue from "vue";
import Vuex from "vuex";

import auth from "./_store/auth";
import search from "./_store/search";
import freeze from "./_store/freeze";
import rating from "./_store/rating";

Vue.use(Vuex);

const modules = {
    auth,
    search,
    freeze,
    rating
}

export const store = new Vuex.Store({
    modules: modules,
    actions: {
        resetModuleState: ({commit}, currentModule) => {
            commit(`${currentModule}/reset_module`);
        }
    }
});
