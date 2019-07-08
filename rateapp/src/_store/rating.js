import axios from "axios";
import {store} from "../store";
import {elasticSearchService} from "../_services";
import _ from "lodash";

const state = {
    rating_status: "",
    document_status: "",
    all_query_data: {},
    current_query: "",
    current_subquery: "",
    current_query_ratings: {},
    current_query_rating_documents: [],
};

const getters = {
    ratingStatus: state => state.rating_status,
    ratingDocumentStatus: state => state.document_status,
    ratingQuery: state => state.current_query,
    ratingSubquery: state => state.current_subquery,
    ratingResults: state => state.current_query_ratings,
    ratingDocuments: state => state.current_query_rating_documents
};

const actions = {
    getRatingData({commit}) {
        new Promise((resolve, reject) => {
            commit("rating_request");
            axios.get(process.env.VUE_APP_API_URL + 'search/query/').then(res => {
                commit("rating_success", res.data)
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
                    reject(err);
                })
            });
            promises.push(promise);
        }

        return Promise.all(promises)
    },
    setQuery({commit}, search_string) {
        commit('documents_request', search_string);

        console.log(search_string);
        let rating_object = _.find(state.all_query_data, {'query': search_string});
        if (rating_object) {
            let ids_array = [];
            _.forEach(rating_object.rankings, function (ranking_object) {
                ids_array.push(_.keysIn(ranking_object.ranking))
            });
            let ids = ids_array.flat();

            store.dispatch('rating/getDocuments', ids).then(documents => {
                commit('documents_success', {ratings: rating_object, documents: documents.flat()})
            }).catch(err => {
                commit('documents_error')
            });
        }
    },
    post({commit}, data) {
        // let object = {
        //     "query": state.query,
        //     "rankings": [
        //         {
        //             "subquery": state.subquery,
        //             "ranking:": data,
        //             "freeze": store.getters['freeze/currentFreeze'].id
        //         }
        //     ]
        // };

        let object = state.current_query_ratings;
        delete object.created_at;
        delete object.modified_at;

        console.log('object',object);
        // let object = {
        //     "query": "genen",
        //     "rankings": [
        //         {
        //             "subquery": "dna",
        //             "ranking": {
        //                 "edc04e983da57f10fafe7775179f0e9c592af41a": 5
        //             },
        //             "freeze": store.getters['freeze/currentFreeze'].id
        //         },
        //         {
        //             "subquery": "genen",
        //             "ranking": {"92c52372b361e20e6d3011526d62a218340c7463": 3},
        //             "freeze": store.getters['freeze/currentFreeze'].id
        //         }
        //     ]
        // };

        return new Promise((resolve, reject) => {
            axios.post(process.env.VUE_APP_API_URL + 'search/query/', object).then((res) => {
                console.log(res);
            }).catch(err => {
                reject(err)
            });
        })
    },
    addRating({commit}, data) {
        // TODO: ADD CHECK IF ID IS ALREAYD PRESENT;
        commit('add_document', data.document);
        commit('add_rating', {id: data.document._id, rating: data.rating});
        store.dispatch('rating/post');
    }
};

const mutations = {
    rating_request(state) {
        state.rating_status = "loading";
        state.all_query_data = {};
        state.current_query = "";
        state.current_subquery = "";
        state.current_query_ratings = {};
        state.current_query_rating_documents = [];
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
    add_document(state, document) {
        state.current_query_rating_documents.push(document)
    },
    add_rating(state, data) {
        let current_ratings = state.current_query_ratings;

        if (_.isEmpty(current_ratings)) {
            state.current_query_ratings = {
                query: state.current_query,
                rankings: [{
                    freeze: store.getters['freeze/currentFreeze'].id,
                    ranking: {},
                    subquery: state.current_query
                }]
            }
        }

        // TODO: USE SUBQUERY INSTEAD OF QUERY
        let found_ranking = _.find(state.current_query_ratings.rankings, {'subquery': state.current_query});

        if (found_ranking) {
            console.log('found_ranking', found_ranking);
            found_ranking.ranking[data.id] = data.rating;
        }

    }
};

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
};
