import axios from "axios";

const state = {
    status: "",
    token: localStorage.getItem("token") || "",
    username: ""
};

const getters = {
    isLoggedIn: state => !!state.token,
    authStatus: state => state.status,
};

const actions = {
    login({commit}, credentials) {
        return new Promise((resolve, reject) => {
            commit("auth_request");
            axios.post(process.env.VUE_APP_API_URL + "auth/token", {
                username: credentials.username,
                password: credentials.password
            })
                .then(resp => {
                    const token = resp.data.token;
                    const username = credentials.username;
                    localStorage.setItem("token", token);
                    axios.defaults.headers.common["Authorization"] = "Token " + token;
                    commit("auth_success", {token, username});
                    resolve(resp)
                })
                .catch(err => {
                    commit("auth_error");
                    localStorage.removeItem("token");
                    reject(err)
                })
        })
    },
    logout({commit}) {
        return new Promise((resolve) => {
            commit("logout");
            localStorage.removeItem("token");
            delete axios.defaults.headers.common["Authorization"];
            resolve();
        })
    }
};

const mutations = {
    auth_request(state) {
        state.status = "loading";
    },
    auth_success(state, data) {
        state.status = "success";
        state.token = data.token;
        state.username = data.username;
    },
    auth_error(state) {
        state.status = "error";
    },
    logout(state) {
        state.status = "";
        state.token = "";
        state.username = "";
    },
};

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
};
