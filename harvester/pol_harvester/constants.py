class HarvestStages:
    NEW = "New"
    BASIC = "Basic"
    VIDEO = "Video"
    COMPLETE = "Complete"

HARVEST_STAGE_CHOICES = [
    (value, value) for attr, value in sorted(HarvestStages.__dict__.items()) if not attr.startswith("_")
]


PLAIN_TEXT_MIME_TYPES = [
    "text/html",
    "application/msword",
    "application/octet-stream",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "vnd.openxmlformats-officedocument.presentationml.presentation"
]
