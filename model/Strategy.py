class Strategy:

    def __init__(self, name: str, script: str, version: int):
        self._name = name
        self._script = script
        self._version = version

    @property
    def name(self) -> str:
        return self._name

    @property
    def script(self) -> str:
        return self._script

    @property
    def version(self) -> int:
        return self._version

    def __repr__(self):
        return "%s(%s, %s..., %d)" % (self.__class__.__qualname__,
                                      self.name,
                                      self.script[:20],
                                      self.version)
