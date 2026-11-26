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
Addons = Path(
    r"C:\Users\Mishanya\OneDrive\Робочий стіл\Датабаза Леваса\Games\Minecraft\mods\GTNH Addons"
)
ResourcePacks = Path(
    r"C:\Users\Mishanya\OneDrive\Робочий стіл\Датабаза Леваса\Games\Minecraft\resourcepacks\GTNH"
)

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

def close_window():
    state.save()
    root.destroy()

# tkinter UI
root = tk.Tk()
state.init_vars()
state.load()

tk.Button(root, text="Pick zip", command=pick_zip).pack()
tk.Button(root, text="Pick Instance", command=pick_instance).pack()

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

Addons_List = []
for jar in Addons.glob("*.jar"):
    Addons_List.append(jar.name)

ResourcePacks_List = []
for z in ResourcePacks.glob("*.zip"):
    ResourcePacks_List.append(z.name)

print("\nMigration | Migrating Main Files")
migrate(Migration_List)
if state.migrateOptional.get():
    print("Migration | Migrating Optional Files")
    migrate(Migration_Optional)

if state.addAddons.get():
    print("Migration | Adding Addons")
    for jar in Addons_List:
        source = Addons/jar
        destination = instances/root_folder/".minecraft"/"mods"/jar
        shutil.copy2(source, destination)

    if state.migrateAddons.get():
        print("Migration | Migrating Addons")
        migrate(Migration_Addons)

if state.addResourcePacks.get():
    print("Migration | Migrating Resource Packs")
    for z in ResourcePacks_List:
        source = ResourcePacks / z
        destination = instances / root_folder / ".minecraft" / "resourcepacks" / z
        shutil.copy2(source, destination)

print("Migration | Migration Finished")