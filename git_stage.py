import os
import subprocess
import threading
import util 
from util import Color, color_print
import subprocess
import re
from urllib.parse import urlparse
from config import global_path

global_exclusions = [".git"]

def has_staging_directory(repo_url):
    staging_directory = get_staging_directory(repo_url)
    return os.path.exists(staging_directory)

def get_staging_directory(repo_url):
    # Parse the repository name from the Git URL
    repo_name = os.path.splitext(os.path.basename(urlparse(repo_url).path))[0]

    # Create the full path for the staging directory under global_stage_path
    return os.path.join(global_path, repo_name)

def create_staging_directory(src_directory, email, username, repo_url, branch):

    staging_directory = get_staging_directory(repo_url)

    if os.path.exists(staging_directory):
        return staging_directory

    # Create the staging directory if it does not exist
    os.makedirs(staging_directory, exist_ok=True)

    # Change the current working directory to the staging directory
    os.chdir(staging_directory)

    # Initialize the staging directory as a Git repository and set the remote URL
    subprocess.run(["git", "init"])
    subprocess.run(["git", "config", "--local", "user.email", '"{}"'.format(email)])
    subprocess.run(["git", "config", "--local", "user.name", '"{}"'.format(username)])
    subprocess.run(["git", "remote", "add", "origin", repo_url])
    subprocess.run(["git", "checkout", "-b", branch])

    return staging_directory


def sync(local_directory, staging_directory, branch, delay, callback, commit_message="Auto-sync: Updating from local source."):
    callback_alive = True
    while util.keep_alive and callback_alive:
        git_pull_with_conflict_handling(staging_directory, branch)
        merge_stage(local_directory, staging_directory)
        git_auto_commit_push(staging_directory, branch, commit_message)
        callback_alive = callback(local_directory)
        util.sleep(delay)

    print(f"Killed sync thread for {staging_directory}.")


def merge_stage(local_directory, staging_directory):
    # Change the current working directory to the local source directory
    os.chdir(local_directory)

    if not os.path.exists(os.path.join(local_directory, ".git")):
        subprocess.run(["git", "init"])

    subprocess.run(["git", "add", "."], stdout=subprocess.DEVNULL)

    # Run 'git ls-files' to get a null-delimited list of files
    git_ls_files_result = subprocess.run(
        ["git", "status", "--porcelain"], stdout=subprocess.PIPE, text=True
    )

    status_lines = git_ls_files_result.stdout.split("\n")

    files_list = [re.sub(r'^..."?', '', line.strip('"\n')) for line in status_lines if line]

    if(len(files_list) > 0):
        color_print(f"{Color.YELLOW}Synchronizing files from {local_directory}: {Color.RED}{files_list}")

        # Run 'rsync' to synchronize the files with the staging directory
        cmd = util.rsync_cmd(local_directory + "/", staging_directory, ["--files-from=-", "-ar"], global_exclusions)

        subprocess.run(cmd, input="\n".join(files_list), stdout=subprocess.DEVNULL, text=True)

    cmd = util.rsync_cmd(local_directory + "/", staging_directory, 
                         ["-r", "--delete", "--existing", "--ignore-existing"], 
                         global_exclusions)
    subprocess.run(cmd, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "commit", "-m", "Auto-commit: Delete me."], stdout=subprocess.DEVNULL)

def git_pull_with_conflict_handling(directory, branch):
    # Change the current working directory to the specified directory
    os.chdir(directory)

    response = subprocess.run(["git", "pull", "origin", branch, "--no-edit", "--strategy-option=theirs"], 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if(response.returncode != 0):
        color_print(f"Error [{response.returncode}] during auto-pull: {response.stderr}", Color.RED)


def git_auto_commit_push_with_pull(directory, branch, commit_message):
    # Pull from the remote repository and handle merge conflicts first
    git_pull_with_conflict_handling(directory, branch)

    # Perform the auto-commit and push
    git_auto_commit_push(directory, branch, commit_message)


def git_auto_commit_push(directory, branch, commit_message):
    # Change the current working directory to the specified directory
    os.chdir(directory)

    # Add all changes, commit, and push to the repository
    subprocess.run(["git", "add", "."], stdout=subprocess.DEVNULL)
    subprocess.run(["git", "commit", "-m", commit_message], stdout=subprocess.DEVNULL)
    response = subprocess.run(["git", "push", "--set-upstream", "origin", branch], 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if(response.returncode != 0):
        color_print(f"Error [{response.returncode}] during auto-push: {response.stderr}", Color.RED)

def init_stage(src_dir, repo_url, email, username, branch, delay, callback):
    staging_directory = create_staging_directory(src_dir, email, username, repo_url, branch)
    util.add_thread(threading.Thread(target=lambda: sync(
                src_dir, staging_directory, branch, delay, callback
        )
    )).start()
