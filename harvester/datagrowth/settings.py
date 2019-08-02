import os

from django.conf import settings


######################################
# PLAIN SETTINGS
######################################


DATAGROWTH_DATETIME_FORMAT = getattr(settings, "DATAGROWTH_DATETIME_FORMAT", "%Y%m%d%H%M%S%f")

DATAGROWTH_DATA_DIR = getattr(settings, "DATAGROWTH_DATA_DIR", os.path.join(settings.BASE_DIR, "data"))
DATAGROWTH_MEDIA_ROOT = getattr(settings, "DATAGROWTH_MEDIA_ROOT", settings.MEDIA_ROOT)
DATAGROWTH_BIN_DIR = getattr(settings, "DATAGROWTH_BIN_DIR",
    os.path.join(settings.BASE_DIR, "datagrowth", "resources", "shell", "bin")
)

DATAGROWTH_REQUESTS_PROXIES = getattr(settings, "DATAGROWTH_REQUESTS_PROXIES", None)
DATAGROWTH_REQUESTS_VERIFY = getattr(settings, "DATAGROWTH_REQUESTS_VERIFY", True)

DATAGROWTH_KALDI_BASE_PATH = getattr(settings, "DATAGROWTH_KALDI_BASE_PATH", "")
DATAGROWTH_KALDI_ASPIRE_BASE_PATH = getattr(settings, "DATAGROWTH_KALDI_ASPIRE_BASE_PATH", "")
DATAGROWTH_KALDI_NL_BASE_PATH = getattr(settings, "DATAGROWTH_KALDI_NL_BASE_PATH", "")


######################################
# DEFAULT CONFIGURATION SETTINGS
######################################


DATAGROWTH_DEFAULT_CONFIGURATION = getattr(settings, "DATAGROWTH_DEFAULT_CONFIGURATION", {
    "global_allowed_origins": [],
    "global_async": True,  # by default offload to celery where possible
    "global_user_agent": "POL",
    "global_token": "",
    "global_purge_immediately": False,  # by default keep resources around
    "global_sample_size": 0,
    "global_fetch_only": False,

    "http_resource_batch_size": 0,
    "http_resource_continuation_limit": 1,
    "http_resource_interval_duration": 0,  # NB: milliseconds!
    "http_resource_concat_args_size": 0,
    "http_resource_concat_args_symbol": "|",

    "google_api_key": getattr(settings, 'GOOGLE_API_KEY', ''),
    "google_cx": getattr(settings, 'GOOGLE_CX', ''),
})


DATAGROWTH_MOCK_CONFIGURATION = {}
