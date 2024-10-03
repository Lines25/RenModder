from __future__ import division, absolute_import, with_statement, print_function, unicode_literals
import sys
import renpy.renmodder.presplash # type: ignore
import os
import subprocess
from .main import main
from .mod import Mod
from renpy.renmodder.config import *

# import renpy.display

FSENENCODING = FSENCODING = sys.getfilesystemencoding() or "utf-8"

def log(text: str):
    print(f"[RENMODDER] RENMODDER BOOTSTRAP: {text}")


def get_alternate_base(basedir, always=False):
    """
    :undocumented:

    Tries to find an alternate base directory. This exists in a writable
    location, and is intended for use by a game that downloads its assets
    to the device (generally for ios or android, where the assets may be
    too big for the app store).
    """

    # Determine the alternate base directory location.

    if renpy.android:
        altbase = os.path.join(os.environ["ANDROID_PRIVATE"], "base")

    elif renpy.ios:
        from pyobjus import autoclass # type: ignore
        from pyobjus.objc_py_types import enum # type: ignore

        NSSearchPathDirectory = enum("NSSearchPathDirectory", NSApplicationSupportDirectory=14)
        NSSearchPathDomainMask = enum("NSSearchPathDomainMask", NSUserDomainMask=1)

        NSFileManager = autoclass('NSFileManager')
        manager = NSFileManager.defaultManager()
        url = manager.URLsForDirectory_inDomains_(
            NSSearchPathDirectory.NSApplicationSupportDirectory,
            NSSearchPathDomainMask.NSUserDomainMask,
            ).lastObject()

        # url.path seems to change type based on iOS version, for some reason.
        try:
            altbase = url.path().UTF8String()
        except Exception:
            altbase = url.path.UTF8String()

        if isinstance(altbase, bytes):
            altbase = altbase.decode("utf-8")

    else:
        altbase = os.path.join(basedir, "base")

    if always:
        return altbase

    # Check to see if there's a game in there created with the
    # current version of Ren'Py.

    def ver(s):
        """
        Returns the first three components of a version string.
        """

        return tuple(int(i) for i in s.split(".")[:3])

    import json

    version_json = os.path.join(altbase, "update", "version.json")

    if not os.path.exists(version_json):
        return basedir

    with open(version_json, "r") as f:
        modules = json.load(f)

        for v in modules.values():
            if ver(v["renpy_version"]) != ver(renpy.version_only):
                return basedir

    return altbase

def popen_del(self, *args, **kwargs):
    """
    Fix an issue where the __del__ method of popen doesn't work.
    """

    return

mods = []
def run(renpy_base):
    global renpy
    
    if renpy_base.endswith("/"):
        renpy_base = renpy_base[:-1] # Delete "/" at the end

    print(renpy_base)
    log("Loading mods...")
    mods_path = MODS_PATH.replace("~", renpy_base)

    if not os.path.exists(mods_path):
        os.mkdir(mods_path)

    for file in os.listdir(mods_path):
        if file.endswith(".py"):
            with open(os.path.join(mods_path, file), 'r') as module:
                file_content = module.read()

            is_mod = False
            class_name = None
            for line in file_content.split("\n"):
                if "(Mod)" in line:
                    is_mod = True
                    class_name = line.replace("(Mod):", '').replace("class ", '')
                    # From:
                    # ```python
                    # ...
                    # class ThisIsMod(Mod):
                    # ...
                    # ```
                    # To:
                    # ThisIsMod
                    break

            if is_mod:
                exec(file_content, globals(), locals())
                exec(f"mod = {class_name}()")
                mods.append(mod)

    for mod in mods:
        log(f"Bootstraping: {mod.name} ...")
        mod.bootstrap()

    import renpy.config
    import renpy.log
    
    log("Some required garbage...")
    # Remove a legacy environment setting.
    if os.environ.get("SDL_VIDEODRIVER", "") == "windib":
        del os.environ["SDL_VIDEODRIVER"]

    if not isinstance(renpy_base, str):
        renpy_base = str(renpy_base, FSENCODING)

    # If environment.txt exists, load it into the os.environ dictionary.
    if os.path.exists(renpy_base + "/environment.txt"):
        evars = { }
        with open(renpy_base + "/environment.txt", "r") as f:
            code = compile(f.read(), renpy_base + "/environment.txt", 'exec')
            exec(code, evars)
        for k, v in evars.items():
            if k not in os.environ:
                os.environ[k] = str(v)

    # Also look for it in an alternate path (the path that contains the
    # .app file.), if on a mac.
    alt_path = os.path.abspath("renpy_base")
    if ".app" in alt_path:
        alt_path = alt_path[:alt_path.find(".app") + 4]

        if os.path.exists(alt_path + "/environment.txt"):
            evars = { }
            with open(alt_path + "/environment.txt", "rb") as f:
                code = compile(f.read(), alt_path + "/environment.txt", 'exec')
                exec(code, evars)
            for k, v in evars.items():
                if k not in os.environ:
                    os.environ[k] = str(v)

    basedir = os.getcwd()

    # Get a working name for the game.
    name = os.path.basename(sys.argv[0])

    if name.find(".") != -1:
        name = name[:name.find(".")]

    if not isinstance(renpy_base, str):
        renpy_base = str(renpy_base, FSENCODING)
    
    log("Trying to parse arguments...")
    # Parse the arguments.
    import renpy.arguments # type: ignore
    args = renpy.arguments.bootstrap()

    if args.trace:
        enable_trace(args.trace)  # noqa: F821

    if args.basedir:
        basedir = os.path.abspath(args.basedir)
        if not isinstance(basedir, str):
            basedir = basedir.decode(FSENCODING)
    else:
        basedir = renpy_base

    if not os.path.exists(basedir):
        sys.stderr.write("Base directory %r does not exist. Giving up.\n" % (basedir,))
        sys.exit(1)

    sys.path.insert(0, basedir)

    if renpy.macintosh:
        # If we're on a mac, install our own os.start.
        os.startfile = mac_start # type: ignore  # noqa: F821

        # Are we starting from inside a mac app resources directory?
        if basedir.endswith("Contents/Resources/autorun"):
            renpy.macapp = True

    # Check that we have installed pygame properly. This also deals with
    # weird cases on Windows and Linux where we can't import modules. (On
    # windows ";" is a directory separator in PATH, so if it's in a parent
    # directory, we won't get the libraries in the PATH, and hence pygame
    # won't import.)
    log("Trying to import pygame_sdl2...")
    try:
        import pygame_sdl2 # type: ignore
        if not ("pygame" in sys.modules):  # noqa: E713
            pygame_sdl2.import_as_pygame()
    except Exception:
        print("""\
Could not import pygame_sdl2. Please ensure that this program has been built
and unpacked properly. Also, make sure that the directories containing
this program do not contain : or ; in their names.

You may be using a system install of python. Please run {0}.sh,
{0}.exe, or {0}.app instead.
""".format(name), file=sys.stderr)

        raise
    
    gamedir = renpy.__main__.path_to_gamedir(basedir, name)

    # If we're not given a command, show the presplash.
    if args.command == "run" and not renpy.mobile:
        global window
        from .presplash import PresplashVenom
        pv = PresplashVenom()
        window = pv.start(basedir, gamedir)

    log("Trying to import _renpy...")
    # Ditto for the Ren'Py module.
    try:
        import _renpy # type: ignore  # noqa: F401
    except Exception:
        print("""\
Could not import _renpy. Please ensure that this program has been built
and unpacked properly.

You may be using a system install of python. Please run {0}.sh,
{0}.exe, or {0}.app instead.
""".format(name), file=sys.stderr)
        raise

    log("Trying to import the rest of renpy...")
    # Load the rest of Ren'Py.
    import renpy # type: ignore

    # log("Trying to load presplash venom...")
    # pv = renpy.renmodder.presplash.PresplashVenom()
    # pv.start(basedir, gamedir)

    log("Trying import_all() from renpy...")
    renpy.import_all()

    log("Trying loader.init_importer from renpy...")
    renpy.loader.init_importer()

    log("Starting draw...")

    exit_status = None
    original_basedir = basedir
    original_sys_path = list(sys.path)

    # Debug console, if needed to test smthing

    try:
        while exit_status is None:
            exit_status = 1

            try:

                # Potentially use an alternate base directory.
                try:
                    basedir = get_alternate_base(original_basedir)
                except Exception:
                    import traceback
                    traceback.print_exc()

                gamedir = renpy.__main__.path_to_gamedir(basedir, name)

                sys.path = list(original_sys_path)
                if basedir not in sys.path:
                    sys.path.insert(0, basedir)

                renpy.game.args = args
                renpy.config.renpy_base = renpy_base
                renpy.config.basedir = basedir
                renpy.config.gamedir = gamedir
                renpy.config.args = [ ] # type: ignore

                renpy.config.logdir = renpy.__main__.path_to_logdir(basedir)

                if not os.path.exists(renpy.config.logdir):
                    os.makedirs(renpy.config.logdir, 0o777)

                log("MAIN")
                main(mods)

                exit_status = 0

            except KeyboardInterrupt:
                raise

            except renpy.game.UtterRestartException:

                # On an UtterRestart, reload Ren'Py.
                renpy.reload_all()

                exit_status = None

            except renpy.game.QuitException as e:
                exit_status = e.status

                if e.relaunch:
                    if hasattr(sys, "renpy_executable"):
                        subprocess.Popen([sys.renpy_executable] + sys.argv[1:]) # type: ignore
                    else:
                        if PY2: # type: ignore  # noqa: F821
                            subprocess.Popen([sys.executable, "-EO"] + sys.argv)
                        else:
                            subprocess.Popen([sys.executable] + sys.argv)

            except renpy.game.ParseErrorException:
                pass

            except Exception as e:
                renpy.error.report_exception(e)

        log(f"Exiting with code: {exit_status}")
        sys.exit(exit_status)

    finally:
        log("Triggered shutdown...")

        # if "RENPY_SHUTDOWN_TRACE" in os.environ:
        #     enable_trace(int(os.environ["RENPY_SHUTDOWN_TRACE"]))

        log("Shutdowning: TTS...")
        renpy.display.tts.tts(None) # type: ignore

        log("Shutdowning: Cache...")
        renpy.display.im.cache.quit() # type: ignore

        if renpy.display.draw: # type: ignore
            log("Shutdowning: Draw...")
            renpy.display.draw.quit() # type: ignore

        log("Shutdowning: Audio...")
        renpy.audio.audio.quit()

        # Prevent subprocess from throwing errors while trying to run it's
        # __del__ method during shutdown.
        if not renpy.emscripten:
            subprocess.Popen.__del__ = popen_del # type: ignore

