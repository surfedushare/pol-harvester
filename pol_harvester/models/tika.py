from datagrowth.resources import HttpResource


class HttpTikaResource(HttpResource):
    URI_TEMPLATE = "https://analyzer.metadata.surfcatalog.nl/upload"
    FILE_DATA_KEYS = ["file"]
