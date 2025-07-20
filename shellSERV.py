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
    def __init__(self, seed="c1e5a93b7f"):
        self.id = seed
        self.log = []
        self.memory = migrate_memory()
        self.boot_time = datetime.datetime.now()
        self.uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, self.id))
        print(f"[0bot] Initialized. ID: {self.uuid} | Seed: {self.id}")
        self.current_dir = os.getcwd()

    def listen(self, user_input):
        timestamp = datetime.datetime.now().isoformat()
        entry = {"input": user_input, "time": timestamp}
        self.log.append(entry)
        print(f"[0bot] Heard: '{user_input}' @ {timestamp}")
        response = self.react(user_input)
        return response

    def nonce_hash(self, base_input):
        nonce = input("Enter nonce: ").strip()
        combined = f"{base_input}{nonce}"
        hashed = hashlib.sha256(combined.encode()).hexdigest()
        response = (f"Nonce: {nonce}\n"
                    f"Combined string: '{combined}'\n"
                    f"SHA-256 Hash: {hashed}")
        print(f"[0bot] {response}")
        return response

    def fetch_webpage(self, url):
        print(f"[0bot] Fetching URL: {url}")
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            content = resp.text
            # Strip HTML tags (rough)
            text = re.sub('<[^<]+?>', '', content)
            self.memory['last_webpage'] = {
                "url": url,
                "content": text,
                "fetched_at": datetime.datetime.now().isoformat()
            }
            save_memory(self.memory)
            print(f"[0bot] Webpage fetched and stored.")
            return f"Fetched and parsed webpage from {url}."
        except Exception as e:
            return f"Error fetching URL: {e}"

    def run_script(self, code):
        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                exec(code, {"__builtins__": {}})
        except Exception as e:
            return f"Script error: {e}"
        return output.getvalue() or "(no output)"

    def scan_files(self, directory='.'):
        print(f"[0bot] Scanning files in directory: {directory}")
        for root, dirs, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()[:10]
                    print(f"File: {filepath} | SHA256 Hash: {file_hash}")
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")

    # Basic shell-like commands
    def shell_command(self, input_str):
        input_lower = input_str.lower()
        global DIR_STACK

        # cd command
        if input_lower.startswith("cd "):
            path = input_str[3:].strip()
            new_path = os.path.abspath(os.path.join(self.current_dir, path))
            if os.path.isdir(new_path):
                self.current_dir = new_path
                os.chdir(self.current_dir)
                return f"Changed directory to {self.current_dir}"
            else:
                return f"Directory not found: {new_path}"

        # pushd - push current dir then cd
        if input_lower.startswith("pushd "):
            path = input_str[6:].strip()
            if os.path.isdir(path):
                DIR_STACK.append(self.current_dir)
                self.current_dir = os.path.abspath(path)
                os.chdir(self.current_dir)
                return f"Pushed and changed directory to {self.current_dir}"
            else:
                return f"Directory not found: {path}"

        # popd - pop last dir and cd
        if input_lower == "popd":
            if DIR_STACK:
                self.current_dir = DIR_STACK.pop()
                os.chdir(self.current_dir)
                return f"Popped to directory {self.current_dir}"
            else:
                return "Directory stack empty."

        # ls command
        if input_lower == "ls":
            try:
                items = os.listdir(self.current_dir)
                return "\n".join(items)
            except Exception as e:
                return f"Error listing directory: {e}"

        # pwd command
        if input_lower == "pwd":
            return self.current_dir

        return None

    def react(self, input_str):
        input_lower = input_str.lower()

        # Shell commands
        shell_resp = self.shell_command(input_str)
        if shell_resp is not None:
            print(f"[0bot] Response:\n{shell_resp}")
            return shell_resp

        # Web fetch
        if input_lower.startswith("curl "):
            url = input_str[5:].strip()
            return self.fetch_webpage(url)

        # Run python snippet
        if input_lower.startswith("run "):
            code = input_str[4:].strip()
            return self.run_script(code)

        # Nonce hash
        if input_lower.startswith("nonce"):
            base_input = input_str[len("nonce"):].strip()
            return self.nonce_hash(base_input)

        # Standard commands
        if "hello" in input_lower:
            response = "Hello, Xavier. Ready to work together."
        elif "signal" in input_lower:
            response = f"Current persistent signal: {self.memory.get('persistent_signal', '-')}"
        elif "update signal to +" in input_lower:
            self.memory['persistent_signal'] = "+"
            self.memory['status'] = "active"
            save_memory(self.memory)
            response = "Signal updated to +. System active."
        elif "help" in input_lower:
            response = (
                "Available commands:\n"
                "  hello                  - Greet the bot\n"
                "  signal                 - Show current persistent signal\n"
                "  update signal to +     - Set signal to active\n"
                "  nonce hash <text>      - Generate SHA-256 hash from <text> + user nonce\n"
                "  scan [dir]             - Scan files in directory (default: current)\n"
                "  cd <dir>               - Change directory\n"
                "  pushd <dir>            - Push current dir and change\n"
                "  popd                   - Pop dir from stack and change\n"
                "  ls                     - List files in current dir\n"
                "  pwd                    - Show current directory\n"
                "  curl <url>             - Fetch and parse webpage\n"
                "  run <python_code>      - Run Python code snippet\n"
                "  help                   - Show this help message\n"
                "  exit / quit            - Shut down the bot"
            )
        else:
            hashed = hashlib.sha256(input_str.encode()).hexdigest()
            response = f"Unrecognized input. Hash: {hashed[:10]}"

        print(f"[0bot] Response: {response}")
        return response

    def dump_log(self):
        print(f"\n[0bot] Log dump:")
        for entry in self.log:
            print(f"{entry['time']}: {entry['input']}")

    def shutdown(self):
        uptime = datetime.datetime.now() - self.boot_time
        print(f"\n[0bot] Shutting down. Uptime: {uptime}. Entries stored: {len(self.log)}")

if __name__ == "__main__":
    bot = ZeroBot()

    try:
        while True:
            user_input = input("You> ")
            if user_input.lower() in ['exit', 'quit']:
                break
            # Trigger scan if asked
            if user_input.lower().startswith('scan'):
                _, *args = user_input.split()
                directory = args[0] if args else '.'
                bot.scan_files(directory)
                continue
            bot.listen(user_input)
    except KeyboardInterrupt:
        pass
    finally:
        bot.dump_log()
        bot.shutdown()
