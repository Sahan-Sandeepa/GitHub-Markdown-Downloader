# GitHub Markdown Downloader

This is a Python command-line tool to download `.md` files from a **private GitHub repository**.

## Features

- Secure authentication using GitHub Personal Access Token (PAT).
- Works with private repositories.
- Recursively downloads `.md` files from a given repo directory.
- Preserves directory structure locally.
- Robust error handling.

---

## Installation

```bash
git clone <this-repo>
cd github_downloader
pip install -r requirements.txt
```
## Run the script

```bash
python github_downloader.py <repo_url> <branch> <repo_directory> <local_directory>
```
Example
```bash
python github_downloader.py https://github.com/username/private-repo main docs ./downloaded_docs
```
