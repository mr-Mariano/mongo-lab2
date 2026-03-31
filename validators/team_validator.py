import falcon
from utils import validate_exact_match, validate_required_fields

REQUIRED_FIELDS = ["name", "country", "stats"]
STATS_FIELDS = ["wins", "draws", "losses", "goals_in_favor", "goals_against"]


def validate_team_data(data, update=False):
    if update:
        validate_team_data_update(data)
    else:
        validate_required_fields_teams(data)
        validate_stats_fields(data)


def validate_team_data_update(data):
    """Validate team update - only name and country allowed"""
    allowed_fields = ["name", "country"]
    
    # Check for extra fields
    for field in data:
        if field not in allowed_fields:
            raise falcon.HTTPBadRequest(
                title="Extra fields",
                description=f"{field} is not allowed in updates. Only 'name' and 'country' are allowed."
            )
    
    # At least one field required
    if not data:
        raise falcon.HTTPBadRequest(
            title="Missing fields",
            description="At least one of the following fields is required: name, country."
        )
    
    # Validate name if present
    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip() or data["name"].isdigit():
            raise falcon.HTTPBadRequest(
                title="Invalid Type",
                description="Name must be a non-empty string"
            )
    
    # Validate country if present
    if "country" in data:
        if not isinstance(data["country"], str) or not data["country"].strip() or data["country"].isdigit():
            raise falcon.HTTPBadRequest(
                title="Invalid Type",
                description="Country must be a non-empty string"
            )


def validate_required_fields_teams(data, partial=False):
    for field in data:
        if field not in REQUIRED_FIELDS:
            raise falcon.HTTPBadRequest(title="Extra fields",
                                        description=f"{field} is an extra field not valid for team.")

    if "name" in data and (not isinstance(data["name"], str) or not data["name"].strip() or data["name"].isdigit()):
        raise falcon.HTTPBadRequest(title="Invalid Type",
                                    description="Name field needs to be of a string type")
    if "country" in data and (not isinstance(data["country"], str) or not data["country"].strip() or data["country"].isdigit()):
        raise falcon.HTTPBadRequest(title="Invalid Type",
                                    description="Country field needs to be of a string type")
    if "stats" in data and not isinstance(data["stats"], dict):
        raise falcon.HTTPBadRequest(title="Invalid Type",
                                    description="Stats field needs to be of a dictionary type")


def validate_stats_fields(data):
    for field in data["stats"]:
        if field not in STATS_FIELDS:
            raise falcon.HTTPBadRequest(title="Extra fields",
                                        description=f"{field} is an extra field not valid in stats.")

    for field in STATS_FIELDS:
        if field not in data["stats"]:
            raise falcon.HTTPBadRequest(title="Missing field",
                                        description=f"stats.{field} is required inside stats dictionary.")
        if not isinstance(data["stats"][field], int):
            raise falcon.HTTPBadRequest(title="Invalid Type",
                                        description=f"stats.{field} needs to be an integer.")