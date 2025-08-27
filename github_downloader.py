import os
import sys
import argparse
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
import logging

# Load .env file if it exists
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Extract owner and repo name from GitHub repo URL.


def get_repo_details(repo_url):
    try:
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub repository URL.")
        return path_parts[0], path_parts[1].replace(".git", "")
    except Exception as e:
        raise ValueError(f"Failed to parse repository URL: {e}")


# Continuously fetch contents of a GitHub repository directory
def fetch_directory_contents(owner, repo, branch, directory, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{directory}?ref={branch}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 404:
        raise FileNotFoundError("Directory or branch not found in repository.")
    if response.status_code == 401 or response.status_code == 403:
        raise PermissionError(
            "Authentication failed. Check your token permissions.")

    response.raise_for_status()
    return response.json()


# Download file from GitHub and save locally
def download_file(file_url, local_path, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(file_url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to download file: {file_url}")

    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    with open(local_path, "wb") as f:
        f.write(response.content)

    logging.info(f"Downloaded: {local_path}")


# Recursively process directory and download .md files
def process_directory(owner, repo, branch, directory, local_base, token):
    items = fetch_directory_contents(owner, repo, branch, directory, token)
    for item in items:
        if item["type"] == "dir":
            process_directory(owner, repo, branch,
                              item["path"], local_base, token)
        elif item["type"] == "file" and item["name"].endswith(".md"):
            local_path = os.path.join(local_base, item["path"])
            download_file(item["download_url"], local_path, token)


def main():
    parser = argparse.ArgumentParser(
        description="Download Markdown files from private GitHub repository."
    )
    parser.add_argument(
        "repo_url", help="Full URL of the private GitHub repository")
    parser.add_argument("branch", help="Branch name")
    parser.add_argument(
        "repo_directory", help="Directory path inside repo to fetch .md files")
    parser.add_argument("local_directory",
                        help="Local directory to save files")
    parser.add_argument(
        "--token", help="GitHub Personal Access Token (or set GITHUB_TOKEN env var)")

    args = parser.parse_args()

    token = args.token or os.getenv("GITHUB_TOKEN")
    if not token:
        logging.error(
            "GitHub token must be provided either via --token or GITHUB_TOKEN environment variable.")
        sys.exit(1)

    try:
        owner, repo = get_repo_details(args.repo_url)
        process_directory(owner, repo, args.branch,
                          args.repo_directory, args.local_directory, token)
        logging.info("Download completed successfully.")
    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
