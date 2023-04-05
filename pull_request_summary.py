import asyncio
import json
import os
import openai
from github import Github, PullRequest, Commit, File
from dotenv import load_dotenv
import requests

load_dotenv()
# Set up your API keys
GITHUB_ACCESS_TOKEN = os.environ["GITHUB_ACCESS_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
CONFLUENCE_ACCESS_TOKEN = os.environ["CONFLUENCE_ACCESS_TOKEN"]

# Initialize the GitHub and OpenAI API clients
github = Github(GITHUB_ACCESS_TOKEN)
openai.api_key = OPENAI_API_KEY


def fetch_pull_request_commit(repo_name, pr_number):
    # print(f'repo_name: {repo_name}')
    # print(f'pr_number: {pr_number}')
    repo = github.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    commits = pr.get_commits()
    commit = commits[0]
    return commit


def generate_summary(text):
    # prompt = f"Summarize the following code change in 1-4 sentences: {text}"
    # print(f'text: {text}')

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "I am helping your team summarize cobol code in 1-4 sentences. What file can I help you with?"},
            {"role": "user", "content": f'Here is my cobol file: \n{text}'}
        ],
        max_tokens=1100,
        n=1,
        stop=None,
        temperature=0.5,
    )

    return response.choices[0].message.content.strip()


async def post_to_confluence(summary):
    response = requests.post(
        url="https://slalom.atlassian.net//wiki/api/v2/pages",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Basic {CONFLUENCE_ACCESS_TOKEN}"
        },
        data=summary
    )
    print(response.content)
    return response.status_code


def main():
    repo_name = "jmrosh/h1-connect-ideas"  # input("Enter the repository (in the format 'owner/repo'): ")
    pr_number = 1  # int(input("Enter the pull request number: "))
    cobol_file = "https://raw.githubusercontent.com/cicsdev/cics-genapp/main/base/src/lgacdb01.cbl"

    commit = fetch_pull_request_commit(repo_name, pr_number)
    # print(f'commit.files[0]: {commit.files[0]}')
    raw_url = commit.files[0].raw_url
    print(f'raw_url: {cobol_file}')
    f = requests.get(cobol_file)
    # print(f'raw_url_contents: {f.text}')
    #
    summary = generate_summary(f.text)
    summary_split = summary.split(". ")
    print(f"\nGenerated Summary:\n\t")
    for sentence in summary_split:
        print(f'- {sentence}')

    print(summary)

    my_dict = { "spaceId": 3189311943, "status": "current", "title": "WI PYTHON", "parentId": 3195142195, "body": {"representation": "wiki", "value": summary}}
    data = json.dumps(my_dict)
    asyncio.run(post_to_confluence(data))


if __name__ == "__main__":
    main()
