import unittest
from datetime import datetime, timezone

from icalendar import Calendar

from wwm_calendar import build_calendar, parse_schedule


SCHEDULE = """
<div itemprop="publication" itemtype="http://schema.org/BroadcastEvent">
  <time itemprop="startDate" datetime="2026-10-05T20:15:00+02:00"></time>
  <time itemprop="endDate" datetime="2026-10-06T00:00:00+02:00"></time>
  <span class="sendetermine-2019-episodentitel">Die 3-Millionen-Euro-Woche (42) <abbr>NEU</abbr></span>
</div>
<div itemprop="publication" itemtype="http://schema.org/BroadcastEvent">
  <time itemprop="startDate" datetime="2026-10-05T20:15:00+02:00"></time>
  <time itemprop="endDate" datetime="2026-10-06T00:00:00+02:00"></time>
  <span class="sendetermine-2019-episodentitel">Folge 1777</span>
</div>
<div itemprop="publication" itemtype="http://schema.org/BroadcastEvent">
  <time itemprop="startDate" datetime="2026-10-06T20:15:00+02:00"></time>
  <time itemprop="endDate" datetime="2026-10-07T00:00:00+02:00"></time>
  <span class="sendetermine-2019-episodentitel">Die 3-Millionen-Euro-Woche (43)</span>
</div>
"""


class CalendarTests(unittest.TestCase):
    def test_specials_midnight_and_duplicate_episodes(self):
        now = datetime(2026, 9, 26, tzinfo=timezone.utc)
        broadcasts = parse_schedule(SCHEDULE, now)
        self.assertEqual(len(broadcasts), 2)
        self.assertEqual(broadcasts[0].title, "Wer wird Millionär? – Die 3-Millionen-Euro-Woche (42)")
        self.assertEqual(broadcasts[0].end.day, 6)

        calendar = Calendar.from_ical(build_calendar(broadcasts, now))
        events = calendar.walk("VEVENT")
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].decoded("DTSTART"), broadcasts[0].start.astimezone(timezone.utc))
        self.assertEqual(events[0].decoded("DTEND"), broadcasts[0].end.astimezone(timezone.utc))
        self.assertEqual(str(events[0]["UID"]), "wwm-20261005-1@wwm-calendar")

    def test_fails_if_source_layout_disappears(self):
        with self.assertRaises(ValueError):
            parse_schedule("<html></html>", datetime.now(timezone.utc))


if __name__ == "__main__":
    unittest.main()
