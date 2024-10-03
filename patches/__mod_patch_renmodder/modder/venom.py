class Venom:
    def __init__(self) -> None:
        self.is_faked = False
        self.symlink_func = self.start

    def start(self, original_func) -> bool:
        return True
