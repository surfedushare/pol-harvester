import axios from "axios";
import {store} from "../store";
import {elasticSearchService} from "../_services";
import _ from "lodash";

const initialState = {
    rating_status: "",
    document_status: "",
    all_query_data: {},
    current_query: "",
    current_subquery: "",
    current_query_ratings: {},
    current_query_ratings_list: {},
    current_query_rating_documents: [],
    rated_queries: []
};

const state = Object.assign({}, initialState);

const getters = {
    ratingStatus: state => state.rating_status,
    ratingDocumentStatus: state => state.document_status,
    ratingQuery: state => state.current_query,
    ratingSubquery: state => state.current_subquery,
    ratingResults: state => state.current_query_ratings,
    ratingDocuments: state => state.current_query_rating_documents,
    ratedQueries: state => state.rated_queries,
    ratingList: state => state.current_query_ratings_list
};

const actions = {
    getRatingData({commit}) {
        return new Promise((resolve, reject) => {
            commit("rating_request");
            axios.get(process.env.VUE_APP_API_URL + 'search/query/').then(res => {
                commit("rating_success", res.data)

                let queries = [];
                _.forEach(res.data, function (ranking) {
                    queries.push(ranking.query)
                });

                commit("set_rated_queries", queries);
                commit('set_rating_list');
                resolve(res);
            }).catch(err => {
                commit("rating_error");
                reject(err)
            });
        })
    },
    getDocuments({commit}, ids) {
        let indices = store.getters['freeze/indices'];
        let promises = [];

        for (let i = 0; i < indices.length; i++) {
            let promise = new Promise((resolve, reject) => {
                elasticSearchService.mget(indices[i], ids).then((res) => {
                    let documents = res.data.docs;
                    let found_documents = [];
                    for (let i = 0; i < documents.length; i++) {
                        if (documents[i].found) {
                            found_documents.push(documents[i]);
                        }
                    }
                    resolve(found_documents);
                }).catch((err) => {
                    commit('documents_error');
                    reject(err);
                })
            });
            promises.push(promise);
        }

        return Promise.all(promises)
    },
    setQuery({commit}, search_string) {
        commit('documents_request', search_string);
        let rating_object = _.find(state.all_query_data, {'query': search_string});
        if (rating_object) {
            let ids_array = [];
            _.forEach(rating_object.rankings, function (ranking_object) {
                ids_array.push(_.keysIn(ranking_object.ranking))
            });
            let ids = ids_array.flat();

            store.dispatch('rating/getDocuments', ids).then(documents => {
                commit('documents_success', {ratings: rating_object, documents: documents.flat()})
                commit('set_rating_list');
            }).catch(() => {
                commit('documents_error')
            });
        }
    },
    setSubquery({commit}, search_string) {
        commit('set_subquery', search_string)
    },
    post() {
        let object = state.current_query_ratings;
        delete object.created_at;
        delete object.modified_at;

        return new Promise((resolve, reject) => {
            axios.post(process.env.VUE_APP_API_URL + 'search/query/', object).then((res) => {
                resolve(res);
            }).catch(err => {
                reject(err)
            });
        })
    },
    addRating({commit}, data) {
        // TODO: ADD CHECK IF ID IS ALREAYD PRESENT;
        commit('add_document', data.document);
        commit('add_rating', {id: data.document._id, index: data.document._index, rating: data.rating});
        commit('set_rating_list');
        store.dispatch('rating/post');
    },
    removeRating({commit}, id) {
        commit('remove_rating', id);
        commit('set_rating_list');
        store.dispatch('rating/post');
    }
};

const mutations = {
    rating_request(state) {
        state.rating_status = "loading";
        state.all_query_data = {};
    },
    rating_success(state, query_data) {
        state.rating_status = "success";
        state.all_query_data = query_data;
    },
    rating_error(state) {
        state.rating_status = "error";
        state.all_query_data = {};
        state.current_query = "";
        state.current_subquery = "";
        state.current_query_ratings = {};
        state.current_query_rating_documents = [];
        state.rated_queries = [];
    },
    documents_request(state, query) {
        state.document_status = "loading";
        state.current_query = query;
        state.current_query_ratings = {};
        state.current_query_rating_documents = [];
    },
    documents_success(state, data) {
        state.document_status = "success";
        state.current_query_ratings = data.ratings;
        state.current_query_rating_documents = data.documents;
    },
    documents_error(state) {
        state.document_status = "error";
        state.current_query_rating_documents = [];
    },
    set_subquery(state, search_string) {
        state.current_subquery = search_string;
    },
    set_rated_queries(state, queries) {
        state.rated_queries = queries;
    },
    add_document(state, document) {
        state.current_query_rating_documents.push(document)
    },
    add_rating(state, data) {
        let current_ratings = state.current_query_ratings;
        let already_ranked = false;
        let subquery_ranking;
        let combined_identifier = data.index + ":" + data.id;
        let new_ranking_object = {
            freeze: store.getters['freeze/currentFreeze'].id,
            ranking: {},
            subquery: state.current_subquery
        };

        // If no ratings yet for query, create new object
        if (_.isEmpty(current_ratings)) {
            state.current_query_ratings = {
                query: state.current_query,
                rankings: [new_ranking_object]
            }
        }

        _.forEach(state.current_query_ratings.rankings, function (ranking) {
            if (_.has(ranking.ranking, combined_identifier)) {
                already_ranked = true;
                subquery_ranking = ranking;
            }
        });

        // Change rating if already rated
        if (already_ranked) {
            subquery_ranking.ranking[combined_identifier] = data.rating;
        } else {
            let found_ranking = _.find(state.current_query_ratings.rankings, {'subquery': state.current_subquery});

            // Check if already a ranking for current subquery, else create new object
            if (found_ranking) {
                found_ranking.ranking[combined_identifier] = data.rating;
            } else {
                new_ranking_object.ranking[combined_identifier] = data.rating;
                state.current_query_ratings.rankings.push(new_ranking_object)
            }
        }
    },
    remove_rating(state, id) {
        _.forEach(state.current_query_ratings.rankings, function (ranking) {
            delete ranking.ranking[id];
        });
    },
    set_rating_list(state) {
        let list = {};
        _.forEach(state.current_query_ratings.rankings, function (ranking) {
            _.forOwn(ranking.ranking, function (value, key) {
                let split = key.split(":");
                let reference = split[1];

                list[reference] = value;
            });
        });

        state.current_query_ratings_list = list;
    },
    reset_module(state) {
        state.rating_status = "success";
        state.current_query = "";
        state.current_subquery = "";
        state.current_query_ratings = {};
        state.current_query_rating_documents = [];
    }
};

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
};
