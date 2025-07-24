ShellSERV.py

Overview

ShellSERV.py is an interactive shell-based bot, named ZeroBot, designed to emulate a hybrid between a virtual assistant and a lightweight shell interface. It offers persistent memory storage, web scraping, directory navigation, Python code execution, hashing with nonce support, and file scanning features. This bot is equipped with a pseudo-shell interface and reactive command processing.

Features

✅ Persistent memory tracking via memory.json

🔁 Automatic memory migration from older files (New Folder\memory.json)

🌐 Webpage content fetching and HTML stripping

🧠 Logging and timestamped memory for each session interaction

🔐 SHA-256 hash generation using nonce input

📂 File scanning with hash previews

🧮 Mini shell command set (e.g. cd, pwd, ls, pushd, popd)

🧪 On-the-fly execution of Python code

Directory Structure

.
├── ShellSERV.py            # Main executable
├── memory.json             # Bot's memory storage
├── cipher.json             # Identity configuration (optional)
└── \New Folder\memory.json # Legacy memory file (optional)

Installation

Dependencies

pip install requests

You may also optionally install pyttsx3 if using speech features via shelltalk.py.

Running the Bot

python ShellSERV.py

Once running, interact with the bot via terminal input. Available commands include:

hello - Basic greeting.

signal - Display current signal state.

update signal to + - Set bot to active mode.

nonce <text> - Generate SHA256 hash from <text> and user-provided nonce.

curl <url> - Fetch and parse webpage text.

run <python_code> - Run a Python snippet in a safe scope.

cd <path> - Change working directory.

pushd <path> - Push and change directory.

popd - Revert to last directory.

ls, pwd - Directory listing and path echo.

scan - Recursively hash all files in directory.

Memory Persistence

The bot reads and writes from memory.json, logging every interaction with timestamp. If corrupted or missing, it falls back to legacy paths or resets.

Logging Example

{
  "persistent_signal": "-",
  "status": "inactive",
  "log": [
    {
      "input": "hello",
      "time": "2025-07-19T17:25:33.481Z"
    }
  ]
}

Notes

Directory stack (pushd, popd) is volatile and does not persist.

exec() code is sandboxed with no built-ins to limit abuse.

The memory log can be used for training, analysis, or replaying session behavior.

To-Do



Author

Xavier / iXavier (PLAN STAR)
