import sys
import readAnimAsset as ream
import mapper
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("not enough args")
        input()
        quit()

    uasset_file = ''
    uexp_file = ''
    mapping_file = ''
    for file_name in sys.argv:
        if file_name.endswith(".uexp"):
            uexp_file = file_name
        if file_name.endswith(".uasset"):
            uasset_file = file_name
        if file_name.endswith(".json"):
            mapping_file = file_name

    if not uexp_file or not uasset_file or not mapping_file:
        print("this script requires a .uexp file, .uasset file, and a .json mapping file in order to run")
        input()
        quit()
    name_mappings = ream.read_uasset(uasset_file)
    bone_order = ream.read_skel_uexp(uexp_file)

    mapping = mapper.read_mapping_file(mapping_file)
    new_bones = mapper.bone_order_from_mapping(mapping, bone_order, name_mappings)
    if not new_bones:
        quit()

    ream.write_skel_uexp_bone_order(uexp_file, new_bones)
    print(f"Bones successfully altered for file:\n{uexp_file}")
    # for bone in new_bones:
    #     print(bone)
    # # print(name_mappings[7])
    input()