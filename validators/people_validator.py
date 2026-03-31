import falcon
from utils import validate_exact_match, validate_required_fields

def validate_people_data(data):
    """Validate create based on person type"""
    person_type = data.get("type", "").strip()
    
    if not person_type:
        raise falcon.HTTPBadRequest(
            title="Missing Type",
            description="type field is required"
        )
    
    if person_type not in ["player", "manager"]:
        raise falcon.HTTPBadRequest(
            title="Invalid Type",
            description="type must be 'player' or 'manager'"
        )
    
    if person_type == "player":
        validate_player_create(data)
    else:
        validate_manager_create(data)


def validate_player_create(data):
    """Validate player creation"""
    required = ["type", "first_name", "last_name", "shirt_number"]
    optional = ["team_id", "attributes"]
    allowed = required + optional
    
    # Check extra fields
    for field in data:
        if field not in allowed:
            raise falcon.HTTPBadRequest(
                title="Extra fields",
                description=f"{field} is not allowed for players"
            )
    
    # Check required fields
    for field in required:
        if field not in data:
            raise falcon.HTTPBadRequest(
                title="Missing field",
                description=f"{field} is required for players"
            )
    
    # Validate types and values
    if not isinstance(data["type"], str) or data["type"].strip() != "player":
        raise falcon.HTTPBadRequest(
            title="Invalid Type",
            description="type must be 'player'"
        )
    
    if not isinstance(data["first_name"], str) or not data["first_name"].strip():
        raise falcon.HTTPBadRequest(
            title="Invalid First Name",
            description="first_name must be a non-empty string"
        )
    
    if not isinstance(data["last_name"], str) or not data["last_name"].strip():
        raise falcon.HTTPBadRequest(
            title="Invalid Last Name",
            description="last_name must be a non-empty string"
        )
    
    if not isinstance(data["shirt_number"], int) or data["shirt_number"] < 1:
        raise falcon.HTTPBadRequest(
            title="Invalid Shirt Number",
            description="shirt_number must be a positive integer"
        )
    
    if "team_id" in data:
        if not isinstance(data["team_id"], str) or not data["team_id"].strip():
            raise falcon.HTTPBadRequest(
                title="Invalid Team ID",
                description="team_id must be a non-empty string"
            )
    
    if "attributes" in data:
        validate_attributes(data["attributes"])


def validate_manager_create(data):
    """Validate manager creation"""
    required = ["type", "first_name", "last_name"]
    optional = ["team_id"]
    allowed = required + optional
    
    # Check extra fields
    for field in data:
        if field not in allowed:
            raise falcon.HTTPBadRequest(
                title="Extra fields",
                description=f"{field} is not allowed for managers"
            )
    
    # Check required fields
    for field in required:
        if field not in data:
            raise falcon.HTTPBadRequest(
                title="Missing field",
                description=f"{field} is required for managers"
            )
    
    # Validate types and values
    if not isinstance(data["type"], str) or data["type"].strip() != "manager":
        raise falcon.HTTPBadRequest(
            title="Invalid Type",
            description="type must be 'manager'"
        )
    
    if not isinstance(data["first_name"], str) or not data["first_name"].strip():
        raise falcon.HTTPBadRequest(
            title="Invalid First Name",
            description="first_name must be a non-empty string"
        )
    
    if not isinstance(data["last_name"], str) or not data["last_name"].strip():
        raise falcon.HTTPBadRequest(
            title="Invalid Last Name",
            description="last_name must be a non-empty string"
        )
    
    if "team_id" in data:
        if not isinstance(data["team_id"], str) or not data["team_id"].strip():
            raise falcon.HTTPBadRequest(
                title="Invalid Team ID",
                description="team_id must be a non-empty string"
            )


def validate_attributes(attributes):
    """Validate attributes dictionary"""
    if not isinstance(attributes, dict):
        raise falcon.HTTPBadRequest(
            title="Invalid Type",
            description="attributes must be a dictionary"
        )
    
    for key, value in attributes.items():
        if not isinstance(key, str) or not key.strip():
            raise falcon.HTTPBadRequest(
                title="Invalid Key",
                description="All keys in attributes must be non-empty strings"
            )
        if not isinstance(value, (int, float)):
            raise falcon.HTTPBadRequest(
                title="Invalid Value",
                description="All values in attributes must be integers or floats"
            )


def validate_people_update_data(data, partial=True):
    """Validate person update data"""
    if not data:
        raise falcon.HTTPBadRequest(
            title="Missing fields",
            description="At least one field must be provided for update"
        )
    
    # Determine person type from context or reject updates that change type
    if "type" in data:
        raise falcon.HTTPBadRequest(
            title="Invalid Update",
            description="Cannot update 'type' field"
        )
    
    # Only specific fields can be updated
    allowed_update_fields = {"team_id", "shirt_number", "attributes"}
    for field in data:
        if field not in allowed_update_fields:
            raise falcon.HTTPBadRequest(
                title="Invalid Field",
                description=f"Cannot update '{field}'. Only team_id, shirt_number, and attributes can be updated for players, or team_id for managers"
            )
    
    # Validate team_id if present
    if "team_id" in data:
        if not isinstance(data["team_id"], str) or not data["team_id"].strip():
            raise falcon.HTTPBadRequest(
                title="Invalid Team ID",
                description="team_id must be a non-empty string"
            )
    
    # Validate shirt_number if present (players only)
    if "shirt_number" in data:
        if not isinstance(data["shirt_number"], int) or data["shirt_number"] < 1:
            raise falcon.HTTPBadRequest(
                title="Invalid Shirt Number",
                description="shirt_number must be a positive integer"
            )
    
    # Validate attributes if present (players only)
    if "attributes" in data:
        validate_attributes(data["attributes"])