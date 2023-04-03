import os
import openai
from github import Github, PullRequest

# Set up your API keys
GITHUB_ACCESS_TOKEN = os.environ["GITHUB_ACCESS_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Initialize the GitHub and OpenAI API clients
github = Github(GITHUB_ACCESS_TOKEN)
openai.api_key = OPENAI_API_KEY

def fetch_pull_request(repo_name, pr_number):
    print(repo_name)
    print(pr_number)
    repo = github.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    return pr

def generate_summary(text):
    #prompt = f"Summarize the following code change in 1-4 sentences: {text}"
    print(text)
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "I am helping your team summarize pull requests in 1-4 sentences. What PR can I help you with?"},
            {"role": "user", "content": f'{text}'}
        ],
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.5,
    )
    
    return response.choices[0].message.content.strip()

def main():
    repo_name = input("Enter the repository (in the format 'owner/repo'): ")
    pr_number = int(input("Enter the pull request number: "))

    pr = fetch_pull_request(repo_name, pr_number)
    text = pr.body

    summary = generate_summary(text)
    print("\nGenerated Summary:")
    print(summary)

if __name__ == "__main__":
    main()
