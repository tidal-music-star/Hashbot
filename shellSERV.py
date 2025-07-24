import uuid
import datetime
import hashlib
import os
import json
import requests
import re
import io
import contextlib

MEMORY_FILE = "memory.json"
BOT_IDENTITY_FILE = "cipher.json"
OLD_MEMORY_FILE = r"\New Folder\memory.json"

# For shell dir navigation stack
DIR_STACK = []

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'w') as f:
            json.dump({"persistent_signal": "-", "status": "inactive", "log": []}, f, indent=2)
    with open(MEMORY_FILE, 'r') as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=2)

def load_json_file(filepath, default=None):
    if not os.path.exists(filepath):
        return default
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"[0bot] Warning: {filepath} corrupted. Resetting.")
        return default

def save_json_file(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def migrate_memory():
    if os.path.exists(MEMORY_FILE):
        mem = load_json_file(MEMORY_FILE, default=None)
        if mem:
            return mem
        else:
            print("[0bot] Memory corrupted; resetting.")
            os.rename(MEMORY_FILE, MEMORY_FILE + ".bak_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    if os.path.exists(OLD_MEMORY_FILE):
        print("[0bot] Found old memory file. Migrating...")
        old_mem = load_json_file(OLD_MEMORY_FILE, default=None)
        if old_mem:
            new_mem = {
                "persistent_signal": old_mem.get("signal", "-"),
                "status": old_mem.get("state", "inactive"),
                "log": old_mem.get("log", [])
            }
            save_json_file(MEMORY_FILE, new_mem)
            print("[0bot] Migration complete.")
            return new_mem
        else:
            print("[0bot] Old memory corrupted; skipping migration.")
    default_mem = {"persistent_signal": "-", "status": "inactive", "log": []}
    save_json_file(MEMORY_FILE, default_mem)
    return default_mem

class ZeroBot:
    
