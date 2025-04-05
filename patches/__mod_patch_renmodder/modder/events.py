EVENT_INPUT = 0x01                # When input field shows
EVENT_BUTTON_PRESSED = 0x02       # When button was pressed by player 
EVENT_SKIP_ENABLED = 0x03         # When SKIP mode enabled
EVENT_TEXT_SKIPPED = 0x04         # When text is slowly showing and player presses btn to instant get it all
EVENT_CHOICE_MADE = 0x05          # When player selects an option in choice menu
EVENT_SCENE_CHANGED = 0x06        # When background scene/location changes
EVENT_CHARACTER_SHOWN = 0x07      # When character sprite appears on screen
EVENT_CHARACTER_HIDDEN = 0x08     # When character sprite is removed
EVENT_MUSIC_CHANGED = 0x09        # When background music changes
EVENT_SOUND_PLAYED = 0x0A         # When sound effect is played
EVENT_SAVE_CREATED = 0x0B         # When player creates a save
EVENT_SAVE_LOADED = 0x0C          # When save file is loaded
EVENT_MENU_OPENED = 0x0D          # When game menu is opened (save/load/preferences)
EVENT_MENU_CLOSED = 0x0E          # When game menu is closed
EVENT_DIALOG_STARTED = 0x0F       # When new dialog/text block begins

if not 'last_events' in globals().keys():
    global last_events
    last_events = []

def trigger_event(event_type):
    last_events.append(event_type)

def setup_event_hooks():
    """Set up hooks for all the events into Ren'Py's systems"""
    import renpy
    
    # # Hook into input events
    original_input = renpy.display.behavior.Input
    class InputHook(original_input):
        def render(self, *args, **kwargs):
            trigger_event(EVENT_INPUT)
            return super().render(*args, **kwargs)
    renpy.display.behavior.Input = InputHook

    # # Hook into button events
    # original_button = renpy.display.behavior.Button
    # class ButtonHook(original_button):
    #     def clicked(self):
    #         trigger_event(EVENT_BUTTON_PRESSED)
    #         return super().clicked()
    # renpy.display.behavior.Button = ButtonHook

    # # Hook into skip mode
    # original_skipping = renpy.config.skipping
    # def skipping_hook(enable):
    #     if enable:
    #         trigger_event(EVENT_SKIP_ENABLED)
    #     original_skipping(enable)
    # renpy.config.skipping = skipping_hook

    # # Hook into scene changes
    # original_scene = renpy.exports.scene
    # def scene_hook(*args, **kwargs):
    #     trigger_event(EVENT_SCENE_CHANGED)
    #     return original_scene(*args, **kwargs)
    # renpy.exports.scene = scene_hook

    # # Hook into character showing/hiding
    # original_show = renpy.exports.show
    # def show_hook(*args, **kwargs):
    #     trigger_event(EVENT_CHARACTER_SHOWN)
    #     return original_show(*args, **kwargs)
    # renpy.exports.show = show_hook

    # original_hide = renpy.exports.hide
    # def hide_hook(*args, **kwargs):
    #     trigger_event(EVENT_CHARACTER_HIDDEN)
    #     return original_hide(*args, **kwargs)
    # renpy.exports.hide = hide_hook

    # # Hook into music/sound
    # original_music_start = renpy.audio.music.play
    # def music_hook(*args, **kwargs):
    #     trigger_event(EVENT_MUSIC_CHANGED)
    #     return original_music_start(*args, **kwargs)
    # renpy.audio.music.play = music_hook

    # original_sound_play = renpy.audio.sound.play
    # def sound_hook(*args, **kwargs):
    #     trigger_event(EVENT_SOUND_PLAYED)
    #     return original_sound_play(*args, **kwargs)
    # renpy.audio.sound.play = sound_hook

    # # Hook into save/load
    # original_save = renpy.loadsave.save
    # def save_hook(*args, **kwargs):
    #     trigger_event(EVENT_SAVE_CREATED)
    #     return original_save(*args, **kwargs)
    # renpy.loadsave.save = save_hook

    # original_load = renpy.loadsave.load
    # def load_hook(*args, **kwargs):
    #     trigger_event(EVENT_SAVE_LOADED)
    #     return original_load(*args, **kwargs)
    # renpy.loadsave.load = load_hook

    # # Hook into menu events
    # original_show_menu = renpy.game.interface.show_menu
    # def show_menu_hook(*args, **kwargs):
    #     trigger_event(EVENT_MENU_OPENED)
    #     return original_show_menu(*args, **kwargs)
    # renpy.game.interface.show_menu = show_menu_hook

    # original_hide_menu = renpy.game.interface.hide_menu
    # def hide_menu_hook(*args, **kwargs):
    #     trigger_event(EVENT_MENU_CLOSED)
    #     return original_hide_menu(*args, **kwargs)
    # renpy.game.interface.hide_menu = hide_menu_hook

    # # Hook into dialogue
    # original_say = renpy.character.say
    # def say_hook(*args, **kwargs):
    #     trigger_event(EVENT_DIALOG_STARTED)
    #     return original_say(*args, **kwargs)
    # renpy.character.say = say_hook

    # # Hook into text skipping
    # original_fast_skip = renpy.display.screen.fast_skip
    # def fast_skip_hook(*args, **kwargs):
    #     trigger_event(EVENT_TEXT_SKIPPED)
    #     return original_fast_skip(*args, **kwargs)
    # renpy.display.screen.fast_skip = fast_skip_hook

    # # Hook into choice selection
    # original_choice = renpy.display.screen.choice
    # def choice_hook(*args, **kwargs):
    #     trigger_event(EVENT_CHOICE_MADE)
    #     return original_choice(*args, **kwargs)
    # renpy.display.screen.choice = choice_hook