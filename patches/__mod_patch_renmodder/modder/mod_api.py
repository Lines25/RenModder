import sys

def parse(*args, **kwargs):
    raise NotImplementedError("Renmodder Error: Mod API not loaded, but used function that uses other modules")

mod_api_loaded = False
def load_mod_api():
    global mod_api_loaded
    global archived

    if mod_api_loaded:
        return

    # from renpy.parser import parser

    mod_api_loaded = True

def wait_mod(mod_name: str):
    """Wait for other mod to load
    
    Keyword arguments:
    mod_name: str -- Mod name in string (test.lines.library)
    Return: None
    """
    global mods_loaded
    while True:
        if mod_name in mods_loaded:
            break

def run_renpy_code(code: str, linenumber: int = 1):
    """Run Ren'Py code
    
    Keyword arguments:
    code: str -- All code that have to be injected (you can use '''/\"\"\" for this)
    linenumber: int -- Line that start exec code from
    Return: None
    """
    parse(code, linenumber=linenumber)

def wait_for_module(module_name: str):
    """Wait for module to load (via import, checks sys.modules)
    
    Keyword arguments:
    module_name: str -- module name that wait for
    Return: None
    """
    while True:
        if module_name in sys.modules:
            break

def patch_script(script_name: str, code_to_patch: str, patched_code: str):
    """Function that inject Ren'Py code into script_name in archive.rpa or scripts.rpa
    
    Keyword arguments:
    script_name: str -- Files that how to be patched
    code_to_patch: str -- Fragment of code that have to be replaced
    patched_code: str -- Code to replace code_to_patch fragment
    Return: None
    """
    
