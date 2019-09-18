import logging

from datagrowth.configuration import create_config
from datagrowth.processors import ExtractProcessor
from datagrowth.exceptions import DGHttpError40X

from pol_harvester.models import HttpTikaResource
from edurep.models import EdurepSearch, EdurepFile


err = logging.getLogger("pol_harvester")


def get_edurep_query_seeds(query):
    queryset = EdurepSearch.objects.filter(request__contains=query)

    extract_config = create_config("extract_processor", {
        "objective": {
            "@": "soup.find_all('srw:record')",
            "url": "el.find('czp:location').text",
            "title": "el.find('czp:title').find('czp:langstring').text",
            "language": "el.find('czp:language').text",
            "keywords": "[keyword.find('czp:langstring').text for keyword in el.find_all('czp:keyword')]",
            "description": "el.find('czp:description').find('czp:langstring').text if el.find('czp:description') else None",
            "mime_type": "el.find('czp:format').text",
        }
    })
    prc = ExtractProcessor(config=extract_config)

    results = []
    for search in queryset.filter(status=200):
        try:
            results += list(prc.extract_from_resource(search))
        except ValueError as exc:
            err.warning("Invalid XML:", exc, search.uri)
    return results


def get_edurep_basic_resources(url):
    # TODO: make this cache_only
    try:
        file_resource = EdurepFile().get(url)
    except (DGHttpError40X, EdurepFile.DoesNotExist):
        return None, None
    tika_resource = HttpTikaResource().post(file=file_resource.body)
    return file_resource, tika_resource
