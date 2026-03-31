from bson.objectid import ObjectId


class Tournament:
    def __init__(
        self,
        name: str,
        country: str,
        teams: list[ObjectId],
        total_match_days: int,
        winner_team_id: ObjectId | None = None
    ):
        self.name = name
        self.country = country
        self.teams = teams
        self.total_match_days = total_match_days
        self.winner_team_id = winner_team_id

    def to_dict(self):
        return {
            "name": self.name,
            "country": self.country,
            "teams": self.teams,
            "total_match_days": self.total_match_days,
            "winner_team_id": self.winner_team_id
        }