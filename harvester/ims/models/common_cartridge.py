import json
import os
from zipfile import ZipFile

from bs4 import BeautifulSoup

from django.conf import settings
from django.db import models
from django import forms
from django.core.exceptions import ValidationError


class CommonCartridge(models.Model):

    file = models.FileField(max_length=255)
    manifest = models.TextField(blank=True)
    upload_at = models.DateTimeField(auto_now_add=True)

    def get_metadata(self):
        manifest = BeautifulSoup(self.manifest, "lxml")
        schema = manifest.find('schema').text
        title = manifest.find('lomcc:title').find('lomcc:string').text if schema == "IMS Common Cartridge" else \
                manifest.find('imsmd:title').find('imsmd:langstring').text
        return {
            'schema': {
                'type': schema,
                'version': manifest.find('schemaversion').text
            },
            'title': title
        }

    def get_content_tree(self):
        manifest = BeautifulSoup(self.manifest, "lxml")
        return manifest.find('organization').find('item')

    def get_resources(self):
        manifest = BeautifulSoup(self.manifest, "lxml")
        results = {}
        resources = manifest.find_all('resource', identifier=True)
        for resource in resources:
            results[resource['identifier']] = {
                'content_type': resource['type'],
                'main': resource.get('href', None),
                'files': [file['href'] for file in resource.find_all('file')]
            }
        return results

    def get_extract_destination(self):
        tail, head = os.path.split(self.file.name)
        return os.path.join(settings.MEDIA_ROOT, "tmp", head)

    def extract(self):
        destination = self.get_extract_destination()
        if os.path.exists(destination):
            return
        cartridge = ZipFile(self.file)
        cartridge.extractall(destination)

    def metadata_tag(self):
        return '<pre>{}</pre>'.format(json.dumps(self.get_metadata(), indent=4))
    metadata_tag.short_description = 'Metadata'
    metadata_tag.allow_tags = True

    def clean(self):
        cartridge = ZipFile(self.file)
        try:
            self.manifest = cartridge.read('imsmanifest.xml')
        except KeyError:
            raise ValidationError('The common cartridge should contain a manifest file')

    @property
    def success(self):
        return bool(self.manifest)

    def __str__(self):
        tail, head = os.path.split(self.file.name)
        return head


class CommonCartridgeForm(forms.ModelForm):

    def clean(self):
        self.instance.clean()  # TODO: is this necessary?
        # TODO: check metadata
        super().clean()

    class Meta:
        model = CommonCartridge
        fields = ['file']
