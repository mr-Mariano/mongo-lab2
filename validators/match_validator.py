import falcon
from utils import validate_exact_match, validate_required_fields

REQUIRED_FIELDS = ["tournament_id", "match_day", "date",
                   "home_team", "away_team", "mvp_player_id",
                   "stats", "player_stats"]

TEAMS_FIELDS = ["team_id", "name", "goals"]
STATS_FIELD = ["possession", "shots_on_target", "corners", "fouls"]
PLAYER_STATS_FIELDS = ["player_id", "goals", "assists", "shots_on_target", "minutes_played"]


"""
{
    tournament_id: ObjectId, // reference
    match_day: Number,
    date: Date,
    home_team: {
        team_id: ObjectId,
        name: String, // duplicated for faster reads
        goals: Number
    },
    away_team: {
        team_id: ObjectId,
        name: String, // duplicated
        goals: Number
    },
    mvp_player_id: ObjectId, // reference
    stats: {
        possession: { home: Number, away: Number },
        shotsOnTarget: { home: Number, away: Number },
        corners: { home: Number, away: Number },
        fouls: { home: Number, away: Number }
    },
    player_stats: [ // Bucket Pattern
        {
        playerId: ObjectId,
        goals: Number,
        assists: Number,
        shotsOnTarget: Number,
        minutesPlayed: Number
    }]
}
"""

def validate_match_data(data):
    validate_required_fields_match(data)
    

def validate_required_fields_match(data):
    # Validate the fields in data are just the exact match
    validate_exact_match(REQUIRED_FIELDS, data)
    validate_required_fields(REQUIRED_FIELDS, data)

    if not isinstance(data["match_day"], int):
        raise falcon.HTTPBadRequest(title="Invalid Type",
                                    description="match_day field needs to be of an integer type.")
    if not isinstance(data["date"], str) or not data["date"].strip():
        raise falcon.HTTPBadRequest(title="Invalid Type",
                                    description="date field needs to be of a non-empty string type.")
    if not isinstance(data["home_team"], dict):
        raise falcon.HTTPBadRequest(title="Invalid Type",
                                    description="home_team field needs to be of a dictionary type.")
    if not isinstance(data["away_team"], dict):
        raise falcon.HTTPBadRequest(title="Invalid Type",
                                    description="away_team field needs to be of a dictionary type.")
    if not isinstance(data["stats"], dict):
        raise falcon.HTTPBadRequest(title="Invalid Type",
                                    description="stats field needs to be of a dictionary type.")
    if not isinstance(data["player_stats"], list):
        raise falcon.HTTPBadRequest(title="Invalid Type",
                                    description="player_stats field needs to be of a list type.")

    validate_team_data(data["home_team"], "home_team")
    validate_team_data(data["away_team"], "away_team")
    validate_stats(data["stats"])
    validate_player_stats(data["player_stats"])


def validate_team_data(team_data, field_name):
    validate_exact_match(TEAMS_FIELDS, team_data)

    if not isinstance(team_data["team_id"], str) or not team_data["team_id"].strip():
        raise falcon.HTTPBadRequest(title="Invalid Type",
                                    description=f"{field_name}.team_id field needs to be a non-empty string.")
    if not isinstance(team_data["name"], str) or not team_data["name"].strip():
        raise falcon.HTTPBadRequest(title="Invalid Type",
                                    description=f"{field_name}.name field needs to be a non-empty string.")
    if not isinstance(team_data["goals"], int):
        raise falcon.HTTPBadRequest(title="Invalid Type",
                                    description=f"{field_name}.goals field needs to be of an integer type.")
    
def validate_stats(stats):
    validate_exact_match(STATS_FIELD, stats)

    for stat in STATS_FIELD:
        if stat not in stats:
            raise falcon.HTTPBadRequest(title="Missing Field",
                                        description=f"{stat} field is required in stats.")
        if not isinstance(stats[stat], dict):
            raise falcon.HTTPBadRequest(title="Invalid Type",
                                        description=f"{stat} field needs to be of a dictionary type.")
        if "home" not in stats[stat] or "away" not in stats[stat]:
            raise falcon.HTTPBadRequest(title="Missing Field",
                                        description=f"home and away fields are required in {stat}.")
        if not isinstance(stats[stat]["home"], int) or not isinstance(stats[stat]["away"], int):
            raise falcon.HTTPBadRequest(title="Invalid Type",
                                        description=f"home and away fields in {stat} need to be of an integer type.")


def validate_player_stats(player_stats):
    for idx, player_stat in enumerate(player_stats):
        validate_exact_match(PLAYER_STATS_FIELDS, player_stat)

        if not isinstance(player_stat["player_id"], str) or not player_stat["player_id"].strip():
            raise falcon.HTTPBadRequest(title="Invalid Type",
                                        description=f"player_stats[{idx}].player_id field needs to be a non-empty string.")
        if not isinstance(player_stat["goals"], int):
            raise falcon.HTTPBadRequest(title="Invalid Type",
                                        description=f"player_stats[{idx}].goals field needs to be of an integer type.")
        if not isinstance(player_stat["assists"], int):
            raise falcon.HTTPBadRequest(title="Invalid Type",
                                        description=f"player_stats[{idx}].assists field needs to be of an integer type.")
        if not isinstance(player_stat["shots_on_target"], int):
            raise falcon.HTTPBadRequest(title="Invalid Type",
                                        description=f"player_stats[{idx}].shots_on_target field needs to be of an integer type.")
        if not isinstance(player_stat["minutes_played"], int):
            raise falcon.HTTPBadRequest(title="Invalid Type",
                                        description=f"player_stats[{idx}].minutes_played field needs to be of an integer type.")



def validate_match_update_data(data):
    """Validate match update - only allow mvp_player_id, stats, player_stats, date"""
    if not data:
        raise falcon.HTTPBadRequest(
            title="Missing fields",
            description="At least one field must be provided for update"
        )
    
    ALLOWED_UPDATE_FIELDS = {"mvp_player_id", "stats", "player_stats", "date"}
    
    for field in data:
        if field not in ALLOWED_UPDATE_FIELDS:
            raise falcon.HTTPBadRequest(
                title="Invalid Field",
                description=f"Cannot update '{field}'. Only mvp_player_id, stats, player_stats, and date can be updated"
            )
    
    if "date" in data:
        if not isinstance(data["date"], str) or not data["date"].strip():
            raise falcon.HTTPBadRequest(
                title="Invalid Type",
                description="date must be a non-empty string"
            )
    
    if "stats" in data:
        validate_stats(data["stats"])
    
    if "player_stats" in data:
        if not isinstance(data["player_stats"], list):
            raise falcon.HTTPBadRequest(
                title="Invalid Type",
                description="player_stats must be a list"
            )
        validate_player_stats(data["player_stats"])