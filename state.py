import json
import tkinter as tk
from pathlib import Path

CONFIG = Path(__file__).parent / "config.json"
print("Config path:", CONFIG)

modpack_zip = None
instance_old = None
addons_path = None
resourcepacks_path = None

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


def _to_path(value):
    if not value:
        return None
    path = Path(value)
    return path if path.exists() else None


def load():
    global modpack_zip, instance_old, addons_path, resourcepacks_path
    if not CONFIG.exists():
        return
    try:
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        print("WARN | config.json is empty or corrupted, ignoring it")
        return

    modpack_zip = _to_path(data.get("modpack_zip"))
    instance_old = _to_path(data.get("instance_old"))
    addons_path = _to_path(data.get("addons_path"))
    resourcepacks_path = _to_path(data.get("resourcepacks_path"))

    migrateOptional.set(bool(data.get("migrateOptional", False)))
    addAddons.set(bool(data.get("addAddons", False)))
    migrateAddons.set(bool(data.get("migrateAddons", False)))
    addResourcePacks.set(bool(data.get("addResourcePacks", False)))


def save():
    CONFIG.write_text(json.dumps({
        "modpack_zip": str(modpack_zip) if modpack_zip else None,
        "instance_old": str(instance_old) if instance_old else None,
        "addons_path": str(addons_path) if addons_path else None,
        "resourcepacks_path": str(resourcepacks_path) if resourcepacks_path else None,
        "migrateOptional": migrateOptional.get(),
        "addAddons": addAddons.get(),
        "migrateAddons": migrateAddons.get(),
        "addResourcePacks": addResourcePacks.get(),
    }, indent=2), encoding="utf-8")