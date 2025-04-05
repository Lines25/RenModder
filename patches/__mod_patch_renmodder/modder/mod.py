# We can just add "global mod_api" and use it as mod_api
# import renpy.renmodder.mod_api


class Mod:
    def __mod_log(self, text: str):
        print(f"[{self.name}] {text}")

    def __init__(self) -> None:
        self.id = id(self)
        self.name = "NO NAME"
        self.sys_name = f"no.name.{self.id}"
        self.version = 1.0

    def event(self, event_type: str, event_args: set or None):
        self.__mod_log(f"Event {event_type} with args {event_args}")

    def tick(self):
        self.__mod_log("Ticking...")

    def bootstrap(self):
        self.__mod_log("BOOTSTRAPing...")
    
    def bootstrap_end(self):
        self.__mod_log("END BOOTSTRAPing...")

    def main(self):
        self.__mod_log("Running in main()...")

    def main_end(self):
        self.__mod_log("Running in main() at the end...")

    def unload(self):
        self.__mod_log("Unloading...")


