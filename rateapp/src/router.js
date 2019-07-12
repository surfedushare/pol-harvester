import Vue from "vue";
import Router from "vue-router";
import Find from "./views/Find.vue";
import {store} from "./store.js";

Vue.use(Router);

let router = new Router({
    mode: "history",
    base: process.env.BASE_URL,
    routes: [
        {
            path: "/",
            name: "find",
            component: Find
        },
        {
            path: "/rate",
            name: "rate",
            // route level code-splitting
            // this generates a separate chunk (about.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: () => import(/* webpackChunkName: "rate" */ "./views/Rate.vue"),
            meta: {
                requiresAuth: true
            }
        }
    ]
});

router.beforeEach((to, from, next) => {
    if (to.matched.some(record => record.meta.requiresAuth)) {
        if (store.getters["auth/isLoggedIn"]) {
            next();
            return
        }
        next("/");
    } else {
        next();
    }
});

export default router;
