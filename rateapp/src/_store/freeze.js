import axios from "axios";
import _ from "lodash";

const state = {
    status: "",
    name: "",
    freeze: {}
};

const getters = {
    currentStatus: state => state.status,
    currentName: state => state.name,
    currentFreeze: state => state.freeze,
    indices: state => _.map(state.freeze.indices, "remote_name"),
};

const actions = {
    setFreeze({commit}, freeze_name) {
        return new Promise((resolve, reject) => {
            commit("freeze_request");
            axios.get(process.env.VUE_APP_API_URL + "freeze/",)
                .then(resp => {
                    let found = _.find(resp.data, {"name": freeze_name});
                    if (found) {
                        commit("freeze_success", {name: freeze_name, freeze: found});
                        resolve(resp)
                    } else {
                        commit("freeze_error", freeze_name);
                        reject("Freeze not found")
                    }
                })
                .catch(err => {
                    commit("freeze_error", freeze_name);
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
        state.name = data.name;
        state.freeze = data.freeze;
    },
    freeze_error(state, name) {
        state.status = "error";
        state.name = name;
        state.freeze= {};
    }
};

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
};
