class Strategy:

    def __init__(self, name: str, script: str):
        self._name = name
        self._script = script

    @property
    def name(self):
        return self._name

    @property
    def script(self):
        return self._script
