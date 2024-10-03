# This patch just automatic enable dev mode in game
# For open dev menu for cheating, press: SHIFT+D
# Created by: Lines
PATCH_IDETEFICATOR = 0xFFAAFF # DON'T CHANGE IT. IF YOU CHANGE THIS YOU CAN'T UNPATCH
PATCH = f"""#{PATCH_IDETEFICATOR} RENMODDER DEV PATCH

#    if config.script_version:
#        config.developer = False
#        config.default_developer = False
#    else:
#        config.developer = True
#        config.default_developer = True
    config.developer = True
    config.default_developer = True"""


ORIGINAL_CODE = """    if config.script_version:
        config.developer = False
        config.default_developer = False
    else:
        config.developer = True
        config.default_developer = True"""

def patch_game(game_path: str) -> bool:
    file_path = f'{game_path}/renpy/common/00library.rpy'
    
    with open(file_path, 'r') as lib:
        content = lib.read()

    if f"#{PATCH_IDETEFICATOR}" in content:
        return False

    if ORIGINAL_CODE in content:
        content = content.replace(ORIGINAL_CODE, PATCH)

        with open(file_path, 'w') as lib:
            lib.write(content)
            
        print("[LOG] (+) Yep, game is now have developer mode enabled. Go have fun !")
        print("[LOG] (*) If you don't know how to use dev menu, just press SHIFT+D")
        return True
    else:
        print("[LOG] (-) Failed to found original code...")

    print("[LOG] (?) Hmm.. Someting wrong.. Try run the game first or rerun script. If it's isn't helped, please, open new Issue on github of this project or write me: @lines8810 (in discord)")
    return False

def unpatch_game(game_path: str) -> bool:
    file_path = f'{game_path}/renpy/common/00library.rpy'
    
    with open(file_path, 'r') as lib:
        content = lib.read()

    if f"#{PATCH_IDETEFICATOR}" in content:
        raw_unpatch_code = "\n".join(
            line[1:] for line in PATCH.splitlines() if line.strip().startswith("#")
        ).replace(f"{PATCH_IDETEFICATOR} RENMODDER DEV PATCH", '')

        raw_unpatch_code = raw_unpatch_code.strip()
        print(raw_unpatch_code)
        
        unpatch_code = raw_unpatch_code
        if "    if" not in raw_unpatch_code:
            unpatch_code = "".join(
                unpatch_code.splitlines()
            )


        content = content.replace(PATCH.strip(), unpatch_code)

        with open(file_path, 'w') as lib:
            lib.write(content)
        return True

    return False
