from shutil import rmtree, copytree, move, copy, unpack_archive
from os import listdir, remove, walk, path, makedirs, environ
from sys import argv, path as sys_path
from threading import Thread
import urllib.request
import zipfile

PATCH_IDETEFICATOR = 0x8000 | 0xABC  # DON'T CHANGE IT. IF YOU CHANGE THIS YOU CAN'T UNPATCH. ONLY BY HANDS
PATCH_VERSION = 0.1

TITLE_ORIGINAL = "        config.window_title = config.name or \"A Ren'Py Game\""
TITLE_PATCHED = f"#{TITLE_ORIGINAL}\n        config.window_title = config.name+\" (PATCHED WITH RENMODDER v{PATCH_VERSION})\" or \"A Ren'Py Game (PATCHED WITH RENMODDER v{PATCH_VERSION})\" #{PATCH_IDETEFICATOR} RENMODDER MOD PATCH"

BOOTSTRAP_ORIGINAL = "def bootstrap(renpy_base):\n\n    global renpy"
BOOTSTRAP_PATCHED = \
"""def bootstrap(renpy_base, real_one=False):

    #{PATCH_IDETEFICATOR} RENMODDER MOD PATCH
    # global renpy
    if not real_one:
        global l
        print("[RENMODDER] RENMODDER BOOTSTRAPING: GLOBALING", end=' ')
        for l in sys.modules.keys():
            if not '.' in l:
                print(f"{l},", end=' ')
                exec(f'global {l}')

        print('\\n[RENMODDER] RENMODDER BOOTSTRAPING: LOADING RENMODDER MODULE')
        import renpy.renmodder
        renpy.renmodder.bootstrap.run(renpy_base)
        return
    else:
        print("[RENMODDER] RENMODDER BOOTSTRAPING: STARTING ORIGINAL REN'PY BOOTSTRAPING...")
    #{PATCH_IDETEFICATOR} RENMODDER MOD PATCH
    """.replace("{PATCH_IDETEFICATOR}", str(PATCH_IDETEFICATOR))

INIT_ORIGINAL = """for m in sys.modules.values():
            if m is None:
                continue

            self.backup_module(m)"""
INIT_PATCHED = f"""for m in sys.modules.values():
            if m is None:
                continue

            if not list(sys.modules.keys())[list(sys.modules.values()).index(m)].startswith('renpy.renmodder'): # {PATCH_IDETEFICATOR} RENMODDER MOD PATCH
                self.backup_module(m)""" 

DEV_TEST_MOD = """
# import renpy.renmodder.mod_api as mod_api


class TestMod(Mod):
    def __mod_log(self, text: str):
        print(f"[{self.name}] {text}")

    def __init__(self) -> None:
        self.id = id(self)
        self.name = "DME"
        self.version = 1.0

    def bootstrap(self): pass
    def bootstrap_end(self): pass
    def main(self): pass

    def main_end(self):
        global renpy
        
        self.__mod_log("Loading dev mode...")
        renpy.config.developer = True
        renpy.config.default_developer = True

    def unload(self):
        global renpy
        self.__mod_log("Disabling dev mode...")
        renpy.config.developer = False
        renpy.config.default_developer = False
"""

lib = '/renpy/common/00library.rpy'
bootstrap = '/renpy/bootstrap.py'
renmodder = '/renpy/renmodder'
init = "/renpy/__init__.py"

MOD_PATCH_LOG_FILE = 'MOD_PATCH.log'

MODDER_RESOURCES = "modder_resources"
LIBRARIES_DIR = path.join(MODDER_RESOURCES, "libraries")

def log(text: str, end: str = "\n", print_data: bool = True, print_log: bool = True):
    if print_data:
        if print_log:
            print(f"[LOG] {text}", end=end, flush=True)
        else:
            print(text, end=end, flush=True)
    with open(MOD_PATCH_LOG_FILE, "a") as log_file:
        log_file.write(f"{text}{end}")

def install_library(lib_name: str, lib_info: dict, target_dir: str):
    lib_path = path.join(target_dir, lib_name)

    if path.exists(lib_path):
        log(f"($) {lib_name} already exists, skipping installation")
        return True

    try:
        if lib_info['method'] == 'source':
            log(f"(*) Installing {lib_name} from source...")
            url = lib_info['url']
            source_path = lib_info['source_path']
            zip_path = path.join(target_dir, f"{lib_name}_temp.zip")

            # Download
            urllib.request.urlretrieve(url, zip_path)

            # Extract
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if file.startswith(source_path + '/') and not file.endswith('/'):
                        dest_path = path.join(target_dir, lib_name, path.relpath(file, source_path))
                        makedirs(path.dirname(dest_path), exist_ok=True)
                        with open(dest_path, 'wb') as f:
                            f.write(zip_ref.read(file))
            # Cleanup
            remove(zip_path)

        elif lib_info['method'] == 'wheel':
            log(f"(*) Installing {lib_name} from wheel...")
            url = lib_info['url']
            wheel_path = path.join(target_dir, f"{lib_name}.whl")

            # Download
            urllib.request.urlretrieve(url, wheel_path)

            # Extract
            unpack_archive(wheel_path, path.join(target_dir, lib_name))
            remove(wheel_path)

        log(f"(+) {lib_name} installed successfully")
        return True
    except Exception as e:
        log(f"(-) Failed to install {lib_name}: {str(e)}")
        return False

def setup_libraries(game_path: str):
    target_dir = path.abspath(path.join(game_path, LIBRARIES_DIR))
    makedirs(target_dir, exist_ok=True)

    libraries = {
        'tkinter': {
            'method': 'source',
            'url': 'https://github.com/python/cpython/archive/refs/tags/v3.9.13.zip',
            'source_path': 'cpython-3.9.13/Lib/tkinter'
        }
    }

    for lib_name, lib_info in libraries.items():
        install_library(lib_name, lib_info, target_dir)

    lib_path = path.abspath(target_dir)
    if lib_path not in sys_path:
        sys_path.insert(0, lib_path)

    pythonpath = environ.get('PYTHONPATH', '')
    if lib_path not in pythonpath.split(path.pathsep):
        environ['PYTHONPATH'] = path.pathsep.join([lib_path, pythonpath])

def reset_log():
    with open(MOD_PATCH_LOG_FILE, 'w') as log_file:
        log_file.write('')

def patch(found: str, replace: str, file: str) -> bool:
    with open(file, 'r', encoding='utf-8') as patching:
        content = patching.read()

    patched = content.replace(found, replace)

    if content == patched:
        return False

    with open(file, 'w', encoding='utf-8') as write:
        write.write(patched)
    return True

def unpatch(found: str, replace: str, file: str) -> bool:
    return patch(found, replace, file)

def check_patched(file: str) -> bool:
    with open(file, 'r') as f:
        content = f.read()
    
    return str(PATCH_IDETEFICATOR) in content

def patch_game(game_path: str) -> bool:
    reset_log()
    global lib
    global bootstrap
    global renmodder
    global init

    lib = game_path + lib
    bootstrap = game_path + bootstrap
    renmodder = game_path + renmodder
    init = game_path + init

    ### Add prefix in window name
    if "--disable-lib" not in argv and "-dl" not in argv:
        if check_patched(lib):
            log("(F) 00library.rpy: ALREADY PATCHED")
        else:
            log("(*) Patching: Title...", end='')
            ret = patch(TITLE_ORIGINAL, TITLE_PATCHED, lib)
            if not ret:
                log("NOT FOUND", print_log=False)
            else:
                log("OK", print_log=False)
            log(f"(DEBUG) TITLE ORIGINAL: \n{TITLE_ORIGINAL}", print_data=False)
            log(f"(DEBUG) TITLE PATCHED: \n{TITLE_PATCHED}", print_data=False)
    else:
        log("($) 00library.rpy disabled by user (--disable-lib)")
    
    ### Patch bootstrap.py
    if check_patched(bootstrap):
        log("(F) bootstrap.py: ALREADY PATCHED")
    else:
        log("(*) Patching: Bootstrap...", end='')
        ret = patch(BOOTSTRAP_ORIGINAL, BOOTSTRAP_PATCHED, bootstrap)
        if not ret:
            log("NOT FOUND", print_log=False)
        else:
            log("OK", print_log=False)

    ### Patch __init__.py
    if check_patched(init):
        log("(F) __init__.py: ALREADY PATCHED")
    else:
        log("(*) Patching: __init__.py...", end='')
        ret = patch(INIT_ORIGINAL, INIT_PATCHED, init)
        if not ret:
            log("NOT FOUND", print_log=False)
        else:
            log("OK", print_log=False)

    ### Copy modder
    if "renmodder" not in listdir(game_path+"/renpy/"):
        log("(*) Renmodder folder not found. Creating it and copying files...", end='')
        copytree("patches/__mod_patch_renmodder/modder/", renmodder)
        log("OK", print_log=False)
    else:
        log("(*) Renmodder folder found. Skipping copying files...")

    ### Create test DME mod
    if "renmodder_mods" in listdir(game_path) and len(listdir(game_path+"/renmodder_mods/")) < 1:
        log("(*) Installing DME mod...", end='')
        with open(f"{game_path}/renmodder_mods/DME.py", "w") as mod:
            mod.write(DEV_TEST_MOD)
        log("OK", print_log=False)
    else:
        log("(*) DME.py found. Skipping...")

    ### Install RenModder 00start.rpy
    if "0RM_start.rpy" not in listdir(game_path+"/renpy/common/"):
        log("(*) Installing custom RenModder start.rpy script...", end='')
        with open("patches/__mod_patch_renmodder/modder/RM_start.rpy", "r") as start:
            custom_start = start.read()
        with open(f"{game_path}/renpy/common/0000A_RM_start.rpy", "w") as start:
            start.write(custom_start)
        log("OK", print_log=False)
    else:
        log("(*) 0RM_start.rpy found. Skipping...")

    ### Block original 00start.rpy
    if "00start.rpy" in listdir(game_path+"/renpy/common/"):
        log("(*) Blocking 00start.rpy...", end='')
        move(f"{game_path}/renpy/common/00start.rpy", f"{game_path}/renpy/common/00start.rpy.RM_BLOCKED")
        log("OK", print_log=False)
    else:
        log("(*) 00start.rpy not found, maybe already blocked. Skipping...")

    log("(*) Copying logo to game folder...", end='')
    copy("patches/__mod_patch_renmodder/modder/logo.png",
        path.join(game_path, "game/renmodder_logo.png"))
    log("OK", print_log=False)

    ### Install libraries
    setup_libraries(game_path)

    ### Clear compiled files
    def del_file(file_path: str):
        try:
            remove(file_path)
        except OSError as e:
            log(f"Failed to delete file {file_path}: {e}")

    log("(*) Clearing all .rpyc files...", end='')
    for root, dirs, files in walk(game_path):
        for file in files:
            if file.endswith(".rpyc"):
                file_path = path.join(root, file)
                Thread(target=del_file, args=(file_path,)).start()
    log("OK", print_log=False)

    return True

def unpatch_game(game_path: str) -> bool:
    reset_log()
    global lib
    global bootstrap
    global renmodder
    global init

    lib = game_path + lib
    bootstrap = game_path + bootstrap
    renmodder = game_path + renmodder
    init = game_path + init

    ### Unpatch title
    if check_patched(lib):
        log("(*) Unpatching: Title...", end='')
        ret = unpatch(TITLE_PATCHED, TITLE_ORIGINAL, lib)
        if not ret:
            log("NOT FOUND", print_log=False)
        else:
            log("OK", print_log=False)
    else:
        log("(F) 00library.rpy: NOT PATCHED")

    ### Unpatch bootstrap
    if check_patched(bootstrap):
        log("(*) Unpatching: Bootstrap...", end='')
        ret = unpatch(BOOTSTRAP_PATCHED, BOOTSTRAP_ORIGINAL, bootstrap)
        if not ret:
            log("NOT FOUND", print_log=False)
        else:
            log("OK", print_log=False)
    else:
        log("(F) bootstrap.py: NOT PATCHED")

    ### Unpatch __init__.py
    if check_patched(init):
        log("(*) Unpatching: __init__.py...", end='')
        ret = unpatch(INIT_PATCHED, INIT_ORIGINAL, init)
        if not ret:
            log("NOT FOUND", print_log=False)
        else:
            log("OK", print_log=False)
    else:
        log("(F) __init__.py: NOT PATCHED")

    ### Remove modder files
    log("(*) Deleting renmodder folder...", end='')
    rmtree(renmodder, True)
    log("OK", print_log=False)

    ### Unblock original 00start.rpy
    if "00start.rpy" not in listdir(game_path+"/renpy/common/"):
        log("(*) Unblocking 00start.rpy...", end='')
        move(f"{game_path}/renpy/common/00start.rpy.RM_BLOCKED", 
            f"{game_path}/renpy/common/00start.rpy")
        log("OK", print_log=False)
    else:
        log("(*) 00start.rpy found. Skipping...")

    ### Clear compiled files
    log("(*) Clearing all .rpyc files...", end='')
    for root, dirs, files in walk(game_path):
        for file in files:
            if file.endswith(".rpyc"):
                try:
                    remove(path.join(root, file))
                except OSError as e:
                    log(f"Failed to delete file {file}: {e}")
    log("OK", print_log=False)

    ### Remove logo
    log("(*) Deleting logo...", end='')
    try:
        remove(path.join(game_path, "game/renmodder_logo.png"))
    except Exception:
        pass
    log("OK", print_log=False)

    ### Remove libraries
    libs_path = path.join(game_path, LIBRARIES_DIR)
    if path.exists(libs_path):
        log("(*) Removing libraries...", end='')
        rmtree(libs_path)
        log("OK")

    return True