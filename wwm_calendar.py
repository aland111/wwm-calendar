"""Publish upcoming RTL broadcasts of Wer wird Millionär? as an iCalendar feed."""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from icalendar import Calendar, Event


SCHEDULE_URL = "https://www.fernsehserien.de/wer-wird-millionaer/sendetermine/rtl"


@dataclass(frozen=True)
class Broadcast:
    start: datetime
    end: datetime
    title: str
    url: str


def fetch_schedule() -> str:
    request = Request(
        SCHEDULE_URL,
        headers={"User-Agent": "WWM-calendar/1.0 (personal calendar feed)"},
    )
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def event_title(episode_title: str) -> str:
    episode_title = " ".join(episode_title.split())
    if not episode_title or episode_title.startswith("Folge "):
        return "Wer wird Millionär?"
    return f"Wer wird Millionär? – {episode_title}"


def parse_schedule(html: str, now: datetime) -> list[Broadcast]:
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select('div[itemtype="http://schema.org/BroadcastEvent"][itemprop="publication"]')
    if not rows:
        raise ValueError("Keine RTL-Sendetermine gefunden; die Quellseite hat sich möglicherweise geändert.")

    by_slot: dict[tuple[datetime, datetime], Broadcast] = {}
    for row in rows:
        start_tag = row.select_one('time[itemprop="startDate"][datetime]')
        end_tag = row.select_one('time[itemprop="endDate"][datetime]')
        if start_tag is None or end_tag is None:
            continue  # Zusätzliche Episoden desselben Sendeplatzes tragen keine eigenen Zeiten.

        start = datetime.fromisoformat(start_tag["datetime"])
        end = datetime.fromisoformat(end_tag["datetime"])
        if start.tzinfo is None or end.tzinfo is None or end <= start or end <= now:
            continue

        episode = row.select_one(".sendetermine-2019-episodentitel")
        if episode:
            for badge in episode.select("abbr"):
                badge.decompose()
        title = event_title(episode.get_text(" ", strip=True) if episode else "")
        link = row.find_parent("a", href=True)
        url = f"https://www.fernsehserien.de{link['href']}" if link else SCHEDULE_URL
        slot = (start, end)
        candidate = Broadcast(start, end, title, url)
        if slot not in by_slot or (
            by_slot[slot].title == "Wer wird Millionär?" and title != "Wer wird Millionär?"
        ):
            by_slot[slot] = candidate

    return sorted(by_slot.values(), key=lambda item: (item.start, item.end))


def build_calendar(broadcasts: list[Broadcast], generated_at: datetime) -> bytes:
    calendar = Calendar()
    calendar.add("prodid", "-//WWM Calendar//DE")
    calendar.add("version", "2.0")
    calendar.add("calscale", "GREGORIAN")

    daily_count: defaultdict[str, int] = defaultdict(int)
    for broadcast in broadcasts:
        day = broadcast.start.strftime("%Y%m%d")
        daily_count[day] += 1
        event = Event()
        event.add("uid", f"wwm-{day}-{daily_count[day]}@wwm-calendar")
        event.add("dtstamp", generated_at)
        event.add("dtstart", broadcast.start.astimezone(timezone.utc))
        event.add("dtend", broadcast.end.astimezone(timezone.utc))
        event.add("summary", broadcast.title)
        event.add("location", "RTL")
        event.add("description", f"Ausstrahlung auf RTL. Sendetermin: {broadcast.url}")
        event.add("url", broadcast.url)
        calendar.add_component(event)

    return calendar.to_ical()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("site/wwm.ics"))
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    broadcasts = parse_schedule(fetch_schedule(), now)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(build_calendar(broadcasts, now))
    (args.output.parent / "index.html").write_text(
        '<!doctype html><html lang="de"><meta charset="utf-8">'
        '<title>Wer wird Millionär? – Kalender</title>'
        '<h1>Wer wird Millionär? – Kalender</h1>'
        '<p><a href="wwm.ics">Kalender abonnieren (.ics)</a></p></html>',
        encoding="utf-8",
    )
    print(f"{len(broadcasts)} kommende RTL-Ausstrahlungen nach {args.output} geschrieben")
    for broadcast in broadcasts:
        print(f"{broadcast.start:%d.%m.%Y %H:%M}–{broadcast.end:%H:%M} {broadcast.title}")


if __name__ == "__main__":
    main()
