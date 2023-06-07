import requests
import json
import concurrent.futures
import threading


pr_count = 0
pr_count_lock = threading.Lock()

def close_pull_request(pr):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Get pull request repository information 
    repo = requests.get(pr["repository_url"], headers=headers).json()
    repo_full_name, pr_number, pr_name = repo["full_name"], pr["number"], pr["name"]

    # Change pull request state to closed
    close_pr_url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}"
    body = json.dumps({"state": "closed"})
    response = requests.patch(close_pr_url,body, headers=headers)

    if response.status_code == 200:
        print(f"Pull request: {pr_name} closed successfully.")
        # Stop race condition when adding successful count
        with pr_count_lock:
            pr_count += 1
    else:
        print(f"Failed to close pull request {pr_name}.")

def close_all_pull_requests(username, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Get all open pull requests created by the user
    url = f"https://api.github.com/search/issues?q=is:open+is:pr+author:{username}"
    response = requests.get(url, headers=headers)
    prs = response.json().get("items")

    # Close pull requests concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(close_pull_request, prs)

    # Github returns a max of 30 pull request per call
    if len(prs) > 0: 
        close_all_pull_requests(username=username, access_token=access_token)
    
    print(f"You removed {pr_count} PRs")

# Replace with your GitHub username and access token

print("Enter your Github username")
username = input()
print("Enter your github access token")
access_token = input()
close_all_pull_requests(username, access_token)