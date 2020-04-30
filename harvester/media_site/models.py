from dateutil.parser import parse as parse_date_string

from django.utils.timezone import make_aware
from django.db import models

from datagrowth.resources import HttpResource


class MediaSiteOAIPMH(HttpResource):

    GET_SCHEMA = {
        "args": {
            "type": "array",
            "items": [
                {
                    "type": "string",
                    "pattern": "^\d{4}-\d{2}-\d{2}(T\d{2}\:\d{2}\:\d{2}Z)?$"
                }
            ],
            "minItems": 1,
            "additionalItems": False
        }
    }

    since = models.DateTimeField()

    URI_TEMPLATE = "https://zoepportal.nl/oai/html/?from={}"
    PARAMETERS = {
        "verb": "ListRecords",
        "metadataPrefix": "oai_lom"
    }

    def variables(self, *args):
        vars = super().variables(*args)
        since_time = None
        if len(vars["url"]) >= 1:
            since_time = vars["url"][0]
            if isinstance(since_time, str):
                since_time = parse_date_string(since_time)
        #vars["since"] = make_aware(since_time)
        return vars

    def clean(self):
        super().clean()
        variables = self.variables()
        if not self.since:
            self.since = variables.get("since", None)

    def send(self, method, *args, **kwargs):
        # We're sending along a default "from" parameter in a distant past to get all materials
        # if no start date was specified
        if len(args) == 0:
            args = ("2016-01-01T00:00:00Z",)
        return super().send(method, *args, **kwargs)

    def validate_request(self, request, validate_input=True):
        # Casting datetime to string, because we need strings to pass validation
        request["args"] = (str(request["args"][0]),)
        return super().validate_request(request, validate_input=validate_input)

    class Meta:
        verbose_name = "MediaSite OAIPMH harvest"
        verbose_name_plural = "MediaSite OAIPMH harvests"
