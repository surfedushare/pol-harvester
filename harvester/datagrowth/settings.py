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
})


DATAGROWTH_MOCK_CONFIGURATION = {}
