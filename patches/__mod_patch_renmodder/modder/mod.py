# import renpy.renmodder.mod_api


class Mod:
    def __mod_log(self, text: str):
        print(f"[RENMODDER] [{self.name}] ={self.id}= {text}")

    def __init__(self) -> None:
        self.id = id(self)
        self.name = "Test mod"
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


