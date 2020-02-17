from unittest.mock import patch
from io import StringIO
from datetime import datetime

from django.test import TestCase
from django.core.management import call_command
from django.utils.timezone import make_aware

from pol_harvester.models import Freeze, Collection
from pol_harvester.constants import HarvestStages
from edurep.models import EdurepHarvest
from edurep.management.commands.freeze_edurep import Command as FreezeCommand
from edurep.utils import get_edurep_oaipmh_seeds


GET_EDUREP_OAIPMH_SEEDS_TARGET = "edurep.management.commands.freeze_edurep.get_edurep_oaipmh_seeds"
HANDLE_UPSERT_SEEDS_TARGET = "edurep.management.commands.freeze_edurep.Command.handle_upsert_seeds"
HANDLE_DELETION_SEEDS_TARGET = "edurep.management.commands.freeze_edurep.Command.handle_deletion_seeds"
SEND_SERIE_TARGET = "edurep.management.commands.harvest_edurep_basic.send_serie"
DUMMY_SEEDS = [
    {"state": "active", "url": "https://www.vn.nl/speciaalmelk-rechtstreeks-koe/", "mime_type": "text/html"},
    {"state": "active", "url": "http://www.samhao.nl/webopac/MetaDataEditDownload.csp?file=2:145797:1", "mime_type": "application/pdf"},
    {"state": "deleted", "url": None, "mime_type": None}
]


class TestFreezeNoHistory(TestCase):

    fixtures = ["freezes-new", "surf-oaipmh-1970-01-01", "resources"]

    def setUp(self):
        # Setting the stage of the "surf" set harvests to VIDEO.
        # The only valid stage for "freeze_edurep" to act on.
        EdurepHarvest.objects.filter(source__collection_name="surf").update(stage=HarvestStages.VIDEO)

    def get_command_instance(self):
        command = FreezeCommand()
        command.show_progress = False
        command.info = lambda x: x
        return command

    @patch(GET_EDUREP_OAIPMH_SEEDS_TARGET, return_value=DUMMY_SEEDS)
    @patch(HANDLE_UPSERT_SEEDS_TARGET, return_value=[0, 7, 14])
    @patch(HANDLE_DELETION_SEEDS_TARGET, return_value=[1, 3])
    def test_freeze(self, deletion_target, upsert_target, seeds_target):
        # Checking whether end result of the command returned by "handle" matches expectations.
        # We'd expect the command to get seeds from get_edurep_oaipmh_seeds function.
        # After that the modifications to the freeze are done by two methods named:
        # handle_upsert_seeds and handle_deletion_seeds.
        # We'll test those separately, but check if they get called with the seeds returned by get_edurep_oaipmh_seeds
        out = StringIO()
        call_command("freeze_edurep", "--freeze=delta", "--no-progress", stdout=out)
        # Asserting usage of get_edurep_oaipmh_seeds
        seeds_target.assert_called_once_with("surf", make_aware(datetime(year=1970, month=1, day=1)))
        # Asserting usage of download_seed_files
        upsert_target.assert_called_once()
        args, kwargs = upsert_target.call_args
        self.assertIsInstance(args[0], Collection)
        self.assertEqual(args[1], DUMMY_SEEDS[:-1])
        # And then usage of extract_from_seeds
        deletion_target.assert_called_once()
        args, kwargs = deletion_target.call_args
        self.assertIsInstance(args[0], Collection)
        self.assertEqual(args[1], DUMMY_SEEDS[-1:])
        # Last but not least we check that the correct EdurepHarvest objects have indeed progressed
        # to prevent repetitious harvests.
        surf_harvest = EdurepHarvest.objects.get(source__collection_name="surf")
        self.assertEqual(
            surf_harvest.stage,
            HarvestStages.COMPLETE,
            "surf set harvest should got updated to stage BASIC to prevent re-harvest in the future"
        )
        edurep_delen_harvest = EdurepHarvest.objects.get(source__collection_name="edurep_delen")
        self.assertEqual(
            edurep_delen_harvest.stage,
            HarvestStages.COMPLETE,
            "edurep_delen set harvest got updated to other than COMPLETE while we expected it to be ignored"
        )

    def test_basic_invalid_freeze(self):
        # Testing the case where a Freeze does not exist at all
        try:
            call_command("harvest_edurep_seeds", "--freeze=invalid")
            self.fail("harvest_edurep_seeds did not raise for an invalid freeze")
        except EdurepHarvest.DoesNotExist:
            pass
        # Testing the case where a Freeze exists, but no harvest tasks are present
        surf_harvest = EdurepHarvest.objects.get(source__collection_name="surf")
        surf_harvest.stage = HarvestStages.BASIC
        surf_harvest.save()
        try:
            call_command("harvest_edurep_seeds", "--freeze=invalid")
            self.fail("harvest_edurep_seeds did not raise for a freeze without pending harvests")
        except EdurepHarvest.DoesNotExist:
            pass

    def test_handle_upsert_seeds(self):
        freeze = Freeze.objects.last()
        collection = Collection.objects.create(name="surf", freeze=freeze)
        command = self.get_command_instance()
        upserts = [
            seed
            for seed in get_edurep_oaipmh_seeds("surf", make_aware(datetime(year=1970, month=1, day=1)))
            if seed.get("state", "active") == "active"
        ]
        skipped, dumped, documents_count = command.handle_upsert_seeds(collection, upserts)
        # When dealing with an entirely new Freeze
        # Then the arrangement count and document count should equal output of handle_upsert_seeds
        self.assertEqual(collection.arrangement_set.count(), dumped)
        self.assertEqual(collection.document_set.count(), documents_count)


    def test_handle_deletion_seeds(self):
        freeze = Freeze.objects.last()
        collection = Collection.objects.create(name="surf", freeze=freeze)
        command = self.get_command_instance()
        deletes = [
            seed
            for seed in get_edurep_oaipmh_seeds("surf", make_aware(datetime(year=1970, month=1, day=1)))
            if seed.get("state", "active") != "active"
        ]
        # Basically we're testing that deletion seeds are not triggering errors when their targets do not exist.
        command.handle_deletion_seeds(collection, deletes)
        self.assertEqual(collection.document_set.count(), 0)
        self.assertEqual(collection.arrangement_set.count(), 0)


class TestFreezeWithHistory(TestCase):

    fixtures = ["freezes-history", "surf-oaipmh-2020-01-01", "resources"]

    def setUp(self):
        # Setting the stage of the "surf" set harvests to VIDEO.
        # The only valid stage for "freeze_edurep" to act on.
        EdurepHarvest.objects.filter(source__collection_name="surf").update(stage=HarvestStages.VIDEO)

    def get_command_instance(self):
        command = FreezeCommand()
        command.show_progress = False
        command.info = lambda x: x
        return command

    def test_handle_upsert_seeds(self):
        freeze = Freeze.objects.last()
        collection = Collection.objects.create(name="surf", freeze=freeze)
        command = self.get_command_instance()
        upserts = [
            seed
            for seed in get_edurep_oaipmh_seeds("surf", make_aware(datetime(year=2019, month=12, day=31)))
            if seed.get("state", "active") == "active"
        ]
        command.handle_upsert_seeds(collection, upserts)
        self.assertEqual(collection.document_set.count(), 6)
        self.assertEqual(collection.arrangement_set.count(), 6)

    def test_handle_deletion_seeds(self):
        freeze = Freeze.objects.last()
        collection = Collection.objects.create(name="surf", freeze=freeze)
        command = self.get_command_instance()
        arrangement_count = collection.arrangement_set.count()
        document_count = collection.document_set.count()
        deletes = [
            seed
            for seed in get_edurep_oaipmh_seeds("surf", make_aware(datetime(year=2019, month=12, day=31)))
            if seed.get("state", "active") != "active"
        ]
        arrangement_deletes, document_deletes = command.handle_deletion_seeds(collection, deletes)
        self.assertEqual(collection.arrangement_set.count(), arrangement_count - arrangement_deletes)
        self.assertEqual(collection.document_set.count(), document_count - document_deletes)
