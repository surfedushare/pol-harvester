from html import unescape


class EdurepDataExtraction(object):

    @staticmethod
    def find_all_classification_blocks(element, classification_type, output_type):
        assert output_type in ["czp:entry", "czp:id"]
        entries = element.find_all(string=classification_type)
        blocks = []
        for entry in entries:
            classification_element = entry.find_parent('czp:classification')
            if not classification_element:
                continue
            blocks += classification_element.find_all(output_type)
        return blocks

    @classmethod
    def get_records(cls, soup):
        return soup.find_all('srw:record')

    @classmethod
    def get_external_id(cls, soup, el):
        return el.find('srw:recordidentifier').text

    @classmethod
    def get_url(cls, soup, el):
        node = el.find('czp:location')
        return node.text if node else None

    @classmethod
    def get_title(cls, soup, el):
        node = el.find('czp:title')
        if node is None:
            return
        translation = node.find('czp:langstring')
        return unescape(translation.text) if translation else None

    @classmethod
    def get_language(cls, soup, el):
        node = el.find('czp:language')
        return node.text if node else None

    @classmethod
    def get_keywords(cls, soup, el):
        nodes = el.find_all('czp:keyword')
        return [
            unescape(node.find('czp:langstring').text)
            for node in nodes
        ]

    @classmethod
    def get_description(cls, soup, el):
        node = el.find('czp:description')
        if node is None:
            return
        translation = node.find('czp:langstring')
        return unescape(translation.text) if translation else None

    @classmethod
    def get_mime_type(cls, soup, el):
        node = el.find('czp:format')
        return node.text if node else None

    @classmethod
    def get_copyright(clscls, soup, el):
        node = el.find('czp:copyrightandotherrestrictions')
        return node.find('czp:value').find('czp:langstring').text if node else None

    @classmethod
    def get_author(cls, soup, el):
        author = el.find(string='author')
        if not author:
            return []
        contribution = author.find_parent('czp:contribute')
        if not contribution:
            return []
        nodes = contribution.find_all('czp:vcard')
        return [
            unescape(node.text)
            for node in nodes
        ]

    @classmethod
    def get_publisher_date(cls, soup, el):
        publisher = el.find(string='publisher')
        if not publisher:
            return
        contribution = publisher.find_parent('czp:contribute')
        if not contribution:
            return
        datetime = contribution.find('czp:datetime')
        if not datetime:
            return
        return datetime.text

    @classmethod
    def get_lom_educational_levels(cls, soup, el):
        educational = el.find('czp:educational')
        if not educational:
            return []
        contexts = educational.find_all('czp:context')
        if not contexts:
            return []
        educational_levels = [
            edu.find('czp:value').find('czp:langstring').text
            for edu in contexts
        ]
        return list(set(educational_levels))

    @classmethod
    def get_educational_levels(cls, soup, el):
        blocks = cls.find_all_classification_blocks(el, "educational level", "czp:id")
        return list(set([block.text for block in blocks]))

    @classmethod
    def get_humanized_educational_levels(cls, soup, el):
        blocks = cls.find_all_classification_blocks(el, "educational level", "czp:entry")
        return list(set([block.find('czp:langstring').text for block in blocks]))

    @classmethod
    def get_disciplines(cls, soup, el):
        blocks = cls.find_all_classification_blocks(el, "discipline", "czp:id")
        return list(set([block.text for block in blocks]))

    @classmethod
    def get_humanized_disciplines(cls, soup, el):
        blocks = cls.find_all_classification_blocks(el, "discipline", "czp:entry")
        return list(set([block.find('czp:langstring').text for block in blocks]))
