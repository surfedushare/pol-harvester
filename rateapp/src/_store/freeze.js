import axios from "axios";
import _ from "lodash";

const state = {
    status: "",
    freeze: {}
};

const getters = {
    currentFreeze: state => !!state.freeze,
    indices: state => _.map(state.freeze.indices, "remote_name"),
};

const actions = {
    setFreeze({commit}, freeze_name) {
        return new Promise((resolve, reject) => {
            commit("freeze_request");
            axios.get(process.env.VUE_APP_API_URL + "freeze/",)
                .then(resp => {
                    let found = _.find(resp.data, {'name': freeze_name});
                    if (found) {
                        commit("freeze_success", found);
                        resolve(resp)
                    } else {
                        commit("freeze_error");
                        reject("Freeze not found")
                    }
                })
                .catch(err => {
                    commit("freeze_error");
                    reject(err)
                })
        })
    },
};

const mutations = {
    freeze_request(state) {
        state.status = "loading";
    },
    freeze_success(state, data) {
        state.status = "success";
        state.freeze = data;
    },
    freeze_error(state) {
        state.status = "error";
        state.freeze = "";
    }
};

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
};
