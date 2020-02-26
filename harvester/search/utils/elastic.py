from elasticsearch import Elasticsearch

from django.conf import settings


def get_es_config():
    """
    Reads a json file containing the elastic search credentials and url.
    The file is expected to have 'url', 'username' and 'password' keys
    """
    username = settings.ELASTIC_SEARCH_USERNAME
    password = settings.ELASTIC_SEARCH_PASSWORD
    if not username or not password:
        raise RuntimeError("No Elastic Search credentials provided")
    return (settings.ELASTIC_SEARCH_URL,
            (username, password),
            settings.ELASTIC_SEARCH_HOST)


def get_es_client(silent=False):
    """
    Returns the elasticsearch client which uses the configuration file
    """
    _, auth, host = get_es_config()
    es_client = Elasticsearch([host],
                              http_auth=auth,
                              scheme='https',
                              port=443,
                              http_compress=True)
    # test if it works
    if not silent and not es_client.cat.health(request_timeout=30):
        raise ValueError('Credentials do not work for Elastic search')
    return es_client


def get_index_config(lang):
    """
    Returns the elasticsearch index configuration.
    Configures the analysers based on the language passed in.
    """
    return {
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        },
        'mappings': {
            '_doc': {
                'properties': {
                    'title': {
                        'type': 'text',
                        'analyzer': settings.ELASTIC_SEARCH_ANALYSERS[lang]
                    },
                    'text': {
                        'type': 'text',
                        'analyzer': settings.ELASTIC_SEARCH_ANALYSERS[lang]
                    },
                    'transcription': {
                        'type': 'text',
                        'analyzer': settings.ELASTIC_SEARCH_ANALYSERS[lang]
                    },
                    'url': {'type': 'text'},
                    'title_plain': {'type': 'text'},
                    'text_plain': {'type': 'text'},
                    'transcription_plain': {'type': 'text'},
                    'author': {
                        'type': 'keyword'
                    },
                    'keywords': {
                        'type': 'keyword'
                    },
                    'file_type': {
                        'type': 'keyword'
                    },
                    'id': {'type': 'text'},
                    'external_id': {
                        'type': 'keyword'
                    },
                    'arrangement_collection_name': {
                        'type': 'keyword'
                    },
                    'educational_levels': {
                        'type': 'keyword'
                    },
                    'disciplines': {
                        'type': 'keyword'
                    },
                    "suggest" : {
                        "type" : "completion"
                    },
                }
            }
        }
    }
