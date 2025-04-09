import requests
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import tzlocal
import os
import json

load_dotenv()
# === CONFIGURATION ===
LOCAL_TIMEZONE = ZoneInfo("Asia/Kolkata")
GITHUB_ORG = "AdvayaHackathon"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
API_BASE = "https://api.github.com"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


def get_org_repos(org_name):
    repos = []
    page = 1
    while True:
        url = f"{API_BASE}/orgs/{org_name}/repos?per_page=100&page={page}"
        # print(url)
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print("Error fetching repos:", response.text)
            break
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos


def get_repo_all_branchs(repo_name):
    url_repo = f"{API_BASE}/repos/{repo_name}/branches"
    try:
        repo_info = requests.get(url_repo, headers=HEADERS).json()
        if repo_info:
            return repo_info
        return None
    except Exception as e:
        return None


def get_first_commit(repo_full_name, branch="main"):
    commits = []
    page = 1

    while True:
        url = f"{API_BASE}/repos/{repo_full_name}/commits?sha={branch}&per_page=100&page={page}"
        res = requests.get(url, headers=HEADERS)

        if res.status_code != 200:
            print(f"Error: {res.status_code} - {res.text}")
            break

        page_commits = res.json()

        if not page_commits:
            break

        commits.extend(page_commits)
        page += 1

    if not commits:
        return []

    count = 3
    sorted_commits = sorted(commits, key=lambda c: c["commit"]["author"]["date"])
    first_n = sorted_commits[:count]
    return [
        {
            "author": c["commit"]["author"]["name"],
            "email": c["commit"]["author"]["email"],
            "date": c["commit"]["author"]["date"],
            "message": c["commit"]["message"],
            "url": c["html_url"],
        }
        for c in first_n
    ]


def main():
    repos = get_org_repos(GITHUB_ORG)
    print(f"\nFound {len(repos)} repositories in organization '{GITHUB_ORG}'.\n")
    caught = []
    for repo in repos:
        repo_name = repo["full_name"]
        branchs = get_repo_all_branchs(repo_name)
        got_caught = False
        if branchs:
            for branch in branchs:
                branch_name = branch["name"]
                commits = get_first_commit(repo_name, branch_name)
                for commit in commits:
                    if commit["email"] == "advaya@bgscet.ac.in":
                        continue
                    if is_not_april_11_or_12_local(commit["date"]):
                        caught.append({"repo": repo_name, "commit": commit})
                        got_caught = True
                        break
        if got_caught == False:
            print(f"Repository: {repo_name} ✅")
        else:
            print(f"Repository: {repo_name} Caught ❌")
    print()
    if len(caught) == 0:
        print("Everyone is Good")
    else:
        for cau in caught:
            print(cau)


def get_local_datetime(date_str):
    # Parse GitHub's UTC time and convert to local time
    utc_time = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc
    )
    return utc_time.astimezone(tzlocal.get_localzone())


def is_not_april_11_or_12_local(date_str):
    local_time = get_local_datetime(date_str)
    return not (local_time.month == 4 and local_time.day in [11, 12])


if __name__ == "__main__":
    main()
