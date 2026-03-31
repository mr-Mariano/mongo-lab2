from bson import ObjectId

class Person:
    def __init__(self, type: str,
                        first_name: str,
                        last_name: str,
                        team_id : ObjectId | None = None,
                        shirt_number : int | None = None,
                        attributes : dict | None = None):
        self.type = type
        self.first_name = first_name
        self.last_name = last_name
        self.team_id = team_id
        self.shirt_number = shirt_number
        self.attributes = attributes or {}


    def to_dict(self):
        data = {
            "type": self.type,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "team_id": self.team_id,
        }

        # Si es player, el servicio garantiza que shirt_number y attributes existen
        if self.type == "player":
            data["shirt_number"] = self.shirt_number
            data["attributes"] = self.attributes

        return data