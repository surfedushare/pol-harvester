import axios from "axios";
import {store} from '../store';

const state = {
    status: "",
    token: localStorage.getItem("token") || "",
    username: ""
};

const getters = {
    authUsername: state => state.username,
    authToken: state => !!state.token,
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
                    console.log('hier?');
                    const token = resp.data.token;
                    const username = credentials.username;
                    store.dispatch('auth/storeCredentials', {token: token, username: username});
                    resolve(resp)
                })
                .catch(err => {
                    console.log('daar?');

                    commit("auth_error");
                    localStorage.removeItem("username");
                    localStorage.removeItem("token");
                    reject(err)
                })
        })
    },
    logout({commit}) {
        return new Promise((resolve) => {
            commit("logout");
            localStorage.removeItem("username");
            localStorage.removeItem("token");
            delete axios.defaults.headers.common["Authorization"];
            resolve();
        })
    },
    storeCredentials({commit}, data) {
        commit("auth_success", {token: data.token, username: data.username});
        localStorage.setItem('username', data.username);
        localStorage.setItem("token", data.token);
        axios.defaults.headers.common["Authorization"] = "Token " + data.token;
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
