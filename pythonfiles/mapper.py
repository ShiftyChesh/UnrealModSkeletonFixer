from collections import namedtuple
from typing import Sequence

from .readAnimAsset import *
import sys
import json

DEFAULT_MAPPING_FILE = "mapping.json"


def create_mapping_file(file_name, bone_order: Sequence[BoneData], name_mappings):
    structs = []
    for index, bi in enumerate(bone_order):
        bone_index = bi.bone_name_index
        bone_name = name_mappings[bone_index]
        structs.append(
            {
                "bone_name": bone_name,
                "bone_index": index,
            })
    json_obj = {
        "bone_count": len(bone_order),
        "bones": structs
    }
    with open(file_name, "w") as f:
        json.dump(json_obj, f, indent=2)


def read_mapping_file(file_name):
    with open(file_name, "r") as f:
        return json.load(f)


# given a mapping order, and an input bone_order & name mapping for the bones, rearrange the bones to fit the mapping_data
# for context, 'old' refers to the order being modified. in this case the modded data.
def bone_order_from_mapping(mapping_data, old_bone_order, old_name_mapping) -> (Sequence[BoneData], {int, int}):
    if len(mapping_data["bones"]) != len(old_bone_order):
        print("bone replacement for models with different numbers of bones are not yet supported.")
        print("Continuing by truncating new bones array. (additional bones will be lost if modding skeleton)")

        while len(mapping_data["bones"]) > len(old_bone_order):
            del (old_bone_order[-1])  # delete last index

    new_order_mapping = dict((item["bone_name"], item) for item in mapping_data["bones"])
    new_bone_order = [BoneData(0, 0)] * mapping_data["bone_count"]
    extra_bones = []
    bone_index_order = {}

    # make sure first bone is root bone. if not, you got yourself a problem
    root_bone_name = old_name_mapping[old_bone_order[0].bone_name_index]
    if not (root_bone_name == "root"):
        raise Exception("Skeleton used in mod does not have the base name 'Armature'")

    for old_index, boneData in enumerate(old_bone_order):
        # print(map)
        bone_name = old_name_mapping[boneData.bone_name_index]
        new_item = new_order_mapping.get(bone_name)
        old_parent_name = old_name_mapping[old_bone_order[boneData.parent_index].bone_name_index]
        if boneData.parent_index == -1:
            new_parent_index = -1
        else:
            new_parent_index = new_order_mapping[old_parent_name]["bone_index"]
        new_bone_data = BoneData(boneData.bone_name_index, new_parent_index)
        if new_item is None:  # bone doesnt exist in original skeleton
            extra_bones.append((new_bone_data,old_index))
            continue
        new_index = new_item["bone_index"]
        bone_index_order[old_index] = new_index
        # bone does exist, put it in correct location in array
        new_bone_order[new_index] = new_bone_data

    for bone,old_bone_index in extra_bones:
        bone_index = len(new_bone_order)
        bone_index_order[old_bone_index] = bone_index
        new_bone_order.append(bone)

    return (new_bone_order, bone_index_order)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("not enough args")
        input()
        quit()

    uasset_file = ''
    uexp_file = ''
    for file_name in sys.argv:
        if file_name.endswith(".uexp"):
            uexp_file = file_name
        if file_name.endswith(".uasset"):
            uasset_file = file_name

    if not uexp_file or not uasset_file:
        print("this script requires a file with a .uexp extension, and one with a .uasset extension")
        input()
        quit()
    name_mappings = read_uasset(uasset_file)
    bone_order = read_skel_uexp(uexp_file)

    create_mapping_file(DEFAULT_MAPPING_FILE, bone_order, name_mappings)
    print(f"Created mapping from files: {uasset_file}\n& {uexp_file}")
    # mapping = read_mapping_file(DEFAULT_MAPPING_FILE)
    # new_bones = bone_order_from_mapping(mapping, bone_order, name_mappings)
    # for bone in new_bones:
    #     print(bone)
    # # print(name_mappings[7])
    input()
