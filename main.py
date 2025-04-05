#!/bin/python3
from os import listdir
from os.path import exists
from sys import argv, exc_info
from importlib import import_module
from traceback import print_exc
from sys import exit

def main():
    raw_patches = listdir("./patches/")

    patches = []
    for raw_patch in raw_patches:
        if raw_patch.endswith("patch.py") and not raw_patch.startswith("__"):
            patches.append(raw_patch[:-9]) # [:9] deletes "_patch.py" from filename

    print("[LOG] RenModder - The modder for Ren'Py games")
    print(f"[LOG] (+) Founded patches: {len(patches)}")
    if len(argv) <= 2 or len(argv) > 4:
        print("[LOG] (F) Please, use this tool like this:")
        print(f"{argv[0]} ~/DDLC/ dev patch # Patching to enable developer mode")
        print(f"{argv[0]} \"C:\\Games\\Starry flowers\\\" mod unpatch # Unpatching to delete mod support")
        print("New patches coming soon...")
        exit(1)

    game = argv[1]
    patch = argv[2]
    have_to_patch = argv[3].lower() == 'patch'

    if game.endswith('\\') or game.endswith('/'):
        game = game[:-1]

    if not exists(game):
        print(f"[LOG] (F) Game with path '{game}' not found")
    else:
        print(f"[LOG] (+) Game with path '{game}' was found")

    if patch.endswith("_patch"):
        patch = patch[:-6]

    if patch.endswith(".py"):
        patch = patch[:-3]

    if patch in patches:
        patch_module = import_module(f"patches.{patch}_patch")
        if have_to_patch:
            try:
                patched = patch_module.patch_game(game)
            except Exception as e:
                patched = False
                print("[LOG] (I) Exception:")
                print_exc()
                
            if patched:
                print("[LOG] (+) Game patched")
            else:
                print("[LOG] (F) Failed to patch game")
        elif argv[3].lower() == 'repatch':
            try:
                unpatched = patch_module.unpatch_game(game)
            except Exception as e:
                unpatched = False
                print("[LOG] (I) Exception:", end=' ')
                print(exc_info()[1])

            if unpatched:
                print("[LOG] (+) Yep, game now unpatched !")
            else:
                print("[LOG] (F) An Error corrupted when trying to unpatch, maybe, game isn't patched !")
                exit(1)

            try:
                patched = patch_module.patch_game(game)
            except Exception as e:
                patched = False
                print("[LOG] (I) Exception:")
                print_exc()
                
            if patched:
                print("[LOG] (+) Game patched")
            else:
                print("[LOG] (F) Failed to patch game")
                exit(1)
        else:
            try:
                unpatched = patch_module.unpatch_game(game)
            except Exception as e:
                unpatched = False
                print("[LOG] (I) Exception:", end=' ')
                print(exc_info()[1])

            if unpatched:
                print("[LOG] (+) Yep, game now unpatched !")
            else:
                print("[LOG] (F) An Error corrupted when trying to unpatch, maybe, game isn't patched !")
    else:
        print(f"[LOG] (F) Patch {patch} Not found")

if __name__ == "__main__":
    main()
