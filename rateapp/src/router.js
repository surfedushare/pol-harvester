import Vue from "vue";
import Router from "vue-router";
import Home from "./views/Home.vue";
import store from "./store.js";

Vue.use(Router);

let router = new Router({
    mode: "history",
    base: process.env.BASE_URL,
    routes: [
        {
            path: "/",
            name: "home",
            component: Home
        },
        // {
        //     path: "/annotate",
        //     name: "annotate",
        //     // route level code-splitting
        //     // this generates a separate chunk (about.[hash].js) for this route
        //     // which is lazy-loaded when the route is visited.
        //     component: () => import(/* webpackChunkName: "about" */ "./views/About.vue"),
        //     meta: {
        //         requiresAuth: true
        //     }
        // }
    ]
});

router.beforeEach((to, from, next) => {
    if (to.matched.some(record => record.meta.requiresAuth)) {
        if (store.getters.isLoggedIn) {
            next();
            return
        }
        next("/");
    } else {
        next();
    }
});

export default router;
