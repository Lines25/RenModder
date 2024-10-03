from shutil import rmtree, copytree
from os import listdir
from sys import argv

PATCH_IDETEFICATOR = 0x8000 | 0xABC # DON'T CHANGE IT. IF YOU CHANGE THIS YOU CAN'T UNPATCH
PATCH_VERSION = 0.1

TITLE_ORIGINAL = "        config.window_title = config.name or \"A Ren'Py Game\""
TITLE_PATCHED  = f"#{TITLE_ORIGINAL}\n        config.window_title = config.name+\" (PATCHED WITH RENMODDER v{PATCH_VERSION})\" or \"A Ren'Py Game (PATCHED WITH RENMODDER v{PATCH_VERSION})\" #{PATCH_IDETEFICATOR} RENMODDER MOD PATCH"

BOOTSTRAP_ORIGINAL = "def bootstrap(renpy_base):\n\n    global renpy"
BOOTSTRAP_PATCHED = \
"""def bootstrap(renpy_base, real_one=False):

    #{PATCH_IDETEFICATOR} RENMODDER MOD PATCH
    # global renpy
    if not real_one:
        global l
        for l in sys.modules.keys():
            print(f"[RENMODDER] RENMODDER BOOTSTRAPING: GLOBALING {l}")
            if not '.' in l:
                exec(f'global {l}')

        print('[RENMODDER] RENMODDER BOOTSTRAPING: LOADING RENMODDER MODULE')
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
# import renpy.renmodder.mod_api


class TestMod(Mod):
    def __mod_log(self, text: str):
        print(f"[RENMODDER] [{self.name}] ={self.id}= {text}")

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

def log(text: str, end: str = "\n", print_data: bool = True, print_log: bool = True):
    if print_data:
        if print_log:
            print(f"[LOG] {text}", end=end)
        else:
            print(text, end=end)
    with open(MOD_PATCH_LOG_FILE, "a") as log_file:
        log_file.write(f"{text}{end}")

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
    # If needed, we can add some to this function
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

    if "--disable-lib" not in argv and "-dl" not in argv:
        if check_patched(lib):
            log("(F) 00library.rpy: ALREDY PATCHED")

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
    
    if check_patched(bootstrap):
        log("(F) bootstrap.py: ALREDY PATCHED")
    else:
        log("(*) Patching: Bootstrap...", end='')
        ret = patch(BOOTSTRAP_ORIGINAL, BOOTSTRAP_PATCHED, bootstrap)
        if not ret:
            log("NOT FOUND", print_log=False)
        else:
            log("OK", print_log=False)

    if check_patched(init):
        log("(F) __init__.py: ALREDY PATCHED")
    else:
        log("(*) Patching: __init__.py...", end='')
        ret = patch(INIT_ORIGINAL, INIT_PATCHED, init)
        if not ret:
            log("NOT FOUND", print_log=False)
        else:
            log("OK", print_log=False)

    if "renmodder" not in listdir(game_path+"/renpy/"):
        log("(*) Renmodder folder not found. Creating it and copying files...", end='')

        # mkdir(renmodder)
        copytree("patches/__mod_patch_renmodder/modder/", renmodder)

        print("OK")
    else:
        log("(*) Renmodder folder is founded. Skipping copying files...")

    if "renmodder_mods" in listdir(game_path) and \
         len(listdir(game_path+"/renmodder_mods/")) < 1:
        log("(*) Installing DME mod...", end='')

        with open(f"{game_path}/renmodder_mods/", "w") as mod:
            mod.write(DEV_TEST_MOD)
        
        print("OK")

    else:
        log("(*) DME.py founded. Skipping...")

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

    if check_patched(lib):
        log("(*) Unpatching: Title...", end='')
        ret = patch(TITLE_PATCHED, TITLE_ORIGINAL, lib)
        # ret = unpatch(lib, PATCH_IDETEFICATOR)
        if not ret:
            log("NOT FOUND", print_log=False)
        else:
            log("OK", print_log=False)
    else:
        log("(F) 00library.rpy: NOT PATCHED")

    if check_patched(bootstrap):
        log("(*) Unpatching: Bootstrap...", end='')
        ret = patch(BOOTSTRAP_PATCHED, BOOTSTRAP_ORIGINAL, bootstrap)
        if not ret:
            log("NOT FOUND", print_log=False)
        else:
            log("OK", print_log=False)
    else:
        log("(F) bootstrap.py: NOT PATCHED")

    if check_patched(init):
        log("(*) Unpatching: __init__.py...", end='')
        ret = patch(INIT_PATCHED, INIT_ORIGINAL, init)
        # ret = unpatch(lib, PATCH_IDETEFICATOR)
        if not ret:
            log("NOT FOUND", print_log=False)
        else:
            log("OK", print_log=False)
    else:
        log("(F) __init__.py: NOT PATCHED")


    log("(*) Deleting renmodder folder...", end='')
    rmtree(renmodder, True)
    log("OK", print_log=False)

    log("(*) Deleting renmodder_mods folder...", end='')
    rmtree(game_path+"/renmodder_mods/", True)
    log("OK", print_log=False)

    return True
