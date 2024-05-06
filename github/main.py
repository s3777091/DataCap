import os
import requests

# Define the GitHub repository details
owner = "s3777091"
repo = "AndroidShopping"
branch = "master"
lang = "java"
token = "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"

# Setup the authorization headers for accessing GitHub API
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}

# Local directory setup
local_directory = "tab"
if not os.path.exists(local_directory):
    os.makedirs(local_directory)

# Path for the consolidated .txt file
output_file_path = os.path.join(local_directory, "all_java_files.txt")

def getFile(repo_owner, repo_name, repo_branch, file_path):
    # Construct the URL to access the file content
    url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{repo_branch}/{file_path}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(f"Downloading {file_path}...")
            # Append the content to the output file
            with open(output_file_path, 'a', encoding='utf-8') as f:
                f.write(response.text + "\n\n")
        else:
            print(f"Failed to get file {file_path} from GitHub. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while fetching {file_path}: {e}")

def getFolder(owner, repo, branch, lang, token=None, dir_path=""):
    # API endpoint for repository content
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{dir_path}?ref={branch}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            for item in content:
                if item['type'] == 'dir':
                    # Recursive call to handle directories
                    sub_dir_path = f"{dir_path}/{item['name']}" if dir_path else item['name']
                    getFolder(owner, repo, branch, lang, token, sub_dir_path)
                elif item['name'].endswith(f".{lang}"):
                    # Handle Java files
                    file_path = extract_directory_path(item['url'], repo, branch)
                    getFile(owner, repo, branch, file_path)
        else:
            print(f"Failed to access folder {dir_path} on GitHub. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

def extract_directory_path(url, repo, branch):
    # Extract the file path from the URL
    start_index = url.find(f"{repo}/contents/") + len(f"{repo}/contents/")
    end_index = url.find(f"?ref={branch}")
    if start_index != -1 and end_index != -1:
        return url[start_index:end_index]
    return None

if __name__ == "__main__":
    # Clear content of the output file before starting
    open(output_file_path, 'w').close()
    getFolder(owner, repo, branch, lang)
