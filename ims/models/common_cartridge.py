import json
import os
from zipfile import ZipFile

from bs4 import BeautifulSoup

from django.db import models
from django import forms
from django.urls import reverse
from django.core.exceptions import ValidationError


class CommonCartridge(models.Model):

    file = models.FileField()
    manifest = models.TextField(blank=True)
    upload_at = models.DateTimeField(auto_now_add=True)

    def get_metadata(self):
        manifest = BeautifulSoup(self.manifest, "lxml")
        return {
            'schema': {
                'type': manifest.find('schema').text,
                'version': manifest.find('schemaversion').text
            },
            'title': manifest.find('lomimscc:title').find('lomimscc:string').text,
            'export_at': manifest.find('lomimscc:contribute').find('lomimscc:date').find('lomimscc:datetime').text,
            'license': manifest.find('lomimscc:rights').find('lomimscc:description').find('lomimscc:string').text
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
                'main': resource['href'],
                'files': [file['href'] for file in resource.find_all('file')]
            }
        return results

    def get_absolute_url(self):
        return reverse('share:common-cartridge-upload-success', kwargs={"pk": self.id})

    def metadata_tag(self):
        return '<pre>{}</pre>'.format(json.dumps(self.get_metadata(), indent=4))
    metadata_tag.short_description = 'Metadata'
    metadata_tag.allow_tags = True

    def __str__(self):
        tail, head = os.path.split(self.file.name)
        return head


class CommonCartridgeForm(forms.ModelForm):

    def clean(self):
        cartridge = ZipFile(self.files['file'])
        try:
            self.instance.manifest = cartridge.read('imsmanifest.xml')
        except KeyError:
            raise ValidationError('The common cartridge should contain a manifest file')
        # TODO: check metadata
        super().clean()

    class Meta:
        model = CommonCartridge
        fields = ['file']
