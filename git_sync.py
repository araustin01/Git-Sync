import util
from util import Color, color_print
import git_stage
import os
import subprocess
from config import global_mapping

def merge_to_src(local_directory, staging_directory):
    color_print(f"{Color.BLUE}Beginning local merge of {Color.CYAN}{staging_directory}{Color.YELLOW} -> {Color.CYAN}{local_directory}{Color.BLUE}.")

    if(not staging_directory or not os.path.exists(staging_directory)):
        color_print(f"Merge Failed! {local_directory} is not yet setup.", Color.RED)
        return

    # Change the current working directory to the local source directory
    os.chdir(local_directory)

    # Read the contents of .gitignore and split into exclusion patterns
    gitignore_patterns = []
    gitignore_file_path = os.path.join(local_directory, ".gitignore")
    if os.path.exists(gitignore_file_path):
        with open(gitignore_file_path, "r") as gitignore_file:
            gitignore_patterns = gitignore_file.read().splitlines()

    # Merge changes from staging directory to local source directory
    add_args = ["-arv"]
    delete_args = ["-rv", "--delete", "--existing", "--ignore-existing"]
    
    add_cmd = util.rsync_cmd(staging_directory + "/", "./", add_args + ["--dry-run"], git_stage.global_exclusions)
    delete_cmd = util.rsync_cmd(staging_directory + "/", "./", 
              delete_args + ["--dry-run"], 
              git_stage.global_exclusions + gitignore_patterns)
    
    dryrun_result = subprocess.run(delete_cmd, stdout=subprocess.PIPE).stdout.decode('utf-8')
    deleted_directories = [line.replace("deleting ", "") for line in dryrun_result.split('\n') if line.endswith('/')]
    exclude_dirs = [dir for dir in deleted_directories if len(os.listdir(dir)) == 0]

    delete_cmd = util.rsync_cmd(staging_directory + "/", "./", 
              delete_args + ["--dry-run"], 
              git_stage.global_exclusions + gitignore_patterns + exclude_dirs)    

    color_print(f"{Color.YELLOW}Please confirm the following changes before continuing with the merge:")

    subprocess.run(add_cmd)
    subprocess.run(delete_cmd)

    user_input = input(f"{Color.YELLOW}Continue with the following changes? (y/n): ").lower()

    if user_input != 'y':
        return

    add_cmd = util.rsync_cmd(staging_directory + "/", "./", add_args, git_stage.global_exclusions)
    delete_cmd = util.rsync_cmd(staging_directory + "/", "./", 
              delete_args, 
              git_stage.global_exclusions + gitignore_patterns + exclude_dirs)

    subprocess.run(add_cmd)
    subprocess.run(delete_cmd)
    

def handle_callback(src):
    # TODO Add support for offline server merge
    #print(f"Handling callback for: {global_mapping[src]}")
    return True

if __name__ == "__main__":
    for local_directory, config in global_mapping.items():
        git_stage.init_stage(local_directory, 
                            config["repo_url"], 
                            config["email"], 
                            config["username"], 
                            config["branch"], 
                            config["sync_delay"], 
                            handle_callback)
        
    util.keep_alive()
    print("All threads have been shut down.")