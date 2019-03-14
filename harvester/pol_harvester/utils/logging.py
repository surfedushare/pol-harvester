from django.conf import settings


def log_header(logger, header):
    logger.info("")
    logger.info("")
    logger.info(header)
    logger.info("-" * len(header))
    logger.info("Commit: {}".format(settings.GIT_COMMIT))
    logger.info("")
