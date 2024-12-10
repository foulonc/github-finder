import requests
import os
import json
from datetime import datetime, timedelta

# Use the GitHub token from the environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise EnvironmentError("GITHUB_TOKEN not found in environment variables!")

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# Dynamically fetch the current repository
REPO = os.getenv("GITHUB_REPOSITORY", "octocat/Hello-World")  # Default repo for testing

OUTPUT_FILE = "filtered_releases.json"

def get_previous_month_range():
    today = datetime.today()
    first_day_this_month = today.replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    first_day_last_month = last_day_last_month.replace(day=1)
    return first_day_last_month, last_day_last_month

def fetch_github_releases(repo):
    url = f"https://api.github.com/repos/{repo}/releases"
    releases = []
    page = 1

    while True:
        response = requests.get(url, headers=HEADERS, params={"page": page, "per_page": 100})
        if response.status_code == 401:
            raise PermissionError("Bad credentials. Check your GITHUB_TOKEN.")
        elif response.status_code != 200:
            print(f"Error fetching releases: {response.status_code}, {response.json()}")
            break

        data = response.json()
        if not data:
            break

        releases.extend(data)
        page += 1

    return releases

def filter_releases_by_date(releases, start_date, end_date):
    filtered = []
    for release in releases:
        published_at = release.get("published_at")
        if not published_at:
            continue

        published_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        if start_date <= published_date <= end_date:
            filtered.append({
                "name": release.get("name"),
                "tag_name": release.get("tag_name"),
                "published_at": published_at,
                "html_url": release.get("html_url")
            })
    return filtered

def write_to_file(data, file_name):
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Filtered releases saved to {file_name}")

def main():
    start_date, end_date = get_previous_month_range()
    print(f"Fetching releases for the previous month: {start_date.date()} to {end_date.date()}")

    releases = fetch_github_releases(REPO)
    if not releases:
        print("No releases found.")
        return

    filtered_releases = filter_releases_by_date(releases, start_date, end_date)
    write_to_file(filtered_releases, OUTPUT_FILE)

if __name__ == "__main__":
    main()
