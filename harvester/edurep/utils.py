import logging
from html import unescape

from django.apps import apps

from datagrowth.configuration import create_config
from datagrowth.processors import ExtractProcessor
from datagrowth.exceptions import DGResourceException, DGHttpError40X

from pol_harvester.models import HttpTikaResource, YouTubeDLResource, KaldiNLResource, KaldiAspireResource
from pol_harvester.utils.language import get_kaldi_model_from_snippet
from edurep.models import EdurepSearch, EdurepFile


err = logging.getLogger("pol_harvester")


UNESCAPE_TARGET_FIELDS = ["title", "description", "author", "keywords"]


def get_edurep_query_seeds(query):
    queryset = EdurepSearch.objects.filter(request__contains=query)

    extract_config = create_config("extract_processor", {
        "objective": {
            "@": "soup.find_all('srw:record')",
            "external_id": "el.find('srw:recordidentifier').text",
            "url": "el.find('czp:location').text if el.find('czp:location') else None",
            "title": "el.find('czp:title').find('czp:langstring').text",
            "language": "el.find('czp:language').text if el.find('czp:language') else None",
            "keywords": "[keyword.find('czp:langstring').text for keyword in el.find_all('czp:keyword')]",
            "description": "el.find('czp:description').find('czp:langstring').text if el.find('czp:description') else None",
            "mime_type": "el.find('czp:format').text if el.find('czp:format') else None",
            "copyright": "el.find('czp:copyrightandotherrestrictions').find('czp:value').find('czp:langstring').text if el.find('czp:copyrightandotherrestrictions') else None",
            "author": "[card.text for card in el.find(string='author').find_parent('czp:contribute').find_all('czp:vcard')] if el.find(string='author') and el.find(string='author').find_parent('czp:contribute') else []",
            "publisher_date": "el.find(string='publisher').find_parent('czp:contribute').find('czp:datetime').text if el.find(string='publisher') and el.find(string='publisher').find_parent('czp:contribute') and el.find(string='publisher').find_parent('czp:contribute').find('czp:datetime') else None",
            "lom_educational_levels": "[edu.find('czp:value').find('czp:langstring').text for edu in el.find('czp:educational').find_all('czp:context')] if el.find('czp:educational') and el.find('czp:educational').find('czp:context') else []",
            "educational_levels": "[level.text for level in el.find(string='educational level').find_parent('czp:classification').find_all('czp:id')] if el.find(string='educational level') and el.find(string='educational level').find_parent('czp:classification') else []",
            "humanized_educational_levels": "[entry.find('czp:langstring').text for entry in el.find(string='educational level').find_parent('czp:classification').find_all('czp:entry')] if el.find(string='educational level') and el.find(string='educational level').find_parent('czp:classification') else []",
            "disciplines": "[discipline.text for discipline in el.find(string='discipline').find_parent('czp:classification').find_all('czp:id')] if el.find(string='discipline') and el.find(string='discipline').find_parent('czp:classification') else []",
            "humanized_disciplines": "[entry.find('czp:langstring').text for entry in el.find(string='discipline').find_parent('czp:classification').find_all('czp:entry')] if el.find(string='discipline') and el.find(string='discipline').find_parent('czp:classification') else []",
        }
    })
    prc = ExtractProcessor(config=extract_config)

    results = []
    for search in queryset.filter(status=200):
        try:
            results += list(prc.extract_from_resource(search))
        except ValueError as exc:
            err.warning("Invalid XML:", exc, search.uri)
    seeds = {}
    duplicate_counts = 0
    overwrite_counts = 0
    missing_disciplines_counts = 0
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
        # We unescape HTML entities, because Edurep doesn't do it for us
        for field in UNESCAPE_TARGET_FIELDS:
            if seed[field]:
                seed[field] = unescape(seed[field])
        if seed["title"] in seeds:
            duplicate_counts += 1
            if len(seeds[seed["title"]]["disciplines"]) and not len(seed["disciplines"]):
                overwrite_counts += 1
            #print(len(seeds[seed["url"]]["disciplines"]), len(seed["disciplines"]))
        # We deduplicate some fields
        seed["lom_educational_levels"] = list(set(seed["lom_educational_levels"]))
        seed["educational_levels"] = list(set(seed["educational_levels"]))
        seed["humanized_educational_levels"] = list(set(seed["humanized_educational_levels"]))
        seed["disciplines"] = list(set(seed["disciplines"]))
        seed["humanized_disciplines"] = list(set(seed["humanized_disciplines"]))
        # And deduplicate entire seeds based on title
        seeds[seed["title"]] = seed
        if not len(seed["disciplines"]):
            missing_disciplines_counts += 1
    print("Counts:", overwrite_counts, duplicate_counts, missing_disciplines_counts)
    return seeds.values()


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
    if file_resource is None or not file_resource.success or tika_resource is None or not tika_resource.success:
        return file_resource, tika_resource, None, None
    # Getting the video download
    video_resource = YouTubeDLResource(config={"fetch_only": True}).run(url)
    if not video_resource.id:
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
    kaldi_resource = Kaldi(config={"fetch_only": True}).run(file_path)
    if not kaldi_resource.id:
        return file_resource, tika_resource, video_resource, None
    return file_resource, tika_resource, video_resource, kaldi_resource
