from dataclasses import dataclass


@dataclass
class Strategy:
    id: str
    name: str
    script: str
    version: int

    @classmethod
    def from_mongo_server_response(cls, data: dict):
        return cls(
            id=data["_id"],
            name=data["name"],
            script=data["script"],
            version=data["version"]
        )

    def to_json(self) -> dict:
        return {
            "_id": self.id
        }
