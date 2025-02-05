# List of teams you want to track (exact or partial matches).
TEAMS = [
    "Liverpool",
    "Everton",
    "AC Milan",
    "Hibernian",
    "Barcelona",
    "Celtic",
    "Bayer Leverkusen",
    "Heart of Midlothian",
    "Bayern Munich",
    "Inter Miami CF",
    "Wrexham"
]

# List of leagues you want to track.
LEAGUES = [
    "English Premier League",
    "German Bundesliga"
]

# List of cups or tournaments you want to track.
CUPS = [
    "English FA Cup",
    "UEFA Champions League",
    "English Carabao Cup"
]

# Desired timezone for your calendar events.
# Must match a TZ identifier recognized by your environment (e.g., 'Europe/London', 'America/New_York')
TIMEZONE = "America/New_York"

# List of ESPN fixture URLs to scrape.
# Add as many URLs as you need. For example, you might add league-specific pages.
# If this list is empty, the scraper will default to the central fixtures page.
FIXTURE_URLS = [
    "https://www.espn.com/soccer/fixtures"  # central fixtures page
]