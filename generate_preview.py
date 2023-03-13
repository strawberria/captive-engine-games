import glob
from json import dump, load
from os import popen

# Iterate over games within ./games/**/game.json
game_previews = []
relative_game_filepaths = glob.glob("./games/**/game.json", recursive=True)
for relative_game_filepath in relative_game_filepaths:
    print(f">> Generating preview for {relative_game_filepath}")

    game_preview = { "top_filepath": relative_game_filepath }

    # Retrieve Git last updated timestamp
    git_updated_timestamp_str = popen(f'git log -1 --pretty="format:%at" "{relative_game_filepath}"').read()
    # Ignore files with length 0 - somehow not added?
    if(len(git_updated_timestamp_str) == 0): 
        print(f"/!\\ '{relative_game_filepath}' couldn't retrieve git updated timestamp")
        continue
    git_updated_timestamp = int(git_updated_timestamp_str)

    # Parse engine version and game (title, version, author, synopsis)
    game_preview["updated"] = git_updated_timestamp
    with open(relative_game_filepath, "r") as game_data_file:
        game_data = load(game_data_file)

        # Skip adding game data if somehow missing information field
        if game_data["game"] == None or game_data["game"]["metadata"] == None:
            print(f"/!\\ '{relative_game_filepath}' couldn't find information for preview generation")

        game_preview["engine"] = game_data["custodial"]["version"] if "custodial" in game_data else "0.0.0"
        game_preview["title"] = game_data["game"]["metadata"]["title"]
        game_preview["author"] = game_data["game"]["metadata"]["author"]
        game_preview["version"] = game_data["game"]["metadata"]["version"]
        game_preview["synopsis"] = game_data["game"]["metadata"]["synopsis"]
        game_preview["path"] = relative_game_filepath

        print(f"'{relative_game_filepath}' found '{game_preview['title']}' by '{game_preview['author']}' with version '{game_preview['version']}'")
    
    game_previews.append(game_preview)

# Sort preview with most recently updated first (largest timestamp)
print(f">> Sorting game previews by most recently updated")
game_previews_sorted = sorted(game_previews, key=lambda x: x["updated"])[::-1]

# Write resulting sorted preview data to preview.json
with open("preview.json", "w") as preview_file:
    print(f">> Writing game previews to preview.json")
    dump(game_previews, preview_file)


