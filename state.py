import json
import tkinter as tk
from pathlib import Path

CONFIG = Path(__file__).parent / "config.json"
print("Config path:", CONFIG)

modpack_zip = None
instance_old = None

migrateOptional = None
addAddons = None
migrateAddons = None
addResourcePacks = None


def init_vars():
    global migrateOptional, addAddons, migrateAddons, addResourcePacks
    migrateOptional = tk.BooleanVar(value=False)
    addAddons = tk.BooleanVar(value=False)
    migrateAddons = tk.BooleanVar(value=False)
    addResourcePacks = tk.BooleanVar(value=False)

def load():
    global modpack_zip, instance_old
    if not CONFIG.exists():
        return
    try:
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        print("WARN | config.json is empty or corrupted, ignoring it")
        return

    zip_path = Path(data["modpack_zip"]) if data.get("modpack_zip") else None
    inst_path = Path(data["instance_old"]) if data.get("instance_old") else None
    modpack_zip = zip_path if zip_path and zip_path.exists() else None
    instance_old = inst_path if inst_path and inst_path.exists() else None

    migrateOptional.set(bool(data.get("migrateOptional", False)))
    addAddons.set(bool(data.get("addAddons", False)))
    migrateAddons.set(bool(data.get("migrateAddons", False)))
    addResourcePacks.set(bool(data.get("addResourcePacks", False)))


def save():
    CONFIG.write_text(json.dumps({
        "modpack_zip": str(modpack_zip) if modpack_zip else None,
        "instance_old": str(instance_old) if instance_old else None,
        "migrateOptional": migrateOptional.get(),
        "addAddons": addAddons.get(),
        "migrateAddons": migrateAddons.get(),
        "addResourcePacks": addResourcePacks.get(),
    }, indent=2), encoding="utf-8")