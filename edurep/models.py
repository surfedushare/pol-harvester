from datagrowth.resources import HttpResource


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
        if next_record > 900:
            return {}
        return {
            "startRecord": next_record
        }

    class Meta:
        verbose_name_plural = "Edurep searches"
