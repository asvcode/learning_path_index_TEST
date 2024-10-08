from csv import DictWriter
from pathlib import Path
from urllib.parse import urljoin, urlparse
from lxml import etree
import requests
from scrapers.google_cloud_skill_boost import pages
from config import CONFIG

COURSE_CODE = "CLMML11"
GCSB_HOME_URL = "https://www.cloudskillsboost.google/"
GCSB_LOGIN_URL = "https://www.cloudskillsboost.google/users/sign_in"

DATA_FOLDER = Path(CONFIG.DATA_PATH, COURSE_CODE)
DATA_FOLDER.mkdir(exist_ok=True, parents=True)


def extract_ml_learning_path(GCSB_JOURNEY_URL) -> list[dict]:
    # Send a request to the provided URL
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

        data.append(
            {
                "title": journey.xpath(pages.GCSBLearningJourneyPage.journey_title)[0]
                if journey.xpath(pages.GCSBLearningJourneyPage.journey_title)
                else "No title available",
                "details": details,
                "description": journey.xpath(pages.GCSBLearningJourneyPage.journey_description)[0]
                if journey.xpath(pages.GCSBLearningJourneyPage.journey_description)
                else "No description available",
                "link": link,
            }
        )

    return data


def validate_url(url: str) -> str:
    """Check if the URL has a scheme (http/https) and add https if missing."""
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = "https://" + url  # Prepend https if the scheme is missing
    return url


def main(url=None):
    # Ask the user for the GCSB_JOURNEY_URL input or use the provided URL
    if url:
        GCSB_JOURNEY_URL = validate_url(url)
    else:
        GCSB_JOURNEY_URL = validate_url(
            input("Please enter the GCSB Journey URL: "))

    data = extract_ml_learning_path(GCSB_JOURNEY_URL)

    if not data:
        print("No data to write!")
    else:
        try:
            with open(DATA_FOLDER.joinpath(f"{COURSE_CODE}-Courses.csv"), "w", encoding="utf-8", newline='') as f:
                csvwriter = DictWriter(
                    f, fieldnames=["title", "details", "description", "link"])
                csvwriter.writeheader()
                csvwriter.writerows(data)
            print(f"Data successfully written to {COURSE_CODE}-Courses.csv")
        except Exception as e:
            print(f"An error occurred while writing the file: {e}")


# If running as a standalone script
if __name__ == "__main__":
    main()
