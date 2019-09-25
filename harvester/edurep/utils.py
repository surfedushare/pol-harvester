import logging

from django.apps import apps

from datagrowth.configuration import create_config
from datagrowth.processors import ExtractProcessor
from datagrowth.exceptions import DGResourceException, DGHttpError40X

from pol_harvester.models import HttpTikaResource, YouTubeDLResource, KaldiNLResource, KaldiAspireResource
from pol_harvester.utils.language import get_kaldi_model_from_snippet
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
    """
    Convenience function to return a file resource and Tika resource based on a URL

    Notice that this code checks resource.id to see if a resource really comes from the database.
    In future version of Datagrowth fetch_only will raise when nothing exists in the database.

    :param url: URL to search file and Tika resources for
    :return: file_resource, tika_resource
    """
    file_resource = EdurepFile(config={"fetch_only": True}).get(url)
    if not file_resource.id:
        return None, None
    tika_resource = HttpTikaResource(config={"fetch_only": True}).post(file=file_resource.body)
    if not tika_resource.id:
        return file_resource, None
    return file_resource, tika_resource


def get_edurep_resources(url, language_hint):
    # Checking for basic resources
    file_resource, tika_resource = get_edurep_basic_resources(url)
    if file_resource is None or not file_resource.success or tika_resource is None or tika_resource.success:
        return file_resource, tika_resource, None, None
    # Getting the video download
    video_resource = YouTubeDLResource(config={"fetch_only": True}).run(url)
    if not video_resource.id:
        return file_resource, tika_resource, None, None
    _, file_paths = video_resource.content
    if not len(file_paths):
        return file_resource, tika_resource, video_resource, None
    # Getting the transcription for the download
    file_path = file_paths[0]
    kaldi_model = get_kaldi_model_from_snippet(language_hint)
    if kaldi_model is None:
        return file_resource, tika_resource, video_resource, None
    Kaldi = apps.get_model(kaldi_model)
    kaldi_resource = Kaldi(config={"fetch_only": True}).run(file_path)
    if not kaldi_resource.id:
        return file_resource, tika_resource, video_resource, None
    return file_resource, tika_resource, video_resource, kaldi_resource
