import requests
import json
from datetime import datetime, timedelta

# GitHub repository to query
REPO = "octocat/Hello-World"  # Replace with the repository you want to query

# GitHub token from environment
GITHUB_TOKEN = "GITHUB_TOKEN"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# Output file for filtered releases
OUTPUT_FILE = "filtered_releases.json"

def get_previous_month_range():
    """Get the start and end timestamps for the previous month."""
    today = datetime.today()
    first_day_this_month = today.replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    first_day_last_month = last_day_last_month.replace(day=1)
    return first_day_last_month, last_day_last_month

def fetch_github_releases(repo):
    """Fetch all releases for a given GitHub repository."""
    url = f"https://api.github.com/repos/github-finder/releases"
    releases = []
    page = 1

    while True:
        response = requests.get(url, headers=HEADERS, params={"page": page, "per_page": 100})
        if response.status_code != 200:
            print(f"Error fetching releases: {response.status_code}, {response.json()}")
            break

        data = response.json()
        if not data:
            break

        releases.extend(data)
        page += 1

    return releases

def filter_releases_by_date(releases, start_date, end_date):
    """Filter releases based on their published date."""
    filtered = []
    for release in releases:
        published_at = release.get("published_at")
        if not published_at:
            continue

        # Convert to datetime object
        published_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))

        # Filter by range
        if start_date <= published_date <= end_date:
            filtered.append({
                "name": release.get("name"),
                "tag_name": release.get("tag_name"),
                "published_at": published_at,
                "html_url": release.get("html_url")
            })
    return filtered

def write_to_file(data, file_name):
    """Write filtered releases to a JSON file."""
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
