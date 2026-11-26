from pathlib import Path
import zipfile
import os
import shutil
import tkinter as tk
from tkinter import filedialog
import state
import filecmp
import logging

# Logs
LOG_FILE = Path(__file__).parent / "updater.log"

logging.basicConfig(
    filename=LOG_FILE,
    filemode="w",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# Preparations
AppData = Path(str(os.getenv("APPDATA")))
log.info("AppData located: %s", AppData.exists())
instances = AppData/"PrismLauncher"/"instances"

# Functions
def migrate(mig):
    not_found = []
    skipped = []

    def copy_if_missing(src, dst):
        if Path(dst).exists():
            skipped.append(Path(dst).relative_to(mc))
            return dst
        return shutil.copy2(src, dst)

    for file in mig:
        src = old_mc/file
        dst = mc/file

        try:
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True, copy_function=copy_if_missing)
            elif src.is_file():
                dst.parent.mkdir(parents=True, exist_ok=True)
                copy_if_missing(src, dst)
            else:
                not_found.append(file)
        except Exception:
            log.exception("Failed to migrate %s", file)

    if skipped:
        log.info("Skipped %d item(s) that already exist", len(skipped))
    if not_found:
        log.warning("Missing files: %s", not_found)

def copy_files(source_dir, pattern, dest_dir, label):
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        log.exception("Failed to create destination directory: %s", dest_dir)
        return

    copied = unchanged = 0

    for file in source_dir.glob(pattern):
        dest = dest_dir / file.name
        try:
            if dest.exists() and filecmp.cmp(file, dest, shallow=True):
                unchanged += 1
                continue
            shutil.copy2(file, dest)
            copied += 1
        except Exception:
            log.exception("Failed to copy %s to %s", file, dest)

    log.info("Migration | %s: %d copied, %d already up to date", label, copied, unchanged)

def pick_zip():
    path = filedialog.askopenfilename()
    if path:
        state.modpack_zip = Path(path)
        log.info("Modpack State: %s", state.modpack_zip)

def pick_instance():
    path = filedialog.askdirectory(initialdir=instances, title="Select Instance")
    if path:
        state.instance_old = Path(path)
        log.info("Instance State: %s", state.instance_old)

def pick_addons():
    path = filedialog.askdirectory(title="Select Addons folder")
    if path:
        state.addons_path = Path(path)
        state.save()
        log.info("Addons State: %s", state.addons_path)

def pick_resourcepacks():
    path = filedialog.askdirectory(title="Select Resource Packs folder")
    if path:
        state.resourcepacks_path = Path(path)
        state.save()
        log.info("ResourcePacks State: %s", state.resourcepacks_path)

def close_window():
    state.save()
    root.destroy()

def cancel():
    state.save()
    raise SystemExit

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
root.protocol("WM_DELETE_WINDOW", cancel)
root.mainloop()
state.save()

# Extraction
modpack_zip = state.modpack_zip
instance_old = state.instance_old

problems = []
if not modpack_zip:
    problems.append("Modpack zip not selected")
if not instance_old:
    problems.append("Old instance not selected")
if state.addAddons.get() and not state.addons_path:
    problems.append("'Add addons' is ticked but no Addons folder is selected")
if state.addResourcePacks.get() and not state.resourcepacks_path:
    problems.append("'Add resource packs' is ticked but no Resource Packs folder is selected")

if problems:
    message = "\n".join(problems)
    log.error("Validation failed: %s", message)
    raise SystemExit(message)

try:
    with zipfile.ZipFile(modpack_zip) as z:
        namelist = z.namelist()
        if not namelist:
            raise ValueError("Modpack ZIP contains no files")
        root_folder = namelist[0].split("/")[0]
except Exception:
    log.exception("Failed to read modpack ZIP: %s", modpack_zip)
    raise

mc = instances/root_folder/".minecraft"
old_mc = instance_old/".minecraft"

log.info("Instances | Exists: %s", instances.exists())
log.info("Instances | Is a directory: %s", instances.is_dir())
log.info("ZIP | Exists: %s", modpack_zip.exists())
log.info("ZIP | Root name: %s", root_folder)

if not (instances/root_folder/".minecraft").exists():
    log.info("Extraction: Extraction in progress")
    try:
        with zipfile.ZipFile(modpack_zip) as z:
            z.extractall(instances)
    except Exception:
        log.exception("Extraction failed")
        raise
    log.info("Extraction: Extraction successful")
else:
    log.warning("Extraction: Folder with the name '%s' already exists", root_folder)

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

log.info("Migration | Migrating Main Files")
migrate(Migration_List)

if state.migrateOptional.get():
    log.info("Migration | Migrating Optional Files")
    migrate(Migration_Optional)

if state.addAddons.get():
    log.info("Migration | Adding Addons")
    copy_files(state.addons_path, "*.jar", mc/"mods", "Addons")

if state.migrateAddons.get():
    log.info("Migration | Migrating Addons")
    migrate(Migration_Addons)

if state.addResourcePacks.get():
    log.info("Migration | Adding Resource Packs")
    copy_files(state.resourcepacks_path, "*.zip", mc/"resourcepacks", "Resource Packs")

log.info("Migration | Migration Finished")