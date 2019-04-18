import json

from django.conf import settings


def log_header(logger, header, options=None):
    logger.info("")
    logger.info("")
    logger.info(header)
    logger.info("-" * len(header))
    if options:
        logger.info("Options: {}".format(json.dumps(options, indent=4)))
    logger.info("Commit: {}".format(settings.GIT_COMMIT))
    logger.info("")
