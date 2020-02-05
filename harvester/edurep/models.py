from urlobject import URLObject
from datetime import datetime

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


class EdurepOAIPMH(HttpResource):

    # TODO: add UTC datetime validation (no millis) for (optional) "from" argument
    # TODO: do something with 200 errors

    set_specification = models.CharField(max_length=255, blank=True, null=False)

    URI_TEMPLATE = "http://oai.edurep.kennisnet.nl:8001/edurep/oai?set={}&from={}"
    PARAMETERS = {
        "verb": "ListRecords",
        "metadataPrefix": "lom"
    }

    def next_parameters(self):
        content_type, soup = self.content
        resumption_token = soup.find("resumptiontoken")
        if not resumption_token:
            return {}
        return {
            "verb": "ListRecords",
            "resumptionToken": resumption_token.text
        }

    def create_next_request(self):
        next_request = super().create_next_request()
        if not next_request:
            return
        url = URLObject(next_request.get("url"))
        url = url.without_query().set_query_params(**self.next_parameters())
        next_request["url"] = str(url)
        return next_request

    def clean(self):
        variables = self.variables()
        if not self.set_specification and len(variables["url"]):
            self.set_specification = variables["url"][0]

    class Meta:
        verbose_name = "Edurep OAIPMH harvest"
        verbose_name_plural = "Edurep OAIPMH harvests"


class EdurepFile(HttpFileResource):
    pass


class EdurepSource(models.Model):

    name = models.CharField(max_length=50)
    query = models.CharField(max_length=255, null=True, blank=True)
    freezes = models.ManyToManyField(Freeze, through="EdurepHarvest")
    collection_name = models.CharField(
        max_length=255,
        help_text="This name will be given to the collection holding all documents for this source. "
                  "When dealing with OAI-PMH this value will be the setSpec value"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class EdurepHarvest(models.Model):

    source = models.ForeignKey(EdurepSource)
    freeze = models.ForeignKey(Freeze)

    latest_update_at = models.DateTimeField(null=True, blank=True, default=datetime(year=1970, month=1, day=1))
    completed_at = models.DateTimeField(null=True, blank=True)
    stage = models.CharField(max_length=50, choices=HARVEST_STAGE_CHOICES, default=HarvestStages.NEW)

    def clean(self):
        if not self.id:
            self.stage = HarvestStages.NEW
