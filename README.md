# Unreal Mod Skeleton Fixer & Mod Auto-builder
This project aims to fix modded skeleton .uasset files cooked in Unreal Engine 5 (UE5)
so that they can be added into a mod without breaking the original animations for the unmodded skeleton.
Basically, if you've seen a tutorial for unreal modding where they say "make sure to remove the skeleton asset after cooking", this tool fixes that.
Originally made for Palworld, it currently has not been tested on other games.
Please open Issues if you have any problems using this tool.

if you want to understand the technical side of what this tool does, check out the file "pythonfiles/Unreal Skeletons Technical Stuff.txt" 

### How To Use:
Double-click on the "ModBuilder.bat" file, and it will work automatically, once the config setup steps have been completed (see section: Config Setup)

## Mod Building Automation
This may seem out of place for a tool that's only supposed to mod skeleton files, 
but the process to manually run the commands necessary to fix the skeleton can be confusing and annoying. 
So this automation setup was also created to streamline that process.

### Setup:
In order to get full use out of this tool, it requires some setup steps. 
#### External Requirements: 
1. [Python 3.4+](https://www.python.org/downloads/) - This scripts run on python. 
2. [UnrealPak for UE5 (soft requirement)](https://cdn.discordapp.com/attachments/1107095082567471114/1199033018841571428/UnrealPak.zip?ex=65c11184\u0026is=65ae9c84\u0026hm=cabe101f5232a9ed42c280eedb4e46b6b175fd6a4d7f784232c7fc0b4d2a0a9d\u0026):
Unfortunately the version found by googling is only version 4.27 so the version in this link has to be used to my knowledge.

#### Config Setup:
the config.json file must have the "cook_content_folder", "packer_path", and "mods_p_path" updated in order to work fully
The config json fields do the following:
- "pull_mod_files_from_cook_folder":bool - if true, enables this tool to pull files directly from the cooked assets output of Unreal
- "cook_content_folder" : string - Path to the Cooked/..../Content folder in Unreal that you use to create mods
- "autopack_mods" : bool - If true, automatically creates .pak files of mods in the 'mods' folder/ Requires "packer_path" to be valid
- "packer_path" : string - Path to the UnrealPak.exe file for building .pak files. Only needs a valid path if "autopack_mods" is true
- "bone_fix" : bool - If true, any skeleton uassets will be fixed based on the source mappings found in the 'mapping' folder (see section: ### Mapping Setup)
- "keep_skeleton" : bool - If false, deletes skeleton file after bone fix so built mod doesn't contain skeleton file
- "anim_search_pattern": string - the regex pattern used to find animation files in the mod that sohuld be fixed.
- "mods_p_path" : string - Path to your mods folder for patch mods. This is the unreal mods in the paks directory. For Palworld it's the: /Pal/Content/Paks/~mods folder
- "build_all_mods": bool - If true, builds all mods in the 'mods' folder.
- "build_mod_list" : string[] - lists mods you want to build. useful if only building/testing a specific mod
- "move_all_mods" : bool - If true, copies all built mods into the "mods_p_path" directory
- "moveover_mod_list" : string[] - Lists mods you want to automatically move to "mods_p_path" is "move_all_mods" is false. Good if you only want to move/test some of your mods.

### Mapping File
In order for the bone remapping to work, you need to make sure you have the ORIGINAL skeleton uasset files from the game you are trying to mod. 
They can be exported as raw uasset data by [FModel](https://fmodel.app/).
those ORIGINAL files should be placed in the mappings folder then in a folder with the same name as the mod containing the skeleton uasset you wish to fix. This can be seen in the included ExampleMod_P mod

### Mod Config
When a mod is built for the first time, a modconfig.json is created in the mapping/YOUR_MOD folder (where YOUR_MOD is the name of your mod).
the modconfig.json file contains the source directories that this mod copies its files from, as part of the pull_mods_from_cook_folder step.
if one or more of those source directories don't exist, an error will be thrown and the tool will fail to build.

To update the modconfig.json, either open it and add/remove paths to files you want to copy. Alternatively delete the file, and it will be regenerated with an updated list of files.
populating the list of files by seeing what has the same name as files in your mod's folder structure.


### Limitations
 - Doesn't work if you try and fix the bone order that has been reimported into Unreal itself (yet). The fix is to delete the file and import the entire .fbx file again
 - Should support multiple different skeleton asset files per mod, but untested

### FAQ:
 - Q: What is in ExampleMod_P?
   - A: A Palworld mod that gives the pink cat sunglasses and a hat that bends. its low quality, but shows what this tool can do

 - Q: I get a long string of text that ends with "FileNotFoundError [errorno ..." and lists a directory
   - A: The program is looking for a file that it expects to exist, but can't find it. There are many possible reasons for this.
     1. Most likely it is an issue with your modconfig.json file containing files that you no longer want. To learn how to fix, goto the "Mod Config" section above.
     2. Alternatively, it could break if you change your mod name or move the entire folder somewhere else. Make sure your config.json and modconfig.json paths are correct.
 
- Q: How come the animations I patched in with the skeleton look wrong?
  - A: This mod should automatically fix animations added as long as the skeleton file they use is also cooked. if this is not the case,
  it's either your reimported your skeleton into unreal at some point, adding extra bones, or some unknown issue.
  if you reimported, this can be fixed by deleting the animation,skeleton,and mesh files and dragging in your .fbx file

- Q: If I have other questions/comments/concerns, how do I contact you?
  - A: Currently the best chance is on the Palworld Discord, look for the username Shifty