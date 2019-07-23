import axios from "axios";
import {store} from '../store';
import {elasticSearchService} from "../_services";

const initialState = {
    status: "",
    query: "",
    results: [],
    total: 0
};

const state = Object.assign({}, initialState);

const getters = {
    searchStatus: state => state.status,
    searchResults: state => state.results,
    totalResults: state => state.total,
    currentQuery: state => state.query,
};

const actions = {
    get({commit}, data) {
        commit("search_request");
        elasticSearchService.get(data.search_string, data.from).then(res => {
            let results = res.data.hits.hits;
            let total = res.data.hits.total;
            commit('search_success', {query: data.search_string, results: results, total: total});
        }).catch(() => {
            commit("search_error");
        });
    },
    multiGet({commit}, ids) {
        let indices = store.getters['freeze/indices'];
        let query = {
            "ids": ids
        };
        let promises = [];

        for (let i = 0; i < indices.length; i++) {
            let promise = new Promise((resolve, reject) => {
                axios.get(process.env.VUE_APP_ELASTIC_SEARCH_URL + indices[i] + '/_doc/_mget', {
                    auth: {
                        username: process.env.VUE_APP_ELASTIC_SEARCH_USERNAME,
                        password: process.env.VUE_APP_ELASTIC_SEARCH_PASSWORD
                    },
                    params: {
                        source: JSON.stringify(query),
                        source_content_type: 'application/json',
                    },
                }).then((res) => {
                    let documents = res.data.docs;
                    let found_documents = [];
                    for (let i = 0; i < documents.length; i++) {
                        if (documents[i].found) {
                            found_documents.push(documents[i]);
                        }
                    }
                    resolve(found_documents);
                }).catch((err) => {
                    reject(err);
                });
            });
            promises.push(promise);
        }

        return Promise.all(promises).then(values => {
            return values.flat();
        }).catch(() => {
            commit("search_error");
        });
    },
    reset({commit}) {
        commit("reset_module");
    }
};

const mutations = {
    search_request(state) {
        state.status = "loading";
        state.results = [];
        state.total = 0
    },
    search_success(state, data) {
        state.status = "success";
        state.query = data.query;
        state.results = data.results;
        state.total = data.total;
    },
    search_error(state) {
        state.status = "error";
        state.results = [];
        state.total = 0
    },
    reset_module(state) {
        state.status = "";
        state.query = "";
        state.results = [];
        state.total = 0
    }
};

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
};
