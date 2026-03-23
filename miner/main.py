import os
import requests
import re
import redis
import time

GITHUB_API = "https://api.github.com"

HEADERS = {
    "Accept": "application/vnd.github+json"
}

HEADERS["Authorization"] = f"token {''}"

r = redis.Redis(host="redis", port=6379, decode_responses=True)

def get_repositories(language, page):
    url = f"{GITHUB_API}/search/repositories?q=language:{language}&sort=stars&per_page=10&page={page}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json().get("items", [])

def get_python_functions(code):
    return re.findall(r'^\s*def\s+(\w+)\s*\(', code, re.MULTILINE)

def get_java_methods(code):
    return re.findall(r'(?:public|private|protected)?\s*(?:static\s+)?\s*\w+\s+(\w+)\s*\(', code)

def split_words(name):
    # Snake case
    words = name.split("_")
    # Camel case
    final_words = []
    for word in words:
        split = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', word)
        final_words.extend(split)
    return [w.lower() for w in final_words if w]

def process_repo(repo, language):
    contents_url = repo["contents_url"].replace("{+path}", "")
    response = requests.get(contents_url, headers=HEADERS)

    for file in response.json():
        if file["type"] != "file":
            continue
        # Check .py and .java extensions
        if language == "Python" and file["name"].endswith(".py"):
            process_file(file["download_url"], get_python_functions)
        elif language == "Java" and file["name"].endswith(".java"):
            process_file(file["download_url"], get_java_methods)

def process_file(url, get_names):
    code = requests.get(url).text
    names = get_names(code)

    words = []
    for name in names:
        words.extend(split_words(name))
    if words:
        send_words(words)

def send_words(words):
        for word in words:
            r.rpush("word_queue", word)

def main():
    page = 1 # Initial page
    while True:
        for lang in ["Python", "Java"]:
            repos = get_repositories(lang, page)

            for repo in repos:
                process_repo(repo, lang)

            page += 1

        time.sleep(2)  # Sleep to not trigger secondary rate limit


if __name__ == "__main__":
    main()
