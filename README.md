# RenModder
An tool to patch and mod games that powerd by Ren'Py. This tool can patch games for:
- Mod support
- Dev Mode enable
If you are developer that want to mod som game or just want to add mod support for your favorite game, this tool for you !

***For now, project aim to add mod support for all platforms (like Windows, Linux and MacOS)***

# Installation
## Python3 install
First, you need to download python (3.7+) from [official website](https://python.org) or with your package manager:
### Arch Linux
`sudo pacman -S python3`
### Debian/Ubuntu-based
`sudo apt install python3`
### Windows
1. Go to website
2. Download installer
3. Run it
3.1. !! Check all !! (add to path, inc. path limit, etc)
4. Run install
### MacOS
First, you need to download [HomeBrew](https://brew.sh/), then open console and type:
`brew install python3`
## Patch your games
Download this repository and unzip it anywere (or run `git clone https://github.com/Lines115/RenModder.git` in console, if you have installed git).

Open console in unzipped folder and here you are. You can patch and unpatch like this:
### Enable Dev Mode
On Linux/MacOS:
`python3 main.py "PATH/TO/YOUR/GAME" dev patch`
On Windows:
`py main.py "C://PATH/TO/YOUR/GAME" dev patch`
### Disable Dev Mode
On Linux/MacOS:
`python3 main.py "PATH/TO/YOUR/GAME" dev unpatch`
On Windows:
`py main.py "C://PATH/TO/YOUR/GAME" dev unpatch`
### Add mod support
On Linux/MacOS:
`python3 main.py "PATH/TO/YOUR/GAME" mod patch`
On Windows:
`py main.py "C://PATH/TO/YOUR/GAME" mod patch`
### Delete mod support
On Linux/MacOS:
`python3 main.py "PATH/TO/YOUR/GAME" mod unpatch`
On Windows:
`py main.py "C://PATH/TO/YOUR/GAME" mod unpatch`
NOTE: Replace "PATH/TO/YOUR/GAME" and "C://PATH/TO/YOUR/GAME" with path to game that you want to patch !
# Help
If you want to help this project and you aren't Python developer, you can log in into your GitHub account and star this project

If you want to help this project and you are Python developer, you can create Pull Request and help with developing with project
# Thanks
Thanks lazy me that starts working for this project. 

Thanks for Tom Rothamel (AKA "PyTom") for creating Ren'Py !

# Tests
Tested on:
- Starry Flowers 1.7 (Windows+Linux+MacOS build, maybe) by NomNomNami
- Contract Demon 2.2.7 (Windows+Linux+MacOS build, maybe too) by NomNomNami
