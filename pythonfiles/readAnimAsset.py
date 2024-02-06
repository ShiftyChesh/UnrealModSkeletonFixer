import os
import sys
import mmap
from collections import namedtuple
from typing import Literal, Sequence
import json

# little or big endian
ENDIAN: Literal["little", "big"] = "little"
BoneIndex = namedtuple('BoneIndex', 'bone_name_index parent_index')


# Get the index name pairings of the skeleton form the header .uasset file. needed in order to remap the indexes to fit the original order
def read_uasset(file_name):
    """Reads a .uasset file in order to return a dictionary of [int,str] name mappings,
    which in this case are used to determine bone names"""
    name_mappings = {}  # maps index to bone name

    with open(file_name, "rb") as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            name_size_byte = b'\x00\x22\x00\x80'
            name_size_index = mm.find(name_size_byte) + 4
            num_of_names = int.from_bytes(mm[name_size_index:name_size_index + 4], ENDIAN)
            # print(f"Number of defined names: {num_of_names}")
            header_end = mm.find(b'\xff\xff\xff\xff\xff\xff\xff\xff')  # signifies end of header i think
            names_start = header_end + 8
            # print(names_start)
            start_index: int = names_start
            # array of struct containing length of name, then said name
            for i in range(num_of_names):
                str_length: int = int.from_bytes(mm[start_index:start_index + 4], ENDIAN)
                str_name = mm[(start_index + 4):(start_index + 4 + str_length - 1)].decode(
                    "utf-8")  # final character is null terminator, don't need that when converting to str
                # print(str_name)
                start_index = start_index + 8 + str_length
                name_mappings[i] = str_name
                pass
        return name_mappings


# read the skeleton data stored in the .uexp file (assuming its skeleton data)
def read_skel_uexp(file_name) -> Sequence[BoneIndex]:
    """Returns a sequence of bones that contains their name indexes and the array index of their parent bone.
    Getting the name of the bone requires the associate name index using the name_mappings from the .uasset file"""
    bone_order = []  # order of bones by name index, and parent
    with open(file_name, "rb") as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            root_bone_index = mm.find(
                b'\xff\xff\xff\xff')  # root bone always has -1 for parent, making it easy to find in an AOB search
            start_index = root_bone_index - 8
            bone_count = int.from_bytes(mm[start_index - 4:start_index], ENDIAN)
            # print(f"Number of bones: {bone_count}")

            for i in range(bone_count):
                bone_name_index = int.from_bytes(mm[start_index:start_index + 4], ENDIAN)
                parent_index = int.from_bytes(mm[start_index + 8:start_index + 12], ENDIAN, signed=True)
                bone_order.append(BoneIndex(bone_name_index, parent_index))
                start_index += 12  # size of struct
    return bone_order


def write_skel_uexp_bone_order(file_name, bone_order: Sequence[BoneIndex]):
    with open(file_name, "r+b") as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE) as mm:
            root_bone_index = mm.find(b'\xff\xff\xff\xff')
            start_index = root_bone_index - 8
            for bone in bone_order:
                mm[start_index:start_index + 4] = int.to_bytes(bone.bone_name_index, 4, ENDIAN)
                mm[start_index + 8:start_index + 12] = int.to_bytes(bone.parent_index, 4, ENDIAN, signed=True)
                start_index += 12
            mm.close()


def read_skel_assets_from_dir(working_dir, skel_asset_name=''):
    """Finds and returns a tuple of the (uasset,uexp) files in the given workign directory.
    Can include the skeleton asset name if multiple skeleton files are in the dir"""
    files = []
    uasset_file = ''
    uexp_file = ''
    if skel_asset_name is None:
        files = os.listdir(working_dir)
    else:
        files = [name for name in os.listdir(working_dir) if os.path.splitext(name)[0].endswith(skel_asset_name)]
    for fname in files:
        if fname.endswith('.uasset'):
            uasset_file = f"{working_dir}/{fname}"
        if fname.endswith('.uexp'):
            uexp_file = f"{working_dir}/{fname}"

    return (uasset_file, uexp_file)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        quit()

    uasset_file = sys.argv[1]
    name_mappings = read_uasset(uasset_file)

    if len(sys.argv) < 3:
        quit()

    uexp_file = sys.argv[2]
    bone_order = read_skel_uexp(uexp_file)

    for bi in bone_order:
        bone_index = bi.bone_name_index
        parent_index = bi.parent_index
        print(f"Name: {name_mappings[bone_index]}, parent index: {parent_index}")

    # print(name_mappings[7])
    input()
