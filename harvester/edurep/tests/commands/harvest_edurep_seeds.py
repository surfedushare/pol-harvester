from unittest.mock import patch
from io import StringIO
from datetime import datetime

from django.test import TestCase
from django.core.management import call_command
from django.utils.timezone import make_aware

from datagrowth.resources.http.tasks import send
from pol_harvester.constants import HarvestStages
from edurep.models import EdurepHarvest


class TestSeedHarvest(TestCase):

    fixtures = ["freezes", "surf-oaipmh-1970-01-01"]

    def test_edurep_surf(self):
        # Checking whether end result of the command returned by "handle" matches expectations.
        # We'd expect two OAI-PMH calls to be made which should be both a success.
        # Apart from the main results we want to check if Datagrowth was used for execution.
        # This makes sure that a lot of edge cases will be covered like HTTP errors.
        out = StringIO()
        with patch("edurep.management.commands.harvest_edurep_seeds.send", wraps=send) as send_mock:
            call_command("harvest_edurep_seeds", "--freeze=delta", "--no-progress", stdout=out)
        # Asserting main result (ignoring any white lines at the end of output)
        stdout = out.getvalue().split("\n")
        stdout.reverse()
        result = next((rsl for rsl in stdout if rsl))
        self.assertEqual(result, "OAI-PMH: 2/2")
        # Asserting Datagrowth usage
        self.assertEqual(send_mock.call_count, 1, "More than 1 call to send, was edurep_delen set not ignored?")
        args, kwargs = send_mock.call_args
        config = kwargs["config"]
        self.assertEqual(config.resource, "edurep.EdurepOAIPMH", "Wrong resource used for OAI-PMH calls")
        self.assertEqual(
            config.continuation_limit, 1000, "Expected very high continuation limit to assert complete sets"
        )
        self.assertEqual(args, ("surf", "1970-01-01"), "Wrong arguments given to edurep.EdurepOAIPMH")
        self.assertEqual(kwargs["method"], "get", "edurep.EdurepOAIPMH is not using HTTP GET method")
        # Last but not least we check that the correct EdurepHarvest objects have indeed progressed
        # to prevent repetitious harvests.
        surf_harvest = EdurepHarvest.objects.get(source__collection_name="surf")
        self.assertGreater(
            surf_harvest.latest_update_at,
            make_aware(datetime(year=1970, month=1, day=1)),
            "surf set harvest should got updated to prevent re-harvest in the future"
        )
        edurep_delen_harvest = EdurepHarvest.objects.get(source__collection_name="edurep_delen")
        self.assertEqual(
            edurep_delen_harvest.latest_update_at, make_aware(datetime(year=1970, month=1, day=1)),
            "edurep_delen set harvest got updated while we expected it to be ignored"
        )

    def test_edurep_invalid_freeze(self):
        # Testing the case where a Freeze does not exist at all
        try:
            call_command("harvest_edurep_seeds", "--freeze=invalid")
            self.fail("harvest_edurep_seeds did not raise for an invalid freeze")
        except EdurepHarvest.DoesNotExist:
            pass
        # Testing the case where a Freeze exists, but no harvest tasks are present
        surf_harvest = EdurepHarvest.objects.get(source__collection_name="surf")
        surf_harvest.stage = HarvestStages.COMPLETE
        surf_harvest.save()
        try:
            call_command("harvest_edurep_seeds", "--freeze=invalid")
            self.fail("harvest_edurep_seeds did not raise for a freeze without pending harvests")
        except EdurepHarvest.DoesNotExist:
            pass
