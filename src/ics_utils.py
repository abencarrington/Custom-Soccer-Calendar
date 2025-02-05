from ics import Calendar, Event
from datetime import timedelta
import pytz

from keywords import TIMEZONE

def create_ics_file(matches, output_path="football_calendar.ics"):
    """
    Generates an ICS file from the list of matches, adjusting to the user's TIMEZONE.
    """
    calendar = Calendar()
    user_tz = pytz.timezone(TIMEZONE)

    for match in matches:
        start_utc = match["datetime_utc"]
        start_local = start_utc.astimezone(user_tz)
        end_local = start_local + timedelta(hours=2)  # approximate match duration

        event = Event()
        event.name = f"{match['team_home']} vs {match['team_away']} ({match['competition']})"
        event.begin = start_local
        event.end = end_local
        event.description = f"Streaming on: {match['streaming'] or 'Unknown'}"

        calendar.events.add(event)

    # Write out the .ics file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(str(calendar))

    print(f"ICS file created: {output_path}. You can now import this into Google Calendar.")