from csv import DictWriter
from pathlib import Path
from urllib.parse import urljoin
from lxml import etree
import requests

# Import CONFIG from the separate file
from config import CONFIG

COURSE_CODE = "CLMML11"
GCSB_HOME_URL = "https://www.cloudskillsboost.google/"

# Create data folder
DATA_FOLDER = Path(CONFIG.DATA_PATH, COURSE_CODE)
DATA_FOLDER.mkdir(exist_ok=True, parents=True)

# Extract learning path data


def extract_ml_learning_path(url) -> list[dict]:
    r = requests.get(url)
    dom = etree.HTML(r.content)
    data = []

    # Simplified XPath logic (replace with your actual XPaths)
    journeys = dom.xpath("//your-xpath-here")
    for journey in journeys:
        title = journey.xpath(
            ".//title-xpath")[0] if journey.xpath(".//title-xpath") else "No title"
        details = journey.xpath(
            ".//details-xpath")[0] if journey.xpath(".//details-xpath") else "No details"
        description = journey.xpath(
            ".//description-xpath")[0] if journey.xpath(".//description-xpath") else "No description"
        link = urljoin(GCSB_HOME_URL, journey.xpath(".//link-xpath")
                       [0] if journey.xpath(".//link-xpath") else "No link")

        data.append({
            "title": title,
            "details": details,
            "description": description,
            "link": link
        })

    return data

# Main function with minimal logic


def main(url=None):
    url = url or CONFIG.GCSB_JOURNEY_URL  # Use provided URL or default from CONFIG
    data = extract_ml_learning_path(url)

    if data:
        csv_file = DATA_FOLDER / f"{COURSE_CODE}-Courses.csv"
        with open(csv_file, "w", encoding="utf-8", newline='') as f:
            writer = DictWriter(
                f, fieldnames=["title", "details", "description", "link"])
            writer.writeheader()
            writer.writerows(data)
        print(f"Data written to {csv_file}")
    else:
        print("No data found")


# If run directly
if __name__ == "__main__":
    main()  # Uses default CONFIG.GCSB_JOURNEY_URL or pass a custom URL
