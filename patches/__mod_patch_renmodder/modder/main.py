from __future__ import division, absolute_import, with_statement, print_function, unicode_literals

import os
import sys
import time
import zipfile
import gc
import linecache
import json

import renpy # type: ignore
import renpy.game as game # type: ignore
import pygame_sdl2 as pygame

import renpy.renmodder.mod_api
import renpy.renmodder.events
from renpy.renmodder.bootstrap import _dir

last_clock = time.time()

def main_log(text: str, write_to=sys.stdout):
    print(f"[RENMODDER] MAIN: {text}", file=write_to)

def event_wrapper(func, event_type):
    renpy.renmodder.events.trigger_event(event_type)
    func()

class InputEventHandler(object):
    def __init__(self):
        self.event_func = lambda ev: renpy.renmodder.events.trigger_event("input", ev)
    
    def __call__(self, ev, x=0, y=0, st=0):
        self.event_func(ev)
        return None

def run(restart):
    """
    This is called during a single run of the script. Restarting the script
    will cause this to change.
    """
    global io

    reset_clock()

    # Reset the store to a clean version of itself.
    renpy.python.clean_stores()
    log_clock("Cleaning stores")

    # Init translation.
    renpy.translation.init_translation()
    log_clock("Init translation")

    # Rebuild the various style caches.
    renpy.style.build_styles() # @UndefinedVariable
    log_clock("Build styles")

    renpy.sl2.slast.load_cache()
    log_clock("Load screen analysis")

    # Analyze the screens.
    renpy.display.screen.analyze_screens()
    log_clock("Analyze screens")

    if not restart:
        renpy.sl2.slast.save_cache()
        log_clock("Save screen analysis")

    # Prepare the screens.
    renpy.display.screen.prepare_screens()

    log_clock("Prepare screens")

    if not restart:
        renpy.pyanalysis.save_cache()
        log_clock("Save pyanalysis.")

        renpy.game.script.save_bytecode()
        log_clock("Save bytecode.")

    # Handle arguments and commands.
    if not renpy.arguments.post_init():
        # We use 'exception' instead of exports.quit
        # to not call quit label since it's not necessary.
        raise renpy.game.QuitException()

    if renpy.config.clear_lines:
        renpy.scriptedit.lines.clear()

    # Sleep to finish the presplash.
    renpy.display.presplash.sleep()

    # Re-Initialize the log.
    game.log = renpy.python.RollbackLog()

    # Switch contexts, begin logging.
    game.contexts = [ renpy.execution.Context(True) ]

    # Jump to an appropriate start label.
    if game.script.has_label("_start"):
        start_label = '_start'
    else:
        start_label = 'start'

    try:
        renpy.exports.log("--- " + time.ctime())
        renpy.exports.log("")
    except Exception:
        pass

    # Note if this is a restart.
    renpy.store._restart = restart
    # We run until we get an exception.
    renpy.display.interface.enter_context()

    log_clock("Running {}".format(start_label))
    
    game.script.load_script() # Load all new scripts
    if game.script.has_label("RM_start"):
        game.context().goto_label("RM_start")
    else:
        main_log(f" ===== FAILED TO USE RM_start. USING REN'PY ORIGINAL {start_label} ...")
        game.context().goto_label(start_label)

    global mods
    for mod in renpy.store.mods:
        main_log(f"Main Ending: {mod.name}...")
        mod.main_end()
        

    
    # Initialize display and run the context
    main_log("Initializing display...")
    # renpy.display.core.cpu_idle.init() # Not supported by Ren'Py 8.2+
    renpy.display.interface.post_init()
    
    # Run the main game context
    main_log("Running main context...")
    renpy.execution.run_context(True)
    
    # Clean up after run
    main_log("Cleaning up...")
    # renpy.display.core.cpu_idle.end() # Not supported by Ren'Py 8.2+
    
    # Final event trigger before exit
    renpy.renmodder.events.trigger_event("end")
    main_log("Run complete.")


def load_rpe(fn):

    with zipfile.ZipFile(fn) as zfn:
        autorun = zfn.read("autorun.py")

    if fn in sys.path:
        sys.path.remove(fn)
    sys.path.insert(0, fn)
    exec(autorun, {'__file__': os.path.join(fn, "autorun.py")})

def log_clock(s):
    global last_clock
    now = time.time()
    s = "{} took {:.2f}s".format(s, now - last_clock)

    renpy.display.log.write(s)

    # Pump the presplash window to prevent marking
    # our process as unresponsive by OS
    renpy.display.presplash.pump_window()

    last_clock = now


def reset_clock():
    global last_clock
    last_clock = time.time()

def load_build_info():
    """
    Loads cache/build_info.json, and uses it to initialize the
    renpy.game.build_info dictionary.
    """

    try:
        f = renpy.exports.open_file("cache/build_info.json", "utf-8")
        renpy.game.build_info = json.load(f)
    except Exception:
        renpy.game.build_info = { "info" : { } }

def choose_variants():

    if "RENPY_VARIANT" in os.environ:
        renpy.config.variants = list(os.environ["RENPY_VARIANT"].split()) + [ None ] # type: ignore
        renpy.display.emulator.early_init_emulator()
        return

    renpy.config.variants = [ None ]

    # Deleted emiscripten, iOS and Android support
    # Because they all sucks and RenModder ALWAYS have only
    # PC (Linux, MacOS and Windows) support !!!

    renpy.config.variants.insert(0, 'pc') # type: ignore

    renpy.config.variants.insert(0, 'large') # type: ignore


def main(mods):
    if "_loaded_time" not in _dir(renpy.store):
        renpy.store._loaded_time = time.time()
    renpy.store.mods = mods

    renpy.renmodder.mod_api.load_mod_api()
    global win

    for mod in mods:
        main_log(f"Running main() in: {mod.name} ...")
        mod.main()

    gc.set_threshold(*renpy.config.gc_thresholds)

    renpy.game.exception_info = 'Before loading the script.'

    # Clear the line cache, since the script may have changed.
    main_log("Clearing line cache...")
    linecache.clearcache()

    # Get ready to accept new arguments.
    main_log("Preiniting arguments...")
    renpy.arguments.pre_init()

    # Init the screen language parser
    main_log("Initializing sl2 parser")
    renpy.sl2.slparser.init()

    # Init the config after load.
    main_log("Initializing config...")
    renpy.config.init()

    # Reset live2d if it exists.
    try:
        main_log("Trying to reset live2d")
        renpy.gl2.live2d.reset()
    except Exception:
        main_log("Live2d not found, 'kay")
        pass

    # Set up variants.
    choose_variants()
    renpy.display.touch = "touch" in renpy.config.variants

    if (renpy.android or renpy.ios) and not renpy.config.log_to_stdout:
        print("Version:", renpy.version)

    # Note the game directory.
    game.basepath = renpy.config.gamedir
    renpy.config.commondir = renpy.__main__.path_to_common(renpy.config.renpy_base) # E1101 @UndefinedVariable
    try:
        renpy.config.searchpath = renpy.__main__.predefined_searchpath(renpy.config.commondir) # E1101 @UndefinedVariable
    except AttributeError:
            renpy.config.searchpath = [renpy.config.gamedir]



    # Load Ren'Py extensions.
    main_log("Loading Ren'Py extensions:")
    for dir in renpy.config.searchpath: # @ReservedAssignment

        if not os.path.isdir(dir):
            continue

        for fn in sorted(os.listdir(dir)):
            if fn.lower().endswith(".rpe"):
                rpe_file = f"{dir}/{fn}"
                main_log(f" - {rpe_file}")
                load_rpe(rpe_file)

    # Generate a list of extensions for each archive handler.
    main_log("Generating a list of extensions...")
    archive_extensions = [ ]
    for handler in renpy.loader.archive_handlers:
        for ext in handler.get_supported_extensions():
            if not (ext in archive_extensions):  # noqa: E713
                archive_extensions.append(ext)

    main_log("Searching for archives")
    # Find archives.
    for dn in renpy.config.searchpath:

        if not os.path.isdir(dn):
            continue

        for i in sorted(os.listdir(dn)):
            base, ext = os.path.splitext(i)

            # Check if the archive does not have any of the extensions in archive_extensions
            if not (ext in archive_extensions):  # noqa: E713
                continue

            renpy.config.archives.append(base)

    renpy.config.archives.reverse()

    # Initialize archives.
    main_log("Initializing archives...")
    renpy.loader.index_archives()

    # Start auto-loading.
    main_log("Starting auto-loading...")
    renpy.loader.auto_init()

    main_log("Loading build info...")
    load_build_info()

    log_clock("Early init")

    # Initialize the log.
    main_log("Initializing original Ren'Py log...")
    game.log = renpy.python.RollbackLog()

    # Initialize the store.
    renpy.store.store = sys.modules['store'] # type: ignore

    # Set up styles.
    main_log("Setting up styles...")
    game.style = renpy.style.StyleManager() # @UndefinedVariable
    renpy.store.style = game.style

    # Run init code in its own context. (Don't log. Ok)
    game.contexts = [ renpy.execution.Context(False) ]
    game.contexts[0].init_phase = True

    renpy.execution.not_infinite_loop(60)

    # Load the script.
    main_log("Loading script...")
    renpy.game.exception_info = 'While loading the script.'
    renpy.game.script = renpy.script.Script()

    if renpy.session.get("compile", False):
        renpy.game.args.compile = True # type: ignore

    # Set up error handling.
    main_log("Loading error handler...")
    try:
        renpy.exports.load_module("_errorhandling")
    except Exception:
        renpy.exports.load_module("_errorhandling")

    if renpy.exports.loadable("tl/None/common.rpym") or renpy.exports.loadable("tl/None/common.rpymc"):
        renpy.exports.load_module("tl/None/common")

    main_log("Initializing system styles and building styles...")
    try:
        renpy.config.init_system_styles()
        renpy.style.build_styles() # @UndefinedVariable
    except TypeError:
        game.style = renpy.style.StyleManager() # @UndefinedVariable
        renpy.store.style = game.style

    log_clock("Loading error handling")
    main_log("Loading error handling...")

    # If recompiling everything, remove orphan .rpyc files.
    # Otherwise, will fail in case orphan .rpyc have same
    # labels as in other scripts (usually happens on script rename).
    if (renpy.game.args.command == 'compile') and not (renpy.game.args.keep_orphan_rpyc): # type: ignore

        for (fn, dn) in renpy.game.script.script_files:

            if dn is None:
                continue

            if not os.path.isfile(os.path.join(dn, fn + ".rpy")) and not os.path.isfile(os.path.join(dn, fn + "_ren.py")):

                try:
                    name = os.path.join(dn, fn + ".rpyc")
                    os.rename(name, name + ".bak")
                except OSError:
                    # This perhaps shouldn't happen since either .rpy or .rpyc should exist
                    pass

        # Update script files list, so that it doesn't contain removed .rpyc's
        renpy.loader.cleardirfiles()
        renpy.game.script.scan_script_files()

    # Load all .rpy files.
    main_log("Loading all .rpy files...")
    renpy.game.script.load_script() # sets renpy.game.script.
    log_clock("Loading script")

    main_log("Loading script...")
    if renpy.game.args.command == 'load-test': # type: ignore
        start = time.time()

        for i in range(5):
            print(i)
            renpy.game.script = renpy.script.Script()
            renpy.game.script.load_script()

        print(time.time() - start)
        sys.exit(0)

    renpy.game.exception_info = 'After loading the script.'

    # Find the save directory.
    if renpy.config.savedir is None:
        renpy.config.savedir = renpy.__main__.path_to_saves(renpy.config.gamedir) # E1101 @UndefinedVariable

    if renpy.game.args.savedir: # type: ignore
        renpy.config.savedir = renpy.game.args.savedir # type: ignore

    main_log(f"Found Ren'Py savedir at: {renpy.config.savedir}")

    # Init the save token system, if we can.
    try:
        main_log("Initializing savetoken system...")
        renpy.savetoken.init()
    except Exception: pass

    # Init preferences.
    game.persistent = renpy.persistent.init()
    game.preferences = game.persistent._preferences

    for i in renpy.game.persistent._seen_translates: # type: ignore
        if i in renpy.game.script.translator.default_translates:
            renpy.game.seen_translates_count += 1

    if game.persistent._virtual_size:
        renpy.config.screen_width, renpy.config.screen_height = game.persistent._virtual_size

    # Init save locations and loadsave.
    main_log("Initializing saves...")
    renpy.savelocation.init()

    
    main_log("Trying to load event hooks...")
    try:
        renpy.renmodder.events.setup_event_hooks()
    except Exception as e:
        main_log(f"FAILED TO LOAD EVENT HOOKS, ERROR: {e}")

    try:
        # Init save slots and save tokens.
        renpy.loadsave.init()
        try:
            renpy.savetoken.upgrade_all_savefiles()
        except Exception: pass

        log_clock("Loading save slot metadata")

        # Load persistent data from all save locations.
        renpy.persistent.update()
        game.preferences = game.persistent._preferences
        log_clock("Loading persistent")

        # Clear the list of seen statements in this game.
        game.seen_session = { }

        # Initialize persistent variables.
        renpy.store.persistent = game.persistent # type: ignore
        renpy.store._preferences = game.preferences # type: ignore
        renpy.store._test = renpy.test.testast._test # type: ignore

        if renpy.parser.report_parse_errors():
            raise renpy.game.ParseErrorException()

        renpy.game.exception_info = 'While executing init code:'

        for id_, (_prio, node) in enumerate(game.script.initcode):

            renpy.game.initcode_ast_id = id_

            if isinstance(node, renpy.ast.Node):
                node_start = time.time()

                renpy.game.context().run(node)

                node_duration = time.time() - node_start

                if node_duration > renpy.config.profile_init:
                    renpy.display.log.write(" - Init at %s:%d took %.5f s.", node.filename, node.linenumber, node_duration)

            else:
                # An init function.
                node()

        renpy.game.exception_info = 'After initialization, but before game start.'

        # Check if we should simulate android.
#        renpy.android = renpy.android or renpy.config.simulate_android # @UndefinedVariable

        # Re-set up the logging.
        renpy.log.post_init()

        # Run the post init code, if any.
        for i in renpy.game.post_init:
            i()

        renpy.game.script.report_duplicate_labels()

        # Sort the images.
        renpy.display.image.image_names.sort()

        game.persistent._virtual_size = renpy.config.screen_width, renpy.config.screen_height # type: ignore

        log_clock("Running init code")

        renpy.pyanalysis.load_cache()
        log_clock("Loading analysis data")

        # Analyze the script and compile ATL.
        renpy.game.script.analyze()
        renpy.atl.compile_all()
        log_clock("Analyze and compile ATL")

        renpy.savelocation.init()
        renpy.loadsave.init()
        log_clock("Reloading save slot metadata")

        # Index the archive files. We should not have loaded an image
        # before this point. (As pygame will not have been initialized.)
        # We need to do this again because the list of known archives
        # may have changed.
        renpy.loader.index_archives()
        log_clock("Index archives")

        # Check some environment variables.
        renpy.game.less_memory = "RENPY_LESS_MEMORY" in os.environ
        renpy.game.less_mouse = "RENPY_LESS_MOUSE" in os.environ
        renpy.game.less_updates = "RENPY_LESS_UPDATES" in os.environ

        renpy.dump.dump(True)
        renpy.game.script.make_backups()
        log_clock("Dump and make backups")

        # Initialize image cache.
        renpy.display.im.cache.init()
        log_clock("Cleaning cache")

        # Make a clean copy of the store.
        renpy.python.make_clean_stores()
        log_clock("Making clean stores")

        # Init the keymap.
        renpy.display.behavior.init_keymap()

        gc.collect(2)

        if gc.garbage:
            del gc.garbage[:]

        if renpy.config.manage_gc:
            gc.set_threshold(*renpy.config.gc_thresholds)

            gc_debug = int(os.environ.get("RENPY_GC_DEBUG", 0))

            if renpy.config.gc_print_unreachable:
                gc_debug |= gc.DEBUG_SAVEALL

            gc.set_debug(gc_debug)

        else:
            gc.set_threshold(700, 10, 10)

        log_clock("Initial gc")

        # Start debugging file opens.
        renpy.debug.init_main_thread_open()

        # (Perhaps) Initialize graphics.
        if not game.interface:
            renpy.display.core.Interface()
            log_clock("Creating interface object")

        # Start things running.
        restart = None

        main_log(f"renpy.store._window: {renpy.store._window}")

        # main_log("Trying to load logo...")
        # global logo
        # logo = pygame.image.load(f"{os.getcwd()}/renpy/renmodder/logo.png")
        # presplash_log("Starting logo display thread...")
        # Thread(target=hook_update, args=(window.update, logo, window), daemon=True).run()

        # window.blit(logo, (0,0))
        # window.update()

        main_log("Starting loop...")
        while True:

            if restart:
                main_log("Should restart...")
                renpy.display.screen.before_restart()

            try:
                try:
                    main_log(f"renpy.store._window: {renpy.store._window}")
                    run(restart)
                finally:
                    restart = (renpy.config.end_game_transition, "_invoke_main_menu", "_main_menu")

            except renpy.game.QuitException:

                renpy.audio.audio.fadeout_all()
                raise

            except game.FullRestartException as e:
                restart = e.reason

            finally:

                main_log("Shutdowning...")
                renpy.persistent.update(True)
                renpy.persistent.save_on_quit_MP()

                # Reset live2d if it exists.
                try:
                    renpy.gl2.live2d.reset_states()
                except Exception:
                    pass

                # Flush any pending interface work.
                renpy.display.interface.finish_pending()

                # Give Ren'Py a couple of seconds to finish saving.
                renpy.loadsave.autosave_not_running.wait(3.0)

                # Run the at exit callbacks.
                for cb in renpy.config.at_exit_callbacks:
                    cb()

    finally:
        gc.set_debug(0)

        for i in renpy.config.quit_callbacks:
            i()

        main_log("Quiting...")
        renpy.loader.auto_quit()
        renpy.savelocation.quit()
        renpy.translation.write_updated_strings()

    # This is stuff we do on a normal, non-error return.
    if not renpy.display.error.error_handled:
        renpy.display.render.check_at_shutdown()
