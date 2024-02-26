from config import global_mapping
import sys
import git_sync
from git_stage import sync, get_staging_directory

import util 
from util import Color, color_print

args = "\n".join(list(global_mapping.keys()))
if(len(sys.argv) != 2):
    color_print(
        f"{len(sys.argv)-1} arguments given (1 expected). Try {Color.YELLOW}\"python update.py [server_path]\"{Color.RED}.\n"
        f"Please specify a server path to update from the following options: \n{Color.RESET}{args}",
        Color.RED
    )
    exit(1)

src = sys.argv[1]
config = global_mapping.get(src)
if(config is None):
    color_print(
        f"Unexpected path given ({Color.YELLOW}{src}{Color.RED}). Try {Color.YELLOW}\"python update.py [server_path]\"{Color.RED}.\n"
        f"Please specify a server path to update from the following options: \n{Color.RESET}{args}",
        Color.RED
    )
    exit(1)

stage = get_staging_directory(config["repo_url"])
color_print("Synchronizing contents before merging...", Color.YELLOW)
sync(src, stage, config["branch"], 0, lambda local_directory: False)
color_print("Sync Complete!", Color.GREEN)
git_sync.merge_to_src(src, stage)

color_print(f"Done!", Color.GREEN)