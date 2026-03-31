"""
{
    "tournament_id": "Bundesliga",
    "match_day": 1,
    "date": "2024-01-13",
    "home_team": {
      "team_id": "Bayern Munich",
      "name": "Bayern Munich",
      "goals": 3
    },
    "away_team": {
      "team_id": "Borussia Dortmund",
      "name": "Borussia Dortmund",
      "goals": 2
    },
    "mvp_player_id": "Jamal Musiala",
    "stats": {
      "possession": { "home": 62, "away": 38 },
      "shots_on_target": { "home": 8, "away": 5 },
      "corners": { "home": 5, "away": 2 },
      "fouls": { "home": 12, "away": 14 }
    },
    "player_stats": [
      {
        "player_id": "Jamal Musiala",
        "goals": 2,
        "assists": 0,
        "shots_on_target": 6,
        "minutes_played": 90
      },
      {
        "player_id": "Kingsley Coman",
        "goals": 1,
        "assists": 1,
        "shots_on_target": 3,
        "minutes_played": 87
      },
      {
        "player_id": "Florian Wirtz",
        "goals": 1,
        "assists": 0,
        "shots_on_target": 4,
        "minutes_played": 90
      },
      {
        "player_id": "Gregor Kobel",
        "goals": 0,
        "assists": 0,
        "shots_on_target": 0,
        "minutes_played": 90
      }
    ]
  },
"""
from bson import ObjectId

class TeamInfo:
    def __init__(self, team_id: ObjectId, name: str, goals: int):
        self.team_id = team_id
        self.name = name
        self.goals = goals

    def to_dict(self):
        return {
            "team_id": self.team_id,
            "name": self.name,
            "goals": self.goals
        }

class Balance:
    def __init__(self, home: int, away: int):
        self.home = home
        self.away = away

    def to_dict(self):
        return {
            "home": self.home,
            "away": self.away
        }


class Stats:
    def __init__(self, possession: Balance, shots_on_target: Balance, corners: Balance, fouls: Balance):
        self.possession = possession
        self.shots_on_target = shots_on_target
        self.corners = corners
        self.fouls = fouls
        
    def to_dict(self):
        return {
            "possession": self.possession.to_dict(),
            "shots_on_target": self.shots_on_target.to_dict(),
            "corners": self.corners.to_dict(),
            "fouls": self.fouls.to_dict()
        }
    
class Player:
    def __init__(self, player_id: ObjectId, goals: int, assists: int, shots_on_target: int, minutes_played: int):
        self.player_id = player_id
        self.goals = goals
        self.assists = assists
        self.shots_on_target = shots_on_target
        self.minutes_played = minutes_played
    
    def to_dict(self):
        return {
            "player_id": self.player_id,
            "goals": self.goals,
            "assists": self.assists,
            "shots_on_target": self.shots_on_target,
            "minutes_played": self.minutes_played
        }

class Match:
    def __init__(self, tournament_id: ObjectId,
                        match_day: int,
                        date: str,
                        home_team: TeamInfo,
                        away_team: TeamInfo,
                        mvp_player_id: ObjectId,
                        stats: Stats,
                        player_stats: list[Player]):
        self.tournament_id = tournament_id
        self.match_day = match_day
        self.date = date
        self.home_team = home_team
        self.away_team = away_team
        self.mvp_player_id = mvp_player_id
        self.stats = stats or Stats(Balance(0, 0), Balance(0, 0), Balance(0, 0), Balance(0, 0))
        self.player_stats = player_stats or []


    def to_dict(self):
        return {
            "tournament_id": self.tournament_id,
            "match_day": self.match_day,
            "date": self.date,
            "home_team": self.home_team.to_dict(),
            "away_team": self.away_team.to_dict(),
            "mvp_player_id": self.mvp_player_id,
            "stats": self.stats.to_dict(),
            "player_stats": [player.to_dict() for player in self.player_stats]
        }