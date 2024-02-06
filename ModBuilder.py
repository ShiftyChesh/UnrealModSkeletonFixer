import os
import json
import pathlib
import subprocess
import shutil
import pythonfiles.mapper as mapper
import pythonfiles.readAnimAsset as ream

# requires python 3.4+

CONFIG_PATH = "config.json"
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


def bone_realignment(mod_name, mod_files):
    # first, find all the Skel files in the mod
    skel_files = [name for name in mod_files if name.name.endswith("Skeleton.uasset")]
    mapping_path = f"{MAPPING_DIR}/{mod_name}"
    # next, check that we have a mapping file set up, or the files needed to create a mapping file
    # this runs for each unique skeleton found in the mod's subdirectories (usually 1 but can be more)
    for skel_file in skel_files:
        file_name = skel_file.name
        name = os.path.splitext(file_name)[0]
        mapping_file_name = f"{name}-map.json"
        # check if mapping file exists
        mapping_file_path = f"{mapping_path}/{mapping_file_name}"
        mapping_data = {}
        if os.path.exists(mapping_file_path):
            mapping_data = mapper.read_mapping_file(mapping_file_path)
        elif file_name in os.listdir(mapping_path):
            mapping_data = create_mapping(name, mapping_file_path, mapping_path)

        else:
            print(f"WARNING: Unable to find/create mapping file for skeleton file asset: {skel_file}")
            continue
        if not mapping_data:
            print(f"unable to read mapping file data: {mapping_file_path}")
            continue
        # now that we have the mapping data, time to get the .uasset and .uexp files for the skeleton that we want to edit
        skel_file_dir = os.path.dirname(skel_file)

        (uasset, uexp) = ream.read_skel_assets_from_dir(skel_file_dir, name)
        name_mappings = ream.read_uasset(uasset)
        bone_order = ream.read_skel_uexp(uexp)

        # sometimes you just need $100 for a new set of bones
        new_bones = mapper.bone_order_from_mapping(mapping_data, bone_order, name_mappings)
        if new_bones is not None:
            ream.write_skel_uexp_bone_order(uexp, new_bones)
            print(f"Rebuilt bones for Skeleton: {name}")


# run build steps for each mod
def build_mods(mod_folders, config):
    temp_file = f"{os.getcwd()}/temp.txt"
    for folder in mod_folders:
        abs_folder = f"{os.getcwd()}/{MOD_DIR}/{folder}"
        mod_name = os.path.basename(folder)
        print(
            f"""------------------------------------------
        Building {mod_name}
----------------------------------------------
""")
        mod_files = []
        # get all mod files
        for file in pathlib.Path(abs_folder).rglob('*'):
            if os.path.isfile(file):
                mod_files.append(file)

        # perform skeleton mesh update functions...
        bone_fix = config["bone_fix"]
        if bone_fix:
            bone_realignment(mod_name, mod_files)

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


if __name__ == "__main__":
    mods_dir = f"{os.getcwd()}/{MOD_DIR}"
    dir_folders = [name for name in os.listdir(mods_dir) if os.path.isdir(f"mods/{name}") and not name.startswith('.')]
    config = read_mapping_config()

    build_mods(dir_folders, config)
    input()
