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


def get_es_client():
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
    if not es_client.cat.health():
        raise ValueError('Credentials do not work for Elastic search')
    return es_client
