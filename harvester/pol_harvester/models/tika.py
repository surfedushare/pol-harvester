from datagrowth.resources import HttpResource, TikaResource


class HttpTikaResource(HttpResource):
    URI_TEMPLATE = "https://analyzer.metadata.surfcatalog.nl/upload"
    FILE_DATA_KEYS = ["file"]


class ShellTikaResource(TikaResource):
    pass
