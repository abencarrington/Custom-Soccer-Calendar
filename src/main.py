from scraper import scrape_matches
from ics_utils import create_ics_file

def main():
    # 1. Scrape matches from ESPN
    matches = scrape_matches()

    if not matches:
        print("No matches found.")
        return

    # 2. Generate an ICS file with the scraped matches.
    create_ics_file(matches, output_path="football_calendar.ics")

    print("Done. You can now import 'football_calendar.ics' as a new custom calendar.")

if __name__ == "__main__":
    main()