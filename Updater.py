from pathlib import Path
import zipfile
import os
import shutil
import tkinter as tk
from tkinter import filedialog
import state

# Preparations
AppData = Path(str(os.getenv("APPDATA")))
print("AppData located:", AppData.exists())
instances = AppData/"PrismLauncher"/"instances"

# Functions
def migrate(mig):
    not_found = []
    skipped = []

    def copy_if_missing(src, dst):
        if Path(dst).exists():
            skipped.append(Path(dst).relative_to(instances/root_folder/".minecraft"))
            return dst
        return shutil.copy2(src, dst)

    for file in mig:
        src = instance_old/".minecraft"/file
        dst = instances/root_folder/".minecraft"/file

        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True, copy_function=copy_if_missing)
        elif src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            copy_if_missing(src, dst)
        else:
            not_found.append(file)

    if skipped:
        print(f"INFO | Skipped {len(skipped)} item(s) that already exist")
    if not_found:
        print("INFO | Missing Files:\n", not_found)

def pick_zip():
    path = filedialog.askopenfilename()
    if path:
        state.modpack_zip = Path(path)
        print("Modpack State:", state.modpack_zip)

def pick_instance():
    path = filedialog.askdirectory(initialdir=instances, title="Select Instance")
    if path:
        state.instance_old = Path(path)
        print("Instance State:", state.instance_old)

def pick_addons():
    path = filedialog.askdirectory(title="Select Addons folder")
    if path:
        state.addons_path = Path(path)
        state.save()
        print("Addons State:", state.addons_path)

def pick_resourcepacks():
    path = filedialog.askdirectory(title="Select Resource Packs folder")
    if path:
        state.resourcepacks_path = Path(path)
        state.save()
        print("ResourcePacks State:", state.resourcepacks_path)

def close_window():
    state.save()
    root.destroy()

# tkinter UI
root = tk.Tk()
state.init_vars()
state.load()

tk.Button(root, text="Pick zip", command=pick_zip).pack()
tk.Button(root, text="Pick Instance", command=pick_instance).pack()
tk.Button(root, text="Pick Addons", command=pick_addons).pack()
tk.Button(root, text="Pick Resource Packs", command=pick_resourcepacks).pack()

tk.Checkbutton(root, text="Migrate optional files", variable=state.migrateOptional).pack()
tk.Checkbutton(root, text="Add addons", variable=state.addAddons).pack()
tk.Checkbutton(root, text="Migrate addons", variable=state.migrateAddons).pack()
tk.Checkbutton(root, text="Add resource packs", variable=state.addResourcePacks).pack()

tk.Button(root, text="Run", command=close_window).pack()
root.mainloop()
state.save()

# Extraction
modpack_zip = state.modpack_zip
instance_old = state.instance_old
with zipfile.ZipFile(modpack_zip) as z:
    root_folder = z.namelist()[0].split("/")[0]

print("\nInstances | Exists:", instances.exists(), "\n"
      "Instances | Is a directory:", instances.is_dir(), "\n"
      "\nZIP | Exists:", modpack_zip.exists(), "\n"
      "ZIP | Root name:", root_folder)

if not (instances/root_folder/".minecraft").exists():
    print("\nExtraction: Extraction in progress")
    with zipfile.ZipFile(modpack_zip) as z:
        z.extractall(instances)
    print("Extraction: Extraction successful")
else:
    print(f"\nExtraction: Folder with the name '{root_folder}' already exists")

# Migration
Migration_List = [
    "backups",
    "config",
    "config/vendingmachine/favourites",
    "config/shaders.properties",
    "ESM",
    "journeymap",
    "resourcepacks",
    "saves",
    "schematics",
    "screenshots",
    "shaderpacks",
    "TCNodeTracker",
    "visualprospecting",
    "BotaniaVars.dat",
    "localconfig.cfg",
    "options.txt",
    "optionsnf.txt",
    "servers.dat"
]
Migration_Optional = [
    "config/InGameInfoXML",
    "config/GregTech/Pollution.cfg",
    "config/txloader/load/minecraft/sounds.json",
    "config/gtnhintergalactic.cfg",
    "config/lwjgl3ify.cfg",
    "config/tectech.cfg",
    "config/TinkersConstruct.cfg",
    "serverutilities"
]
Migration_Addons = [
    "wayfarmap"
]

print("\nMigration | Migrating Main Files")
migrate(Migration_List)

if state.migrateOptional.get():
    print("Migration | Migrating Optional Files")
    migrate(Migration_Optional)

if state.addAddons.get():
    if not state.addons_path:
        print("WARN | Addons folder not selected, skipping addons")
    else:
        print("Migration | Adding Addons")
        for jar in state.addons_path.glob("*.jar"):
            destination = instances/root_folder/".minecraft"/"mods"/jar.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(jar, destination)

        if state.migrateAddons.get():
            print("Migration | Migrating Addons")
            migrate(Migration_Addons)

if state.addResourcePacks.get():
    if not state.resourcepacks_path:
        print("WARN | Resource Packs folder not selected, skipping resource packs")
    else:
        print("Migration | Adding Resource Packs")
        for pack in state.resourcepacks_path.glob("*.zip"):
            destination = instances/root_folder/".minecraft"/"resourcepacks"/pack.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pack, destination)

print("Migration | Migration Finished")