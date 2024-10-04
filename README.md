# RenModder
<div style="display: flex; align-items: center;">
  <div style="flex: 1;">
    <p><strong>RenModder</strong> is a tool for modding and patching Ren'Py games. Features include:</p>
    <ul>
      <li>Mod support</li>
      <li>Developer Mode enablement</li>
    </ul>
    <p>Whether you're a developer or a fan, RenModder makes modding simple!</p>
    <p><strong>Current goal:</strong> Add mod support across all platforms (Windows, Linux, MacOS).</p>
  </div>
  <div>
    <img src="https://github.com/Lines25/RenModder/blob/main/patches/__mod_patch_renmodder/modder/logo.png?raw=True" alt="RenModder Logo" width="150">
  </div>
</div>


Whether you're a developer wanting to mod a game or just looking to add mod support to your favorite game, this tool is for you!

***Current project goal: add mod support across all platforms (Windows, Linux, MacOS).***

## Installation
### Python3
First, download Python (3.7+) from the [official website](https://python.org) or using your package manager:

- **Arch Linux:** `sudo pacman -S python3`
- **Debian/Ubuntu/Kali:** `sudo apt install python3`
- **Windows:** Download and install from the [official website](https://python.org). Be sure to check all options (add to path, inc. path limit, etc).
- **MacOS:** Install [HomeBrew](https://brew.sh/), then run: `brew install python3`

## Patching Games
Download this repository or run `git clone https://github.com/Lines115/RenModder.git` in your terminal.

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

> **Note:** Replace `"PATH/TO/YOUR/GAME"` with the actual path to the game you want to patch.

## Contributing
- **Not a developer?** You can support the project by starring it on GitHub.
- **Developer?** Feel free to contribute via Pull Requests.

## Making Mods
Check out [DEVELOPERMENT.md](DEVELOPERMENT.md) for modding guidelines.

## Acknowledgements
Thanks to my lazy self for starting this project and special thanks to **Tom Rothamel** (PyTom) for creating Ren'Py!

## Tested Games
| Game             | Version | Platforms             | Author        |
| :--------------- | :-----: | :-------------------: | :-----------: |
| Starry Flowers    | 1.7     | Windows, Linux, MacOS | NomNomNami    |
| Contract Demon    | 2.2.7   | Windows, Linux, MacOS | NomNomNami    |
