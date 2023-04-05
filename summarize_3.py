import os
import openai
from github import Github, PullRequest, Commit, File
from dotenv import load_dotenv
import requests


load_dotenv()
# Set up your API keys
GITHUB_ACCESS_TOKEN = os.environ["GITHUB_ACCESS_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

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
            {"role": "user",
             "content": f'Here is my cobol file: \n{text}'}
        ],
        max_tokens=1200,
        n=1,
        stop=None,
        temperature=0.5,
    )

    return response.choices[0].message.content.strip()


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
    summary = summary.split(". ")
    print(f"\nGenerated Summary:\n\t")
    for sentence in summary:
        print(f'- {sentence}')


if __name__ == "__main__":
    main()
