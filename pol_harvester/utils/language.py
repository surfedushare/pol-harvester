import spacy
from spacy_cld import LanguageDetector


nlp = spacy.load("nl_core_news_sm")
nlp.add_pipe(LanguageDetector())


def get_language_from_snippet(snippet, default=None):
    if not snippet:
        return default
    doc = nlp(snippet)
    return doc._.languages[0] if doc._.languages else default


def get_kaldi_model_from_snippet(snippet, default_language=None):
    language = get_language_from_snippet(snippet, default=default_language)
    if language == "nl":
        return "pol_harvester.KaldiNLResource"
    elif language == "en":
        return "pol_harvester.KaldiAspireResource"
