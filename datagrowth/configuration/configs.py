DEFAULT_CONFIGURATION = {
    "global_allowed_origins": [],
    "global_async": True,  # by default offload to celery where possible
    "global_user_agent": "DataGrowth (v{})".format("0.7.0"),
    "global_token": "",
    "global_purge_immediately": False,  # by default keep resources around
    "global_sample_size": 0,

    "http_resource_batch_size": 0,
    "http_resource_continuation_limit": 1,
    "http_resource_interval_duration": 0,  # NB: milliseconds!
    "http_resource_concat_args_size": 0,
    "http_resource_concat_args_symbol": "|",
}

MOCK_CONFIGURATION = {}
