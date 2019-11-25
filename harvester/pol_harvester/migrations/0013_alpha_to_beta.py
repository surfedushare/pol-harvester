from django.db import migrations


def migrate_annotations(apps, schema_editor):

    Annotation = apps.get_model('pol_harvester', 'Annotation')
    Arrangement = apps.get_model('pol_harvester', 'Arrangement')
    Document = apps.get_model('pol_harvester', 'Document')

    noop = 0
    success = 0
    fail = 0

    for annotation in Annotation.objects.all():
        doc = Document.objects.filter(reference=annotation.reference, freeze__name="beta").last()
        if doc is not None:
            noop += 1
            continue
        # We've found an Annotation that is missing a Document
        arr = Arrangement.objects.filter(meta__reference_id=annotation.reference).last()
        if arr is not None:
            doc = arr.document_set.first()
            annotation.reference = doc.reference
            annotation.save()
            success += 1
        else:
            annotation.delete()
            fail += 1

    # print(f"Noop: {noop}", f"Success: {success}", f"Fail: {fail}")
    # out: Noop: 183 Success: 79 Fail: 99


class Migration(migrations.Migration):

    dependencies = [
        ('pol_harvester', '0012_optional_schema'),
    ]

    operations = [
        migrations.RunPython(
            migrate_annotations,
            lambda app, schema_editor: None  # ignores any reverse migrations
        ),
    ]
