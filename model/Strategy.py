from dataclasses import dataclass


@dataclass
class Strategy:
    strategy_id: str
    name: str
    script: str
    version: int

    @classmethod
    def from_mongo_server_response(cls, data: dict):
        return cls(
            strategy_id=data["_id"],
            name=data["name"],
            script=data["script"],
            version=data["version"]
        )
