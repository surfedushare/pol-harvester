from django.db import migrations


def migrate_query_rankings(apps, schema_editor):

    from search.models import QueryRanking  # needed to use get_elastic_ratings method
    from pol_harvester.models import Freeze  # needed to set foreign key
    Arrangement = apps.get_model('pol_harvester', 'Arrangement')
    Document = apps.get_model('pol_harvester', 'Document')

    beta_freeze = Freeze.objects.get(name="beta")
    noop = 0
    success = 0
    fail = 0

    for query_ranking in QueryRanking.objects.filter(freeze__name="alpha"):
        migrated_ranking = {}
        for reference, rating in query_ranking.get_elastic_ratings(as_dict=True).items():
            doc = Document.objects.filter(reference=reference, freeze__name="beta").last()
            if doc is not None:
                noop += 1
                migrated_ranking[f"beta:{reference}"] = rating
                continue
            arr = Arrangement.objects.filter(meta__reference_id=reference).last()
            if arr is not None:
                doc = arr.document_set.first()
                migrated_ranking[f"beta:{doc.reference}"] = rating
                success += 1
            else:
                fail += 1
                continue

        query_ranking.ranking = migrated_ranking
        query_ranking.freeze = beta_freeze
        query_ranking.save()

    # print(f"Noop: {noop}", f"Success: {success}", f"Fail: {fail}")
    # out: Noop: 145 Success: 30 Fail: 71


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0003_googletext'),
    ]

    operations = [
        migrations.RunPython(
            migrate_query_rankings,
            lambda app, schema_editor: None  # ignores any reverse migrations
        ),
    ]
