import {store} from "../store";
import axios from "axios";

const URL = process.env.VUE_APP_ELASTIC_SEARCH_URL;
const USERNAME = process.env.VUE_APP_ELASTIC_SEARCH_USERNAME;
const PASSWORD = process.env.VUE_APP_ELASTIC_SEARCH_PASSWORD;

export const elasticSearchService = {
    get,
    mget
};

function get(search_string, from) {
    let indices = store.getters['freeze/indices'].join();
    let query = {
        "query": {
            "multi_match": {
                "query": search_string,
                "fields": [
                    "title",
                    "text"
                ]
            },
        },
        "from": from,
        "size": 10
    };

    return axios.get(URL + indices + '/_search', {
        auth: {
            username: USERNAME,
            password: PASSWORD
        },
        params: {
            source: JSON.stringify(query),
            source_content_type: 'application/json',
        },
    });
}

function mget(index, ids) {
    let query = {
        "ids": ids
    };

    return axios.get(process.env.VUE_APP_ELASTIC_SEARCH_URL + index + '/_doc/_mget', {
        auth: {
            username: process.env.VUE_APP_ELASTIC_SEARCH_USERNAME,
            password: process.env.VUE_APP_ELASTIC_SEARCH_PASSWORD
        },
        params: {
            source: JSON.stringify(query),
            source_content_type: 'application/json',
        },
    });
}
