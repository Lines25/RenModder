from .venom import Venom
import pygame_sdl2 # type: ignore
import os
import renpy # type: ignore
import sys
from threading import Thread  # noqa: F401
from time import time, sleep  # noqa: F401

def find_file(base_name, root):
    allowed_exts = [ ".png", ".jpg" ]
    for ext in allowed_exts:
        fn = os.path.join(root, base_name + ext)
        if os.path.exists(fn):
            return fn
    return None

def presplash_log(text: str, write_to=sys.stdout):
    print(f"[RENMODDER] PRESPLASH: {text}", file=write_to)



class ProgressBar(object):

    def __init__(self, foreground, background):
        super(ProgressBar, self).__init__()
        self.foreground = pygame_sdl2.image.load(foreground)
        self.background = pygame_sdl2.image.load(background)
        self.width, self.height = self.background.get_size()

    def convert_alpha(self, surface=None):
        self.foreground = self.foreground.convert_alpha(surface)
        self.background = self.background.convert_alpha(surface)

    def get_size(self):
        return (self.width, self.height)

    def get_at(self, pos):
        return self.background.get_at(pos)

    def draw(self, target, done):
        width = self.width * min(done, 1)
        foreground = self.foreground.subsurface(0, 0, width, self.height)
        target.blit(self.background, (0, 0))
        target.blit(foreground, (0, 0))

class PresplashVenom(Venom):
    def __init__(self):
        super().__init__()

    def start(self, basedir, gamedir):
        if "RENPY_LESS_UPDATES" in os.environ:
            return
        gamedir = "E:\\StarryFlowers-1.7.0-pc\\game\\"

        presplash_fn = find_file("presplash", root=gamedir)

        sys.setprofile(profiler)

        if not presplash_fn:
            foreground_fn = find_file("presplash_foreground", root=gamedir)
            background_fn = find_file("presplash_background", root=gamedir)

            if not foreground_fn or not background_fn:
                return

        if renpy.windows:
            presplash_log("Detected Windows, setting DPI...")

            import ctypes

            ctypes.windll.user32.SetProcessDPIAware() # type: ignore

        presplash_log("Initializing pygame_sdl2.display module...")
        pygame_sdl2.display.init()

        global progress_bar

        if presplash_fn:
            presplash = pygame_sdl2.image.load(presplash_fn)
        else:
            presplash = renpy.display.presplash.ProgressBar(foreground_fn, background_fn) # type: ignore
            progress_bar = presplash

        global window

        bounds = pygame_sdl2.display.get_display_bounds(0)

        sw, sh = presplash.get_size()
        x = bounds[0] + bounds[2] // 2 - sw // 2
        y = bounds[1] + bounds[3] // 2 - sh // 2

        if presplash.get_at((0, 0))[3] == 0:
            shape = presplash
        else:
            shape = None

        if isinstance(shape, renpy.display.presplash.ProgressBar):
            shape = shape.background

        presplash_log("Initializing window...")
        window = pygame_sdl2.display.Window(
            sys.argv[0],
            (sw, sh),
            flags=pygame_sdl2.WINDOW_BORDERLESS,
            pos=(x, y),
            shape=shape)

        presplash_log("Drawing presplash...")
        if presplash_fn:
            presplash = presplash.convert_alpha(window.get_surface())
            window.get_surface().blit(presplash, (0, 0))
        else:
            presplash.convert_alpha(window.get_surface())
            presplash.draw(window.get_surface(), 0)


        presplash_log("All done, updating window and returning None")
        presplash_log("Trying to load logo...")
        global logo
        logo = pygame.image.load(find_file("logo", gamedir))  # noqa: F821
        # presplash_log("Starting logo display thread...")
        # Thread(target=hook_update, args=(window.update, logo, window), daemon=True).run()

        window.update()
        
        return window

def profiler(frame, event, args):
    global window

    # if event == 'call':
    #     presplash_log(f"Function is calling: frame: {frame}")

def window_update_logo(window):
    global x,y
    window.get_surface().blit(pygame.Rect(x,y), (x/2,y/2))  # noqa: F821
    window.update()

def hook_update(self, window):
    global logo
    start = time()  # noqa: F841
    real_update = window.update
    while True:
        # if time() - start >= 3000:
        if False:
            window.update = real_update
            break
        window.update = window_update_logo
