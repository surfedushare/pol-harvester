from urlobject import URLObject
from dateutil.parser import parse as parse_date_string

from django.utils.timezone import datetime, make_aware
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

    GET_SCHEMA = {
        "args": {
            "type": "array",
            "items": [
                {
                    "type": "string"
                },
                {
                    "type": "string",
                    "pattern": "^\d{4}-\d{2}-\d{2}(T\d{2}\:\d{2}\:\d{2}Z)?$"
                }
            ],
            "minItems": 1,
            "additionalItems": False
        }
    }

    set_specification = models.CharField(max_length=255, blank=True, null=False)
    since = models.DateTimeField()

    URI_TEMPLATE = "http://oai.edurep.kennisnet.nl:8001/edurep/oai?set={}&from={}"
    PARAMETERS = {
        "verb": "ListRecords",
        "metadataPrefix": "lom"
    }

    def next_parameters(self):
        content_type, soup = self.content
        resumption_token = soup.find("resumptiontoken")
        if not resumption_token or not resumption_token.text:
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

    def variables(self, *args):
        vars = super().variables(*args)
        since_time = None
        if len(vars["url"]) >= 2:
            since_time = vars["url"][1]
            if isinstance(since_time, str):
                since_time = parse_date_string(since_time)
        vars["since"] = make_aware(since_time)
        return vars

    def clean(self):
        super().clean()
        variables = self.variables()
        if not self.set_specification and len(variables["url"]):
            self.set_specification = variables["url"][0]
        if not self.since:
            self.since = variables.get("since", None)

    def send(self, method, *args, **kwargs):
        # We're sending along a default "from" parameter in a distant past to get all materials
        # if a set has been specified, but no start date.
        if len(args) == 1:
            args = (args[0], "1970-01-01T00:00:00Z")
        return super().send(method, *args, **kwargs)

    def validate_request(self, request, validate_input=True):
        # Casting datetime to string, because we need strings to pass validation
        request["args"] = (request["args"][0], str(request["args"][1]))
        return super().validate_request(request, validate_input=validate_input)

    def handle_errors(self):
        content_type, soup = self.content
        # If there is no response at all we indicate a service not available
        # Note that the IP might be blocked by Edurep
        if soup is None:
            self.status = 503
            super().handle_errors()
            return
        # Edurep always responds with a 200, but it may contain an error tag
        # If not we're fine and done handling errors
        error = soup.find("error")
        if error is None:
            return
        # If an error was found we translate it into an appropriate code
        status = error["code"]
        if status == "badArgument":
            self.status = 400
        elif status == "noRecordsMatch":
            self.status = 204
        # And we raise proper exceptions for the system to pick up
        super().handle_errors()

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

    source = models.ForeignKey(EdurepSource, on_delete=models.CASCADE)
    freeze = models.ForeignKey(Freeze, on_delete=models.CASCADE)

    latest_update_at = models.DateTimeField(
        null=True, blank=True, default=make_aware(datetime(year=1970, month=1, day=1))
    )
    harvested_at = models.DateTimeField(null=True, blank=True)
    stage = models.CharField(max_length=50, choices=HARVEST_STAGE_CHOICES, default=HarvestStages.NEW)

    def clean(self):
        if not self.id:
            self.stage = HarvestStages.NEW

    def reset(self):
        self.latest_update_at = make_aware(datetime(year=1970, month=1, day=1))
        self.harvested_at = None
        self.stage = HarvestStages.NEW
        self.save()
