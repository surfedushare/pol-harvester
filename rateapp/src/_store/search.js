import axios from "axios";
import {store} from '../store';

const state = {
    status: "",
    query: "",
    results: [],
    total: 0
};

const getters = {
    searchStatus: state => state.status,
    searchResults: state => state.results,
    totalResults: state => state.total,
    currentQuery: state => state.query,
};

const actions = {
    search({commit}, data) {
        let indices = store.getters['freeze/indices'].join();
        let query = {
            "query": {
                "multi_match": {
                    "query": data.search_string,
                    "fields": [
                        "title",
                        "text"
                    ]
                },
            },
            "from": data.from
        };
        return new Promise((resolve, reject) => {
            commit("search_request");
            axios.get(process.env.VUE_APP_ELASTIC_SEARCH_URL + indices + '/_search', {
                auth: {
                    username: process.env.VUE_APP_ELASTIC_SEARCH_USERNAME,
                    password: process.env.VUE_APP_ELASTIC_SEARCH_PASSWORD
                },
                params: {
                    source: JSON.stringify(query),
                    source_content_type: 'application/json',
                },
            }).then((res) => {
                let results = res.data.hits.hits;
                let total = res.data.hits.total;
                commit('search_success', {query: data.search_string, results: results, total: total})
            }).catch(err => {
                commit("search_error");
                reject(err)
            });
        })
    },
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
};

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
};
