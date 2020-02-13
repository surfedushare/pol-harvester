import logging

from django.apps import apps

from datagrowth.configuration import create_config
from datagrowth.processors import ExtractProcessor
from datagrowth.exceptions import DGResourceDoesNotExist

from pol_harvester.models import HttpTikaResource, YouTubeDLResource
from pol_harvester.utils.language import get_kaldi_model_from_snippet
from edurep.models import EdurepSearch, EdurepFile, EdurepOAIPMH
from edurep.extraction import EdurepDataExtraction


EDUREP_EXTRACTION_OBJECTIVE = {
    "url": EdurepDataExtraction.get_url,
    "title": EdurepDataExtraction.get_title,
    "language": EdurepDataExtraction.get_language,
    "keywords": EdurepDataExtraction.get_keywords,
    "description": EdurepDataExtraction.get_description,
    "mime_type": EdurepDataExtraction.get_mime_type,
    "copyright": EdurepDataExtraction.get_copyright,
    "author": EdurepDataExtraction.get_author,
    "publisher_date": EdurepDataExtraction.get_publisher_date,
    "lom_educational_levels": EdurepDataExtraction.get_lom_educational_levels,
    "educational_levels": EdurepDataExtraction.get_educational_levels,
    "humanized_educational_levels": EdurepDataExtraction.get_humanized_educational_levels,
    "disciplines": EdurepDataExtraction.get_disciplines,
    "humanized_disciplines": EdurepDataExtraction.get_humanized_disciplines
}


err = logging.getLogger("pol_harvester")


def get_edurep_query_seeds(query):
    queryset = EdurepSearch.objects.filter(request__contains=query)

    api_objective = {
        "@": EdurepDataExtraction.get_api_records,
        "external_id": EdurepDataExtraction.get_api_external_id,
        "state": EdurepDataExtraction.get_api_record_state
    }
    api_objective.update(EDUREP_EXTRACTION_OBJECTIVE)
    extract_config = create_config("extract_processor", {
        "objective": api_objective
    })
    prc = ExtractProcessor(config=extract_config)

    results = []
    for search in queryset.filter(status=200):
        try:
            results += list(prc.extract_from_resource(search))
        except ValueError as exc:
            err.warning("Invalid XML:", exc, search.uri)
    seeds = {}
    for seed in sorted(results, key=lambda rsl: rsl["publisher_date"] or ""):
        # Some records in Edurep do not have any known URL
        # As we can't possibly process those we ignore them (silently)
        # If we want to fix this it should happen on Edurep's or Sharekit's side
        # We informed Kirsten van Veelo and Martine Teirlinck about the situation.
        if not seed["url"]:
            continue
        # We adjust url's of seeds if the source files are not at the URL
        # We should improve data extraction to always get source files
        if seed["mime_type"] == "application/x-Wikiwijs-Arrangement":
            seed["package_url"] = seed["url"]
            seed["url"] += "?p=imscp"
        # And deduplicate entire seeds based on URL
        seeds[seed["url"]] = seed
    return seeds.values()


def get_edurep_oaipmh_seeds(set_specification, latest_update, include_deleted=True):
    queryset = EdurepOAIPMH.objects\
        .filter(set_specification=set_specification, created_at__gte=latest_update, status=200)

    oaipmh_objective = {
        "@": EdurepDataExtraction.get_oaipmh_records,
        "external_id": EdurepDataExtraction.get_oaipmh_external_id,
        "state": EdurepDataExtraction.get_oaipmh_record_state
    }
    oaipmh_objective.update(EDUREP_EXTRACTION_OBJECTIVE)
    extract_config = create_config("extract_processor", {
        "objective": oaipmh_objective
    })
    prc = ExtractProcessor(config=extract_config)

    results = []
    for harvest in queryset:
        try:
            results += list(prc.extract_from_resource(harvest))
        except ValueError as exc:
            err.warning("Invalid XML:", exc, harvest.uri)
    uniques = {}
    for seed in sorted(results, key=lambda rsl: rsl["publisher_date"] or ""):
        # We adjust url's of seeds if the source files are not at the URL
        # We should improve data extraction to always get source files
        if seed["mime_type"] == "application/x-Wikiwijs-Arrangement" and seed.get("url", None):
            seed["package_url"] = seed["url"]
            seed["url"] += "?p=imscp"
        # We deduplicate based on the external_id a UID by Edurep
        uniques[seed["external_id"]] = seed

    return uniques.values() if include_deleted else \
        [result for result in uniques.values() if result.get("state", "active") == "active"]


def get_edurep_basic_resources(url):
    """
    Convenience function to return a file resource and Tika resource based on a URL.

    Notice that this code checks resource.id to see if a resource really comes from the database.

    :param url: URL to search file and Tika resources for
    :return: file_resource, tika_resource
    """
    try:
        file_resource = EdurepFile(config={"cache_only": True}).get(url)
    except DGResourceDoesNotExist:
        return None, None
    try:
        tika_resource = HttpTikaResource(config={"cache_only": True}).post(file=file_resource.body)
    except DGResourceDoesNotExist:
        return file_resource, None
    return file_resource, tika_resource


def get_edurep_resources(url, language_hint):
    # Checking for basic resources
    file_resource, tika_resource = get_edurep_basic_resources(url)
    if file_resource is None or not file_resource.success or tika_resource is None or not tika_resource.success:
        return file_resource, tika_resource, None, None
    # Getting the video download
    try:
        video_resource = YouTubeDLResource(config={"cache_only": True}).run(url)
    except DGResourceDoesNotExist:
        return file_resource, tika_resource, None, None
    _, file_paths = video_resource.content
    if not video_resource.success or not len(file_paths):
        return file_resource, tika_resource, video_resource, None
    # Getting the transcription for the download
    file_path = file_paths[0]
    kaldi_model = get_kaldi_model_from_snippet(language_hint)
    if kaldi_model is None:
        return file_resource, tika_resource, video_resource, None
    Kaldi = apps.get_model(kaldi_model)
    try:
        kaldi_resource = Kaldi(config={"cache_only": True}).run(file_path)
    except DGResourceDoesNotExist:
        return file_resource, tika_resource, video_resource, None
    return file_resource, tika_resource, video_resource, kaldi_resource
