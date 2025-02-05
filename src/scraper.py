import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import pytz

from keywords import TEAMS, LEAGUES, CUPS, TIMEZONE, FIXTURE_URLS

def scrape_matches():
    """
    Scrapes ESPN for upcoming fixtures and returns a list of match dictionaries.
    Each match dict has:
      {
        'team_home': str,
        'team_away': str,
        'competition': str,
        'streaming': str,
        'datetime_utc': datetime (UTC-based)
      }
    """
    # Use fixture URLs from keywords.py; if empty, default to ESPN's central fixtures page.
    urls = FIXTURE_URLS if FIXTURE_URLS else ["https://www.espn.com/soccer/fixtures"]
    all_matches = []

    # Define a headers dictionary to simulate a browser.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/92.0.4515.159 Safari/537.36"
    }

    for url in urls:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # ESPN groups fixtures by date in containers (e.g., <section class="Card ...">).
        date_containers = soup.find_all("section", class_=re.compile(r"Card(\s|$)"))
        if not date_containers:
            # Fallback: try using <div> elements.
            date_containers = soup.find_all("div", class_=re.compile(r"Card(\s|$)"))

        for date_block in date_containers:
            # Look for a header that contains the date (e.g., <h2> or <h3>).
            date_header = date_block.find(["h2", "h3"])
            if not date_header:
                continue

            date_str = date_header.get_text(strip=True)
            match_date = parse_date_from_espn_header(date_str)
            if not match_date:
                continue

            # Find fixture rows; selectors may vary depending on ESPN's HTML.
            match_rows = date_block.find_all("tr", class_=re.compile(r"Table__TR"))
            if not match_rows:
                match_rows = date_block.find_all("div", class_=re.compile(r"matchRow"))

            for row in match_rows:
                cells = row.find_all("td")
                if len(cells) < 4:
                    # Not enough data to parse
                    continue

                time_cell = cells[0].get_text(strip=True)      # e.g., "10:00 AM"
                teams_cell = cells[1].get_text(strip=True)     # e.g., "Liverpool vs. Chelsea"
                comp_cell = cells[2].get_text(strip=True)      # e.g., "English Premier League"
                tv_cell = cells[3].get_text(strip=True)        # e.g., "ESPN+"

                # Use TIMEZONE from keywords.py when converting the match time.
                match_datetime_utc = combine_date_time_to_utc(match_date, time_cell, local_tz_name=TIMEZONE)
                if not match_datetime_utc:
                    continue

                team_home, team_away = parse_teams(teams_cell)

                match_info = {
                    "team_home": team_home,
                    "team_away": team_away,
                    "competition": comp_cell,
                    "streaming": tv_cell,
                    "datetime_utc": match_datetime_utc,
                }

                if is_match_of_interest(match_info):
                    all_matches.append(match_info)

    return all_matches

def parse_date_from_espn_header(date_str):
    """
    Attempt to parse a date from a header like "Monday, January 1".
    Returns a datetime.date object or None if parsing fails.
    """
    current_year = datetime.now().year
    parts = date_str.split(",", 1)
    if len(parts) < 2:
        return None
    date_part = parts[1].strip()  # e.g., "January 1"
    try:
        partial = datetime.strptime(date_part, "%B %d")
        potential_date = partial.replace(year=current_year).date()
        return potential_date
    except ValueError:
        return None

def combine_date_time_to_utc(date_obj, time_str, local_tz_name="US/Eastern"):
    """
    Combine a date object with a time string (e.g., "10:00 AM") into a UTC datetime.
    The local_tz_name parameter is now set via keywords.py.
    """
    try:
        time_format = "%I:%M %p"  # e.g., "10:00 AM"
        time_obj = datetime.strptime(time_str, time_format).time()
    except ValueError:
        return None

    local_tz = pytz.timezone(local_tz_name)
    combined_local = datetime(
        year=date_obj.year,
        month=date_obj.month,
        day=date_obj.day,
        hour=time_obj.hour,
        minute=time_obj.minute
    )
    # Localize the naive datetime
    local_dt = local_tz.localize(combined_local)
    # Convert to UTC
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt

def parse_teams(teams_cell_text):
    """
    Splits a string like "Liverpool vs. Chelsea" into ("Liverpool", "Chelsea").
    Adjust the logic if ESPN uses different separators.
    """
    if "vs." in teams_cell_text:
        parts = teams_cell_text.split("vs.")
    elif "v " in teams_cell_text:
        parts = teams_cell_text.split("v ")
    else:
        parts = [teams_cell_text, ""]
    team_home = parts[0].strip()
    team_away = parts[1].strip() if len(parts) > 1 else ""
    return (team_home, team_away)

def is_match_of_interest(match_info):
    """
    Returns True if the match is of interest based on keywords in TEAMS, LEAGUES, or CUPS.
    """
    home_lower = match_info['team_home'].lower()
    away_lower = match_info['team_away'].lower()
    comp_lower = match_info['competition'].lower()

    team_filter = any(t.lower() in home_lower or t.lower() in away_lower for t in TEAMS) if TEAMS else False
    league_filter = any(l.lower() in comp_lower for l in LEAGUES) if LEAGUES else False
    cup_filter = any(c.lower() in comp_lower for c in CUPS) if CUPS else False

    if TEAMS and not team_filter:
        return False
    if not TEAMS and not LEAGUES and not CUPS:
        return True
    return team_filter or league_filter or cup_filter