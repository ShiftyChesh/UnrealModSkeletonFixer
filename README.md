# Unreal Mod Skeleton Fixer & Mod Auto-builder
This project aims to fix modded skeleton .uasset files cooked in Unreal Engine 5 (UE5)
so that they can be added into a mod without breaking the original animations for the unmodded skeleton.
Basically, if you've seen a tutorial for unreal modding where they say "make sure to remove the skeleton asset after cooking", this tool fixes that.
Originally made for Palworld, it currently has not been tested on other games.
Please open Issues if you have any problems using this tool.

if you want to understand the technical side of what this tool does, check out the file "pythonfiles/Unreal Skeletons Technical Stuff.txt" 
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
the config.json file must be edited for most features to work.
The config json fields do the following:
- "autopack_mods" : bool - If true, automatically creates .pak files of mods in the 'mods' folder/ Requires "packer_path" to be valid
- "packer_path" : string - Path to the UnrealPak.exe file for building .pak files. Only needs a valid path if "autopack_mods" is true
- "bone_fix" : bool - If true, any skeleton uassets will be fixed based on the source mappings found in the 'mapping' folder (see section: ### Mapping Setup)
- "mods_p_path" : string - Path to your mods folder for patch mods. This is the unreal mods in the paks directory. For Palworld it's the: /Pal/Content/Paks/~mods folder
- "move_all_mods" : bool - If true, copies all built mods into the "mods_p_path" directory
- moveover_mod_list : string[] - Lists mods you want to automatically move to "mods_p_path" is "move_all_mods" is false. Good if you only want to move/test some of your mods.

### Mapping Setup
In order for the bone remapping to work, you need to make sure you have the ORIGINAL skeleton uasset files from the game you are trying to mod. 
They can be exported as raw uasset data by [FModel](https://fmodel.app/).
those ORIGINAL files should be placed in the mappings folder then in a folder with the same name as the mod containing the skeleton uasset you wish to fix. This can be seen in the included ExampleMod_P mod

### How To Use:
Double-click on the "ModBuilder.bat" file, and it will work automatically if the config setup steps have been completed.

### Limitations
 - Currently only tested skeletons with nearly the same amount of bones as the original. Haven't tested other cases
 - Doesn't support animations (yet)
 - Can't add new bones in for custom skeletons (yet)

### FAQ:
 - Q: What is in ExampleMod_P?
   - A: A Palworld mod that gives Penking 3 hats instead of 1. Also, intentionally messes up his beak.
   (Future version of this mod will hopefully include an easier to find Pal to verify the mod's successful patching & bone fixing)
 
 - Q: Does this work if I have extra bones on the skeleton not found on the original?
   - A: yes & no. currently the mod does not support adding extra bones and those bones will be truncated/removed when fixing the skeleton.
   This is currently being worked on as a feature
 
- Q: How come the animations I patched in with the skeleton look wrong?
  - A: Fixing the mod skeleton breaks the animations that use it for the same reason that it fixes the skeleton for use on the original animations.
  The feature to also fix custom animations linked to the skeleton is currently in progress
  (this also means adding custom animations without patching the skeleton in the future)
- Q: If I have other questions/comments/concerns, how do I contact you?
  - A: Currently the best chance is on the Palworld Discord, look for the username Shifty