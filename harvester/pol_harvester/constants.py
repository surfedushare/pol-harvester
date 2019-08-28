class HarvestStages:
    NEW = "New"
    BASIC = "Basic"
    VIDEO = "Video"
    COMPLETE = "Complete"

HARVEST_STAGE_CHOICES = [
    (value, value) for attr, value in sorted(HarvestStages.__dict__.items()) if not attr.startswith("_")
]
