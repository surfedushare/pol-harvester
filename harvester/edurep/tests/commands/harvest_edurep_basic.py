from unittest.mock import patch
from io import StringIO
from datetime import datetime

from django.test import TestCase
from django.core.management import call_command
from django.utils.timezone import make_aware

from pol_harvester.constants import HarvestStages
from edurep.models import EdurepHarvest
from edurep.management.commands.harvest_edurep_basic import Command as BasicHarvestCommand


GET_EDUREP_OAIPMH_SEEDS_TARGET = "edurep.management.commands.harvest_edurep_basic.get_edurep_oaipmh_seeds"
DOWNLOAD_SEED_FILES_TARGET = "edurep.management.commands.harvest_edurep_basic.Command.download_seed_files"
EXTRACT_FROM_SEEDS_TARGET = "edurep.management.commands.harvest_edurep_basic.Command.extract_from_seed_files"
SEND_SERIE_TARGET = "edurep.management.commands.harvest_edurep_basic.send_serie"
DUMMY_SEEDS = [
    {"state": "dummy", "url": "https://www.vn.nl/speciaalmelk-rechtstreeks-koe/", "mime_type": "text/html"},
    {"state": "dummy", "url": "http://www.samhao.nl/webopac/MetaDataEditDownload.csp?file=2:145797:1", "mime_type": "application/pdf"}
]


class TestBasicHarvest(TestCase):

    fixtures = ["freezes-new", "surf-oaipmh-1970-01-01", "resources"]

    def get_command_instance(self):
        command = BasicHarvestCommand()
        command.show_progress = False
        command.info = lambda x: x
        return command

    @patch(GET_EDUREP_OAIPMH_SEEDS_TARGET, return_value=DUMMY_SEEDS)
    @patch(DOWNLOAD_SEED_FILES_TARGET, return_value=[1])
    @patch(EXTRACT_FROM_SEEDS_TARGET)
    def test_basic_surf(self, extract_target, download_target, seeds_target):
        # Checking whether end result of the command returned by "handle" matches expectations.
        # We'd expect the command to get seeds from get_edurep_oaipmh_seeds function.
        # After that the heavy lifting is done by two methods named download_seed_files and extract_from_seed_files.
        # We'll test those separately, but check if they get called with the seeds returned by get_edurep_oaipmh_seeds
        out = StringIO()
        call_command("harvest_edurep_basic", "--freeze=delta", "--no-progress", stdout=out)
        # Asserting usage of get_edurep_oaipmh_seeds
        seeds_target.assert_called_once_with(
            "surf", make_aware(datetime(year=1970, month=1, day=1)),
            include_deleted=False
        )
        # Asserting usage of download_seed_files
        download_target.assert_called_once_with(DUMMY_SEEDS)
        # And then usage of extract_from_seeds
        extract_target.assert_called_once_with(DUMMY_SEEDS, [1], [])
        # Last but not least we check that the correct EdurepHarvest objects have indeed progressed
        # to prevent repetitious harvests.
        surf_harvest = EdurepHarvest.objects.get(source__collection_name="surf")
        self.assertEqual(
            surf_harvest.stage,
            HarvestStages.BASIC,
            "surf set harvest should got updated to stage BASIC to prevent re-harvest in the future"
        )
        edurep_delen_harvest = EdurepHarvest.objects.get(source__collection_name="edurep_delen")
        self.assertEqual(
            edurep_delen_harvest.stage,
            HarvestStages.COMPLETE,
            "edurep_delen set harvest got updated to other than COMPLETE while we expected it to be ignored"
        )

    @patch(GET_EDUREP_OAIPMH_SEEDS_TARGET, return_value=DUMMY_SEEDS)
    @patch(DOWNLOAD_SEED_FILES_TARGET, return_value=[12024, 12025])
    @patch(EXTRACT_FROM_SEEDS_TARGET)
    def test_basic_surf_skip(self, extract_target, download_target, seeds_target):
        # Here we test the rare scenario where we want to skip certain mime types when extracting
        out = StringIO()
        call_command(
            "harvest_edurep_basic", "--freeze=delta", "--skip-mime-types=text/html,application/pdf", "--no-progress",
            stdout=out
        )
        # Asserting usage of get_edurep_oaipmh_seeds
        seeds_target.assert_called_once_with(
            "surf", make_aware(datetime(year=1970, month=1, day=1)),
            include_deleted=False
        )
        # Asserting usage of download_seed_files
        download_target.assert_called_once_with(DUMMY_SEEDS)
        # And then usage of extract_from_seeds
        extract_target.assert_called_once_with(DUMMY_SEEDS, [12024, 12025], ["text/html", "application/pdf"])
        # Last but not least we check that the correct EdurepHarvest objects have indeed progressed
        # to prevent repetitious harvests.
        surf_harvest = EdurepHarvest.objects.get(source__collection_name="surf")
        self.assertEqual(
            surf_harvest.stage,
            HarvestStages.BASIC,
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

    def test_download_seed_files(self):
        # Asserting Datagrowth usage for downloading files.
        # This handles many edge cases for us.
        command = self.get_command_instance()
        with patch("edurep.management.commands.harvest_edurep_basic.send_serie", return_value=[[12024, 12025], []]) as send_serie_mock:
            command.download_seed_files(DUMMY_SEEDS)
        self.assertEqual(send_serie_mock.call_count, 1, "More than 1 call to send_serie?")
        args, kwargs = send_serie_mock.call_args
        config = kwargs["config"]
        self.assertEqual(config.resource, "edurep.EdurepFile", "Wrong resource used for downloading files")
        self.assertEqual(
            args,
            (
                [
                    ['https://www.vn.nl/speciaalmelk-rechtstreeks-koe/'],
                    ['http://www.samhao.nl/webopac/MetaDataEditDownload.csp?file=2:145797:1']
                ],
                [{}, {}],
            ),
            "Wrong arguments given to send_serie processing multiple edurep.EdurepFile")
        self.assertEqual(kwargs["method"], "get", "edurep.EdurepFile is not using HTTP GET method")

    def test_extract_from_seed_files(self):
        # Asserting Datagrowth usage for extracting content from files with Tika.
        # This handles many edge cases for us.
        command = self.get_command_instance()
        with patch(SEND_SERIE_TARGET, return_value=[[1, 2], []]) as send_serie_mock:
            command.extract_from_seed_files(DUMMY_SEEDS, [12024, 12025], [])
        self.assertEqual(send_serie_mock.call_count, 1, "More than 1 call to send_serie?")
        args, kwargs = send_serie_mock.call_args
        config = kwargs["config"]
        self.assertEqual(config.resource, "pol_harvester.HttpTikaResource",
                         "Wrong resource used for extracting content")
        self.assertEqual(
            args,
            (
                [[], []],
                [
                    {
                        "file": "edurep/downloads/7/c7/20191209102536078995.index.html"
                    },
                    {
                        "file": "edurep/downloads/f/03/20191209102536508370.MetaDataEditDownload.csp"
                    }
                ],
            ),
            "Wrong arguments given to send_serie processing multiple pol_harvester.HttpTikaResource"
        )
        self.assertEqual(kwargs["method"], "post", "pol_harvester.HttpTikaResource is not using HTTP POST method")

        # Now calling the same method, but specify a list of contenttypes to exclude
        send_serie_mock.reset_mock()
        with patch(SEND_SERIE_TARGET, return_value=[[1, 2], []]) as send_serie_mock:
            command.extract_from_seed_files(DUMMY_SEEDS, [12024, 12025], ["application/pdf"])
        self.assertEqual(send_serie_mock.call_count, 1, "More than 1 call to send_serie?")
        args, kwargs = send_serie_mock.call_args
        config = kwargs["config"]
        self.assertEqual(config.resource, "pol_harvester.HttpTikaResource",
                         "Wrong resource used for extracting content")
        self.assertEqual(
            args,
            (
                [[]],
                [
                    {
                        "file": "edurep/downloads/7/c7/20191209102536078995.index.html"
                    }
                ],
            ),
            "Wrong arguments given to send_serie processing multiple pol_harvester.HttpTikaResource"
        )
        self.assertEqual(kwargs["method"], "post", "pol_harvester.HttpTikaResource is not using HTTP POST method")
