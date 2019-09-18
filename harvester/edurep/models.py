from django.db import models
from datagrowth.resources import HttpResource, HttpFileResource

from pol_harvester.models import Freeze
from pol_harvester.constants import HarvestStages, HARVEST_STAGE_CHOICES


class EdurepSearch(HttpResource):

    URI_TEMPLATE = "http://wszoeken.edurep.kennisnet.nl:8000/edurep/sruns?query={}"
    PARAMETERS = {
        "operation": "searchRetrieve",
        "version": "1.2",
        "recordPacking": "xml",
        "maximumRecords": 100
    }

    def next_parameters(self):
        content_type, content = self.content
        next_record_element = content.find("srw:nextrecordposition")
        if next_record_element is None:
            return {}
        next_record = int(next_record_element.text)
        if next_record > 901:
            return {}
        return {
            "startRecord": next_record
        }

    class Meta:
        verbose_name_plural = "Edurep searches"


class EdurepFile(HttpFileResource):
    pass


class EdurepSource(models.Model):

    name = models.CharField(max_length=50)
    query = models.CharField(max_length=255)
    freezes = models.ManyToManyField(Freeze, through="EdurepHarvest")
    collection_name = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class EdurepHarvest(models.Model):

    source = models.ForeignKey(EdurepSource)
    freeze = models.ForeignKey(Freeze)

    scheduled_after = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    stage = models.CharField(max_length=50, choices=HARVEST_STAGE_CHOICES, default=HarvestStages.NEW)

    def clean(self):
        if not self.id:
            self.stage = HarvestStages.NEW
