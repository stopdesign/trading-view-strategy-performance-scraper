class Strategy:

    def __init__(self, strategy_id: str, name: str, script: str, version: int):
        self._strategy_id = strategy_id
        self._name = name
        self._script = script
        self._version = version

    @property
    def id(self) -> str:
        return self._strategy_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def script(self) -> str:
        return self._script

    @property
    def version(self) -> int:
        return self._version

    @classmethod
    def from_mongo_server_response(cls, data: dict):
        return cls(
            strategy_id=data["_id"],
            name=data["name"],
            script=data["script"],
            version=data["version"]
        )

    def __repr__(self):
        return "%s(%s, %s, %s..., %d)" % (self.__class__.__qualname__,
                                          self.id,
                                          self.name,
                                          self.script[:20],
                                          self.version)
