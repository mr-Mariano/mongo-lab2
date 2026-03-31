import falcon
from utils import validate_exact_match, validate_required_fields


REQUIRED_FIELDS = ["name", "country", "total_match_days"]
OPTIONAL_FIELDS = ["teams", "winner_team_id"]


def validate_tournament_data(data):
    validate_fields(data)
    validate_types(data)
    if "teams" in data:
        validate_teams(data["teams"])


def validate_fields(data):
    # Allow required + optional (no extra fields)
    allowed_fields = REQUIRED_FIELDS + OPTIONAL_FIELDS
    validate_exact_match(allowed_fields, data)

    # Required fields must exist
    validate_required_fields(REQUIRED_FIELDS, data)


def validate_types(data):
    if not isinstance(data["name"], str) or not data["name"].strip() or data["name"].isdigit():
        raise falcon.HTTPBadRequest(
            title="Invalid Type",
            description="Name must be a non-empty string and cannot be only numbers."
        )

    if not isinstance(data["country"], str) or not data["country"].strip() or data["country"].isdigit():
        raise falcon.HTTPBadRequest(
            title="Invalid Type",
            description="Country must be a non-empty string and cannot be only numbers."
        )

    if "teams" in data:
        if not isinstance(data["teams"], list):
            raise falcon.HTTPBadRequest(
                title="Invalid Type",
                description="Teams must be a list."
            )

    if not isinstance(data["total_match_days"], int):
        raise falcon.HTTPBadRequest(
            title="Invalid Type",
            description="Total Match Days must be an integer."
        )

    # Optional field
    winner = data.get("winner_team_id")
    if winner is not None:
        if not isinstance(winner, str) or not winner.strip():
            raise falcon.HTTPBadRequest(
                title="Invalid Type",
                description="Winner Team Id must be a non-empty string or None."
            )


def validate_teams(teams):
    for team in teams:
        if not isinstance(team, str) or not team.strip():
            raise falcon.HTTPBadRequest(
                title="Invalid Type",
                description=f"'{team}' must be a non-empty string (team name or id)."
            )


def validate_partial_tournament_data(data):
    allowed_fields = ["name", "country", "teams", "winner_team_id"]

    # Check for extra fields
    for field in data:
        if field not in allowed_fields:
            raise falcon.HTTPBadRequest(
                title="Extra fields",
                description=f"{field} is not allowed in updates. Only 'name', 'country', 'teams', and 'winner_team_id' are allowed."
            )
    
    # At least one field required
    if not data:
        raise falcon.HTTPBadRequest(
            title="Missing fields",
            description="At least one of the following fields is required: name, country, teams, winner_team_id."
        )

    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip() or data["name"].isdigit():
            raise falcon.HTTPBadRequest(
                title="Invalid Type",
                description="Name must be a non-empty string and cannot be only numbers."
            )

    if "country" in data:
        if not isinstance(data["country"], str) or not data["country"].strip() or data["country"].isdigit():
            raise falcon.HTTPBadRequest(
                title="Invalid Type",
                description="Country must be a non-empty string and cannot be only numbers."
            )

    if "teams" in data:
        if not isinstance(data["teams"], list):
            raise falcon.HTTPBadRequest(
                title="Invalid Type",
                description="Teams must be a list."
            )

        for team in data["teams"]:
            if not isinstance(team, str) or not team.strip():
                raise falcon.HTTPBadRequest(
                    title="Invalid Type",
                    description=f"'{team}' must be a non-empty string (team name or id)."
                )

    if "winner_team_id" in data:
        winner = data["winner_team_id"]

        if winner is not None:
            if not isinstance(winner, str) or not winner.strip():
                raise falcon.HTTPBadRequest(
                    title="Invalid Type",
                    description="Winner Team Id must be a non-empty string or None."
                )

    return data

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
    
    # Validate individual fields if provided
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