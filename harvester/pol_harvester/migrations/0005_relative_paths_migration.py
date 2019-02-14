import os

from django.db import migrations

from datagrowth.resources import HttpResource


def relative_path_migration(apps, schema_editor):
    Tika = apps.get_model('pol_harvester', 'HttpTikaResource')
    for resource in Tika.objects.filter(status=200):
        resource.request["kwargs"]["file"] = resource.request["kwargs"]["file"] \
            .replace("/home/surf/pol-harvester/media/", "") \
            .lstrip(os.sep)
        resource.data_hash = HttpResource.hash_from_data(resource.request["kwargs"])
        resource.save()


class Migration(migrations.Migration):

    dependencies = [
        ('pol_harvester', '0004_youtubedlresource'),
    ]

    operations = [
        migrations.RunPython(
            relative_path_migration,
            lambda app, schema_editor: None  # ignores any reverse migrations
        ),
    ]
