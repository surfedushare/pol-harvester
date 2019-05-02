import warnings
import os
from lxml import etree


class WurLibrary4Learning(object):

    def __init__(self, source):
        self.source = source
        self.data = {}
        self.load()

    def __iter__(self):
        return iter(self.data.values())

    def load(self):
        error_count = 0
        meta_file_path = os.path.join(self.source, "library4learning-metadata.xml")
        texts_file_path = os.path.join(self.source, "library4learning-fulltext.xml")
        with open(meta_file_path) as meta_file, open(texts_file_path, "rb") as texts_file:
            meta_tree = etree.parse(meta_file)
            texts_tree = etree.parse(texts_file)

        for source in meta_tree.findall("lfl"):
            id_element = source.find("id")
            title_element = source.find("title")
            url_element = source.find("link").find("url")
            keyword_elements = source.findall("keyword")
            self.data[id_element.text] = {
                "id": id_element.text,
                "url": url_element.text,
                "keywords": [el.find("eng").text for el in keyword_elements],
                "documents": [{
                    "url": url_element.text,
                    "title": title_element.text,
                    "text": None,  # gets set later
                    "content_type": "video/mp4"  # assumption, file type is not in the meta data
                }]
            }

        for document in texts_tree.findall("record"):
            document_id = document.get("id")
            source = self.data.get(document_id, None)
            if source is None:
                warnings.warn("Failed to load text of {} because meta data is missing".format(document_id))
                error_count += 1
                continue
            transcript = document.find("transcript")
            if transcript is None:
                warnings.warn("Failed to load text of {} because text is missing".format(document_id))
                error_count += 1
                continue
            source["documents"][0]["text"] = transcript.text.replace("\xa0", " ").strip('"')

        return error_count
