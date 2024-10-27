# RenModder
<div style="display: flex; align-items: flex-start; text-align: left; margin-top: 0;">
  <img src="https://github.com/Lines25/RenModder/blob/main/patches/__mod_patch_renmodder/modder/logo.png?raw=True" alt="RenModder Logo" width="150">
  <div style="flex: 1;">
    <p><strong>RenModder</strong> is a tool for modding and patching Ren'Py games. Features include:</p>
    <ul>
      <li>🛠️ Mod support</li>
      <li>👨‍💻 Developer Mode enablement</li>
    </ul>
    <p>Whether you're a developer or a fan, RenModder makes modding simple! 🌈</p>
    <p>Current developers: <strong>Lines</strong></p>
  </div>
</div>

> ***RenModder v1.4 Jelly done percent: 15%***

| Description | Status |
| :-----------: | :------: |
| More Mod API functions | NS |
| Mod manager menu | C |
| Run mods in sandbox | NS |
| More control of game | NS |

> **Tip: NS - Not Started. W - Working. C - Canceled**

## 🎉 Features 🎉
- **🔧 First universal mod loader for Ren'Py-based games based on Python and hooking**
- **🌟 Powerful and easy for developers to create mods**
- **🚀 Super fast (~3.5 sec without vs ~3.3 sec with RenModder v1.3)**
- **📝 Adds more logging for developers**
- **👌 Easy to use and integrate**
- **💻 Supports all PC OSes (Windows 7+, MacOS, Linux)**

## Installation
### Python3
First, download Python (3.7+) from the [official website](https://python.org) or using your package manager:

- **Arch Linux:** `sudo pacman -S python3` 🐧
- **Debian-based (like Ubuntu):** `sudo apt install python3` 🐢
- **Windows:** Download and install from the [official website](https://python.org). Be sure to check all options (add to path, inc. path limit, etc). 🖥️
- **MacOS:** Install [HomeBrew](https://brew.sh/), then run: `brew install python3` 🍏

## Patching Games
Download this repository or run `git clone https://github.com/Lines115/RenModder.git` in your terminal. 📦

Open a terminal in the unzipped folder, and you're ready to patch or unpatch with the following commands:

### Enable Developer Mode
- **Linux/MacOS:** `python3 main.py "PATH/TO/YOUR/GAME" dev patch`
- **Windows:** `py main.py "C://PATH/TO/YOUR/GAME" dev patch`

### Disable Developer Mode
- **Linux/MacOS:** `python3 main.py "PATH/TO/YOUR/GAME" dev unpatch`
- **Windows:** `py main.py "C://PATH/TO/YOUR/GAME" dev unpatch`

### Add Mod Support
- **Linux/MacOS:** `python3 main.py "PATH/TO/YOUR/GAME" mod patch`
- **Windows:** `py main.py "C://PATH/TO/YOUR/GAME" mod patch`

### Remove Mod Support
- **Linux/MacOS:** `python3 main.py "PATH/TO/YOUR/GAME" mod unpatch`
- **Windows:** `py main.py "C://PATH/TO/YOUR/GAME" mod unpatch`

> **Note:** Replace `"PATH/TO/YOUR/GAME"` with the actual path to the game you want to patch. 🗂️

## Configure RenModder

You can configure RenModder by opening `PATCH_TO_YOUR_GAME/renpy/renmodder/config.py` with a notepad and write something

> **Note:** This is python file. You have to write something in python syntax !! (True, False, "text", 'text', ...)
- **VERBOSE_LOG** - Print in console text, that may make from console a trash bin (Default: `False` and in **dev** branch: `True`)
- **ENABLE_MAIN_MENU** - If set to `False` then game will skip main menu and just run all game (Default: `True`)
- **SKIP_SPLASH** - Don't draw splash (in most cases it's just author's nickname that made the entire game) at start (Default: `True`)

## Contributing
- **Not a developer?** You can support the project by starring it ⭐
- **Developer?** Feel free to contribute via Pull Requests or write me at discord: lines8810 🤝

## Making Mods
Check out [DEVELOPERMENT.md](DEVELOPERMENT.md) for modding guidelines 📚

## Popular errors
**Error: Game just don't start**

**Answer: Wait like an 10-20secs and run again**

For devs: Maybe, this is just a broken pipe error when one of mods tries to register in RenModder Mod API system and fails, just have to wait when games closes and run it again

**Error: Game take so long to load**

**Answer: You it's your first load after patching - it's normal, other loads after this will be faster**

For devs: Mod patch delets all .rpyc files, cuz if don't delete it, game will crash, cuz it loads RM_start.rpy and other .rpyc files and it may conflict, if don't delete it


## Acknowledgements
Thanks to my lazy self for starting this project and special thanks to **Tom Rothamel** (PyTom) for creating Ren'Py! 🙌

## Changelog 📜
**v1.3 Fish (Current)**: Major update 🚀
- Added:
  - Mod API server and client
  - Mod API server token-based auth
  - Blank event subscribe function
  - `wait_for_mod()` function in `mod_api.py`
  - Mod API server now shutting down at the end of the program before exit
  - Custom `00start.rpy` file in `renpy/common/`
  - Mod Patcher now clears all .rpyc files (Make fisrt run slower, but not compatible error corrupts)

- Replaced: 
  - "[RENMODDER] RENMODDER" with "[RENMODDER]" in all log functions 🔄


## Tested Games
| Game             | Version | Platforms             | Author        |
| :--------------- | :-----: | :-------------------: | :-----------: |
| Starry Flowers   | 1.7     | Windows, Linux, MacOS | NomNomNami    |
| Contract Demon   | 2.2.7   | Windows, Linux, MacOS | NomNomNami    |
