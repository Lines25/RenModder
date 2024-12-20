from shutil import rmtree, copytree, move
from os import listdir, remove, walk, makedirs, path
from sys import argv
from threading import Thread

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
        print(f"[RENMODDER] [{self.name}] {text}")

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
            print(f"[LOG] {text}", end=end, flush=True)
        else:
            print(text, end=end, flush=True)
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

    ### Add prefix in window name
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
    
    ### Patch bootstrap.py that it will be run renpy.renmodder.bootstrap.run()
    if check_patched(bootstrap):
        log("(F) bootstrap.py: ALREDY PATCHED")
    else:
        log("(*) Patching: Bootstrap...", end='')
        ret = patch(BOOTSTRAP_ORIGINAL, BOOTSTRAP_PATCHED, bootstrap)
        if not ret:
            log("NOT FOUND", print_log=False)
        else:
            log("OK", print_log=False)

    ### Patch __init__.py that it don't pickle() renmodder components
    if check_patched(init):
        log("(F) __init__.py: ALREDY PATCHED")
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

        # mkdir(renmodder)
        copytree("patches/__mod_patch_renmodder/modder/", renmodder)

        log("OK", print_log=False)
    else:
        log("(*) Renmodder folder is founded. Skipping copying files...")

    ### Create test DME mod
    if "renmodder_mods" in listdir(game_path) and \
         len(listdir(game_path+"/renmodder_mods/")) < 1:
        log("(*) Installing DME mod...", end='')

        with open(f"{game_path}/renmodder_mods/DME.py", "w") as mod:
            mod.write(DEV_TEST_MOD)
        
        log("OK", print_log=False)

    else:
        log("(*) DME.py founded. Skipping...")

    ### Install RenModder 00start.rpy
    if "0RM_start.rpy" not in listdir(game_path+"/renpy/common/"):
        log("(*) Installing custom RenModder start.rpy script...", end='')

        with open("patches/__mod_patch_renmodder/modder/RM_start.rpy", "r") as start:
            custom_start = start.read()

        with open(f"{game_path}/renpy/common/0000A_RM_start.rpy", "w") as start:
            start.write(custom_start)

        log("OK", print_log=False)
    else:
        log("(*) 0RM_start.rpy founded. Skipping...")

    ### Block original 00start.rpy. If don't do this, it will conflict with RenModder one
    if "00start.rpy" in listdir(game_path+"/renpy/common/"):
        log("(*) Blocking 00start.rpy...", end='')

        move(f"{game_path}/renpy/common/00start.rpy", f"{game_path}/renpy/common/00start.rpy.RM_BLOCKED")

        log("OK", print_log=False)
    else:
        log("(*) 00start.rpy not found, maybe, alredy blocked. Skipping...")


    ### Install RenModder libs
    if len(listdir("patches/__mod_patch_renmodder/libs/")) != 0:
        game_libs = ''
        for file in listdir(game_path+"/lib/"):
            if file.startswith("python"):
                game_libs = f"{game_path}/lib/{file}/renmodder_libs/"
                
                break

        log("(*) Injecting libraries:")
        
        for file in listdir('patches/__mod_patch_renmodder/libs/'):
            log(f"- {file} ...", end='')
            move("patches/__mod_patch_renmodder/libs/"+file, game_libs)
            log("OK", print_log=False)

    ### Clear all compiled .rpy files
    def del_file(file_path: str):
        try:
            remove(file_path)
        except OSError as e:
            log(f"Failed to delete file {file_path}: {e}")

    log("(*) Clearing all .rpyc files, please wait...", end='')

    for root, dirs, files in walk(game_path):
        for file in files:
            if file.endswith(".rpyc"):
                file_path = path.join(root, file)
                Thread(target=del_file, args=(file_path,)).run()
                

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

    ### Unpatch title of window, if patched
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

    ### Unpatch bootstrap, if patched
    if check_patched(bootstrap):
        log("(*) Unpatching: Bootstrap...", end='')
        ret = patch(BOOTSTRAP_PATCHED, BOOTSTRAP_ORIGINAL, bootstrap)
        if not ret:
            log("NOT FOUND", print_log=False)
        else:
            log("OK", print_log=False)
    else:
        log("(F) bootstrap.py: NOT PATCHED")

    ### Unpatch __init__.py, if patched
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


    ### Delete RenModder files
    log("(*) Deleting renmodder folder...", end='')
    rmtree(renmodder, True)
    log("OK", print_log=False)
    
    # If you want, you can turn this on, but author is not recomend to do that:

    # log("(*) Deleting renmodder_mods folder...", end='')
    # rmtree(game_path+"/renmodder_mods/", True)
    # log("OK")

    ### Delete RenModder custom 00start.rpy
    log("(*) Deleting 0RM_start.rpy...", end='')
    try:
        remove(game_path+"/renpy/common/0000A_RM_start.rpy")
    except Exception:
        pass
    log("OK")    

    ### Unblock original 00start.rpy
    if "00start.rpy" not in listdir(game_path+"/renpy/common/"):
        log("(*) Unblocking 00start.rpy...", end='')

        move(f"{game_path}/renpy/common/00start.rpy.RM_BLOCKED", f"{game_path}/renpy/common/00start.rpy")
        
        log("OK", print_log=False)
    else:
        log("(*) 00start.rpy found. Skipping...")



    ### Clear all compiled .rpy files. If don't do this, it will cause conflicts
    # (Ren'Py will load .rpyc files instead of .rpy one)
    log("(*) Clearing all .rpyc files, please wait...", end='')

    for root, dirs, files in walk(game_path):
        for file in files:
            if file.endswith(".rpyc"):
                file_path = path.join(root, file)
                try:
                    remove(file_path)
                except OSError as e:
                    log(f"Failed to delete file {file_path}: {e}")

    log("OK", print_log=False)
    

    return True
