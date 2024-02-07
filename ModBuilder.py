import os
import json
import pathlib
import re
import subprocess
import shutil
import pythonfiles.mapper as mapper
import pythonfiles.readAnimAsset as ream

# requires python 3.4+

CONFIG_PATH = "config.json"
MOD_CONFIG_NAME = "modconfig.json"
MOD_DIR = "mods"
MAPPING_DIR = "mapping"


def create_mapping(skel_name, mapping_file_path, working_dir):
    files = [name for name in os.listdir(working_dir) if os.path.splitext(name)[0] == skel_name]
    # f ind .uasset and .uexp files in dir
    uasset_file = ''
    uexp_file = ''
    for fname in files:
        if fname.endswith('.uasset'):
            uasset_file = f"{working_dir}/{fname}"
        if fname.endswith('.uexp'):
            uexp_file = f"{working_dir}/{fname}"
    if uexp_file is None or uasset_file is None:
        print(
            f"WARNING: Unable to find original files in directory {working_dir} to create mappings from for skeleton: {skel_name}")
        return False
    # read from original files to create mapping structure
    name_mappings = ream.read_uasset(uasset_file)
    bone_order = ream.read_skel_uexp(uexp_file)
    # create and save mapping structure
    mapper.create_mapping_file(mapping_file_path, bone_order, name_mappings)
    # now that the mapping file is created, return the mapping data to be used to update the skeletons
    return mapper.read_mapping_file(mapping_file_path)


def bone_realignment(mod_name, mod_files, config):
    # first, find all the Skel files in the mod
    skel_files = [file for file in mod_files if file.name.endswith("Skeleton.uasset")]
    mapping_path = f"{MAPPING_DIR}/{mod_name}"
    anim_regex = config["anim_search_pattern"]
    anim_files = [file for file in mod_files if re.match(anim_regex, file.name) and file.name.endswith('.uexp')]

    # next, check that we have a mapping file set up, or the files needed to create a mapping file
    # this runs for each unique skeleton found in the mod's subdirectories (usually 1 but can be more)
    if len(skel_files) > 1:
        print(
            "This tool currently does not correctly support fixing the animations for mods with multiple skeleton files. if this becomes an issue, let me know")
    for skel_file in skel_files:
        file_name = skel_file.name
        name = os.path.splitext(file_name)[0]
        mapping_file_name = f"{name}-map.json"
        # check if mapping file exists
        mapping_file_path = pathlib.Path(f"{mapping_path}/{mapping_file_name}")
        if not mapping_file_path.parent.exists():
            mapping_file_path.parent.mkdir(exist_ok=True,parents=True)
        mapping_data = {}
        if mapping_file_path.exists():
            mapping_data = mapper.read_mapping_file(mapping_file_path)
        elif file_name in os.listdir(mapping_path):
            mapping_data = create_mapping(name, mapping_file_path, mapping_path)
        else:
            print(
                f"WARNING: Unable to find/create mapping file for skeleton file asset: {skel_file}\nmake sure you have a copy of the original skeleton.uasset &.uexp in the mapping folder for this mod")
            continue
        if not mapping_data:
            print(
                f"unable to read mapping file data: {mapping_file_path}\nmake sure you have a copy of the original skeleton.uasset &.uexp in the mapping folder for this mod")
            continue
        # now that we have the mapping data, time to get the .uasset and .uexp files for the skeleton that we want to edit
        skel_file_dir = os.path.dirname(skel_file)

        (uasset, uexp) = ream.read_skel_assets_from_dir(skel_file_dir, name)
        name_mappings = ream.read_uasset(uasset)
        bone_order = ream.read_skel_uexp(uexp)

        # sometimes you just need $100 for a new set of bones
        (new_bones, bone_index_remap) = mapper.bone_order_from_mapping(mapping_data, bone_order, name_mappings)
        if new_bones is not None:
            ream.write_skel_uexp_bone_order(uexp, new_bones)
            print(f"Rebuilt bones for Skeleton: {name}")
            # now find and update all animations that use this skeleton

            for anim_file in anim_files:
                ream.write_anim_uexp_bone_index_order(anim_file, bone_index_remap)
                print(f"Bones for animation {anim_file.name} have been fixed")

        if not config["keep_skeleton"]:
            skel_file_noext = os.path.splitext(skel_file)[0]
            os.remove(f"{skel_file_noext}.uexp")
            os.remove(f"{skel_file_noext}.uasset")


def copy_cooked_files_to_mod(mod_config, cook_content_folder, mod_name):
    """Uses the mod config data to copy over the cooked files into the mod"""
    files_to_copy = mod_config["mod_files"]
    abs_mod_content_path = mod_config["mod_content_path"]
    for copy_file in files_to_copy:
        abs_cook_path = f"{cook_content_folder}/{copy_file}"
        abs_mod_path = f"{abs_mod_content_path}/{copy_file}"
        shutil.copyfile(abs_cook_path, abs_mod_path)


# run build steps for each mod
def update_mod_config(mod_config, mod_name, mod_files):
    """Takes the list of mod files and finds ones with the same name in the cook directory"""
    mapping_dir = f"{MAPPING_DIR}/{mod_name}"
    mod_config_file = pathlib.Path(f"{mapping_dir}/{MOD_CONFIG_NAME}")
    mod_content_path = ""

    abs_path = str(mod_files[0])
    if mod_config is None or not mod_config["mod_content_path"]:
        if len(mod_files) > 0:
            mod_content_path = abs_path[:abs_path.find("Content")+8]
    else:
        mod_content_path = mod_config["mod_content_path"]
    mod_cook_paths = []
    if mod_config is None:  # If no mod config, create lsit of files from scratch
        for mod_file in mod_files:
            abs_path = str(mod_file)
            start_index = abs_path.find("Content")
            if (start_index == -1):
                print(f"unable to find cooked content path for: {mod_file.name}")
            else:
                mod_cook_paths.append(
                    abs_path[start_index + 8:])  # +8 because we dont need to content folder name twice
    else:  # has mod config, mod_cook_paths should be loaded from config directly
        mod_cook_paths = mod_config["mod_files"]


    if not mod_config_file.parent.exists():
        mod_config_file.parent.mkdir(exist_ok=True, parents=True)
    mod_config = {
        "mod_content_path": mod_content_path,
        "mod_files": mod_cook_paths
    }
    with open(mod_config_file, "w+") as f:
        json.dump(mod_config, f, indent=2)
    return mod_config


def read_mod_config(mod_name):
    mapping_dir = f"{MAPPING_DIR}/{mod_name}"
    mod_config_file = pathlib.Path(f"{mapping_dir}/{MOD_CONFIG_NAME}")

    if not mod_config_file.exists():
        return None

    with open(mod_config_file, "r") as f:
        return json.load(f)


def build_mods(mod_folders, config):
    temp_file = f"{os.getcwd()}/temp.txt"
    for folder in mod_folders:
        abs_folder = f"{os.getcwd()}/{MOD_DIR}/{folder}"
        mod_name = os.path.basename(folder)
        print(
            f"""------------------------------------------
        Building {mod_name}
----------------------------------------------""")
        mod_files = []
        # get all mod files
        for file in pathlib.Path(abs_folder).rglob('*'):
            if file.exists() and file.is_file():
                mod_files.append(file)
        # import files from cook folder
        # update mod config using existing files in mod folder
        cook_folder = config["cook_content_folder"]
        if os.path.exists(cook_folder):
            mod_config = read_mod_config(mod_name)
            mod_config = update_mod_config(mod_config, mod_name, mod_files)
            # read mod config
            copy_cooked_files_to_mod(mod_config, cook_folder, mod_name)
            print(f"Copied matching cook folder files into mod {mod_name}")

            mod_files = [] # re-init mod_files list
            # get all mod files
            for file in pathlib.Path(abs_folder).rglob('*'):
                if file.exists() and file.is_file():
                    mod_files.append(file)
        else:
            print(f"WARNING: Cannot find cook content folder with path {cook_folder}")
        # now copy the cooked files and move them over!

        # perform skeleton mesh update functions...
        bone_fix = config["bone_fix"]
        if bone_fix:
            bone_realignment(mod_name, mod_files, config)


        # build mods
        packer_exe = config["packer_path"]
        pak_name = f"{os.getcwd()}/{MOD_DIR}/{mod_name}.pak"
        if config["autopack_mods"]:
            if os.path.exists(packer_exe):
                build_command = f"{packer_exe} {pak_name} -create={temp_file} -compress"
                pak_search_paths = f"\"{abs_folder}/*.*\" \"..\\..\\..\\*.*\""  # just search inside the mod folder. thats it
                with open(temp_file, "w") as f:
                    f.write(pak_search_paths)
                subprocess.call(build_command)
            else:
                print(f"ERROR: Cannot find packer executable at location: {packer_exe}.\nPlease check your config.json "
                      f"file and make sure the packer_path value is correct. \nExiting...")
                return
        # move built mods into mod directory
        mod_dir = config["mods_p_path"]
        auto_move = config["move_all_mods"] or mod_name in config["moveover_mod_list"]
        if auto_move:
            if os.path.exists(mod_dir):
                print(f"Copying {mod_name}.pak into mods folder")
                shutil.copyfile(pak_name, f"{mod_dir}/{mod_name}.pak")
            else:
                print(
                    f"ERROR: Cannot find the mods export directory at location: {mod_dir}.\nPlease check your config.json "
                    f"file and make sure the mods_p_path value is correct. \nExiting...")

    if os.path.exists(temp_file):
        os.remove(temp_file)


def read_mapping_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def write_mapping_config(packer_path):
    with open(CONFIG_PATH, 'w') as f:
        json.dump({
            "packer_path": packer_path,

        }, f, indent=2)

# run starts here
if __name__ == "__main__":
    mods_dir = f"{os.getcwd()}/{MOD_DIR}"
    dir_folders = [name for name in os.listdir(mods_dir) if os.path.isdir(f"mods/{name}") and not name.startswith('.')]
    config = read_mapping_config()
    success= True
    try:
        build_mods(dir_folders, config) # where all the work is actually done
    except Exception as ex:
        success = False
        print(ex)
        print("Failed to build correctly.")
        input()
        raise ex

    if success:
        print("Build Complete!")
    input()
