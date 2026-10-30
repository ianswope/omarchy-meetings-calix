import importlib.machinery
import importlib.util
import os
import unittest
from datetime import date, datetime
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
os.environ["MEETINGS_CONFIG"] = str(ROOT / "tests" / "missing-config.json")
os.environ.pop("MEETINGS_PROVIDER", None)

loader = importlib.machinery.SourceFileLoader(
    "meetings_widget_calix", str(ROOT / "bin" / "meetings-widget"))
spec = importlib.util.spec_from_loader(loader.name, loader)
widget = importlib.util.module_from_spec(spec)
loader.exec_module(widget)


class CalixProviderTests(unittest.TestCase):
    def test_no_provider_means_calix(self):
        self.assertEqual(widget.provider_name(""), "calix")
        self.assertEqual(widget.provider_name("google"), "google")
        self.assertEqual(widget.provider_name("outlook"), "microsoft")
        self.assertEqual(widget.PROVIDER, "calix")

    def test_agenda_rows_pass_through(self):
        rows = [{
            "id": "4-1780000000",
            "title": "Standup",
            "start_date": "2026-10-26",
            "start_time": "09:00",
            "end_date": "2026-10-26",
            "end_time": "09:30",
            "calendar": "Work",
            "conference_uri": "https://meet.example/abc",
            "attendees": [{"name": "Sam", "email": "sam@example.com", "status": "accepted"}],
        }]
        with mock.patch.object(widget, "calix_json", return_value=rows):
            self.assertEqual(
                widget.parse_calix_rows(date(2026, 10, 26), date(2026, 10, 26)),
                rows,
            )

    def test_error_object_is_not_an_agenda(self):
        with mock.patch.object(widget, "calix_json", return_value={"error": "not-set-up"}):
            self.assertIsNone(
                widget.parse_calix_rows(date(2026, 10, 26), date(2026, 10, 26)))

    def test_a_row_keeps_its_join_link_and_the_day(self):
        rows = [{
            "id": "4-1780000000",
            "title": "Standup",
            "start_date": "2026-10-26",
            "start_time": "09:00",
            "end_date": "2026-10-26",
            "end_time": "09:30",
            "calendar": "Work",
            "conference_uri": "https://meet.example/abc",
            "attendees": [{"name": "Sam", "email": "sam@example.com", "status": "accepted"}],
        }]
        day = widget.build_day(rows, date(2026, 10, 26))
        self.assertEqual(day["date_iso"], "2026-10-26")
        self.assertEqual(day["events"][0]["hangout"], "https://meet.example/abc")
        self.assertTrue(day["events"][0]["attendees_embedded"])
        self.assertEqual(day["events"][0]["attendees"][0]["name"], "Sam")

    def test_missing_binary_is_its_own_reason(self):
        with mock.patch.object(widget, "PROVIDER", "calix"), \
             mock.patch.object(widget, "calix_binary", return_value=None):
            self.assertEqual(widget.failure_error(), "calix-missing")

    def test_empty_calendar_list_means_nothing_is_connected(self):
        with mock.patch.object(widget, "PROVIDER", "calix"), \
             mock.patch.object(widget, "calix_binary", return_value="/usr/bin/calix"), \
             mock.patch.object(widget, "calix_json", return_value=[]):
            self.assertEqual(widget.failure_error(), "not-connected")

    def test_attendees_are_looked_up_from_the_id(self):
        when = datetime(2026, 10, 26, 9, 0)
        event_id = "4-%d" % int(when.timestamp())
        rows = [{
            "id": event_id,
            "attendees": [{"name": "Sam", "email": "", "status": "accepted"}],
        }]
        with mock.patch.object(widget, "parse_calix_rows", return_value=rows):
            people = widget.calix_attendees(event_id)
        self.assertEqual(people[0]["name"], "Sam")


if __name__ == "__main__":
    unittest.main()
