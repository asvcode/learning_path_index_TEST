from csv import DictWriter
from pathlib import Path
from urllib.parse import urljoin
from lxml import etree
import argparse
import os
import requests

# Import CONFIG from a separate file
from config import CONFIG
from scrapers.google_cloud_skill_boost import pages

COURSE_CODE = "CLMML11"
GCSB_JOURNEY_URL = "https://www.cloudskillsboost.google/journeys/17"
GCSB_HOME_URL = "https://www.cloudskillsboost.google/"
GCSB_LOGIN_URL = "https://www.cloudskillsboost.google/users/sign_in"

DATA_FOLDER = Path(CONFIG.DATA_PATH, COURSE_CODE)
DATA_FOLDER.mkdir(exist_ok=True, parents=True)

# Open Journey Path


def extract_ml_learning_path(GCSB_JOURNEY_URL) -> list[dict]:
    r = requests.get(GCSB_JOURNEY_URL)
    html_parser = etree.HTMLParser()
    dom = etree.fromstring(r.content, html_parser)

    data = []
    for journey in dom.xpath(pages.GCSBLearningJourneyPage.journeys):
        try:
            details = journey.xpath(
                pages.GCSBLearningJourneyPage.journey_details)[0]
        except IndexError:
            details = journey.xpath(
                pages.GCSBLearningJourneyPage.journey_details)
            details = details if details else "No details available"

        try:
            link = urljoin(GCSB_HOME_URL, journey.xpath(
                pages.GCSBLearningJourneyPage.journey_link)[0])
        except IndexError:
            link = urljoin(GCSB_HOME_URL, journey.xpath(
                pages.GCSBLearningJourneyPage.journey_link))
            link = link if link else "No link available"

        data.append({
            "title": journey.xpath(pages.GCSBLearningJourneyPage.journey_title)[0] if journey.xpath(pages.GCSBLearningJourneyPage.journey_title) else "No title available",
            "details": details,
            "description": journey.xpath(pages.GCSBLearningJourneyPage.journey_description)[0] if journey.xpath(pages.GCSBLearningJourneyPage.journey_description) else "No description available",
            "link": link,
        })

    return data


if __name__ == "__main__":
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Extract ML learning path')
    parser.add_argument('--url', help='GCSB Journey URL')
    args = parser.parse_args()

    # Check for URL from command line arguments, environment variable, or CONFIG
    GCSB_JOURNEY_URL = args.url or os.getenv(
        'GCSB_JOURNEY_URL') or getattr(CONFIG, 'GCSB_JOURNEY_URL', None)

    if not GCSB_JOURNEY_URL:
        # Fallback to user input if URL is not found
        GCSB_JOURNEY_URL = input("Please enter the GCSB Journey URL: ")

    # Extract learning path data
    data = extract_ml_learning_path(GCSB_JOURNEY_URL)

    # Check if data is not empty
    if not data:
        print("No data to write!")
    else:
        try:
            # Writing to the CSV file
            csv_file = DATA_FOLDER.joinpath(f"{COURSE_CODE}-Courses.csv")
            with open(csv_file, "w", encoding="utf-8", newline='') as f:
                csvwriter = DictWriter(
                    f, fieldnames=["title", "details", "description", "link"])
                csvwriter.writeheader()
                csvwriter.writerows(data)
            print(f"Data successfully written to {csv_file}")
        except IOError as e:
            print(f"An I/O error occurred while writing the file: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while writing the file: {e}")
