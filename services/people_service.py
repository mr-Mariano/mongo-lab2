from validators import people_validator
from models.people_model import Person
from bson.objectid import ObjectId, InvalidId
import falcon


# POST
def create_people(data, db):
    teams_map = get_teams_map_name_id(db)  # ← Changed: now maps name → ObjectId
    print(f"DEBUG: teams_map = {teams_map}")
    team_ids = set(teams_map.values())

    people_validator.validate_people_data(data)
    print(f"DEBUG: validated data = {data}")
    resolved_data = resolve_team_reference(data, teams_map, team_ids)
    print(f"DEBUG: resolved_data = {resolved_data}")

    people = Person(**resolved_data)
    result = db.people.insert_one(people.to_dict())
    return str(result.inserted_id)


# GET ALL
def get_all_people(db):
    people = list(db.people.find())
    teams_map = get_teams_map_id_name(db) 
    
    for p in people:
        p["_id"] = str(p["_id"])
        if p["team_id"] in teams_map:
            p["team_id"] = teams_map[p["team_id"]]
        else:
            p["team_id"] = str(p["team_id"])
    
    return people



# GET BY ID
def get_people_by_id(people_id, db):
    try:
        people_id = ObjectId(people_id)
    except InvalidId:
        raise falcon.HTTPBadRequest(title="Invalid ID", description="Invalid people id")

    people = db.people.find_one({"_id": people_id})

    if not people:
        raise falcon.HTTPNotFound(description="Person not found")

    people["_id"] = str(people["_id"])

    team = db.teams.find_one({"_id": people["team_id"]})
    if team:
        people["team_id"] = team["name"]
    else:
        people["team_id"] = str(people["team_id"])
    
    return people



# UPDATE BY ID
def update_people_by_id(people_id, data, db):
    try:
        people_id = ObjectId(people_id)
    except InvalidId:
        raise falcon.HTTPBadRequest(title="Invalid ID", description="Invalid people id")

    teams_map = get_teams_map_name_id(db)
    team_ids = set(teams_map.values())

    people_validator.validate_people_update_data(data, partial=True)
    resolved_data = resolve_team_reference(data, teams_map, team_ids)

    result = db.people.update_one({"_id": people_id}, {"$set": resolved_data})

    if result.matched_count == 0:
        raise falcon.HTTPNotFound(description="Person not found")

    return get_people_by_id(people_id, db)

# DELETE BY ID
def delete_people_by_id(people_id, db):
    try:
        people_id = ObjectId(people_id)
    except InvalidId:
        raise falcon.HTTPBadRequest(title="Invalid ID", description="Invalid people id")

    # Check if person exists
    person = db.people.find_one({"_id": people_id})
    if not person:
        raise falcon.HTTPNotFound(description="Person not found")
    
    # Check if person is MVP in any match
    mvp_match = db.matches.find_one({"mvp_player_id": people_id})
    if mvp_match:
        raise falcon.HTTPConflict(
            title="Cannot Delete",
            description="Cannot delete person who is MVP in a match"
        )
    
    # Check if person appears in player_stats of any match
    stats_match = db.matches.find_one({"player_stats": {"$elemMatch": {"player_id": people_id}}})
    if stats_match:
        raise falcon.HTTPConflict(
            title="Cannot Delete",
            description="Cannot delete person who has player statistics in a match"
        )
    
    # If no references found, proceed with deletion
    result = db.people.delete_one({"_id": people_id})

    if result.deleted_count == 0:
        raise falcon.HTTPNotFound(description="Person not found")
    
    return True


# ---------- Helpers ----------
def get_teams_map_name_id(db):
    """Map team names to ObjectIds (for create operations)"""
    teams = db.teams.find({}, {"name": 1})
    return {team["name"]: team["_id"] for team in teams}


def get_teams_map_id_name(db):
    """Map ObjectIds to team names (for read operations)"""
    teams = db.teams.find({}, {"name": 1})
    return {team["_id"]: team["name"] for team in teams}


def resolve_team_reference(data, teams_map, team_ids):
    team = data.get("team_id")

    if team is None:
        return data

    if team in teams_map:
        team_id = teams_map[team]
    else:
        try:
            team_id = ObjectId(team)

            if team_id not in team_ids:
                raise falcon.HTTPBadRequest(
                    title="Invalid Team",
                    description=f"{team} is not a valid team id"
                )

        except InvalidId:
            raise falcon.HTTPBadRequest(
                title="Invalid Team",
                description=f"{team} is not a valid team name or id"
            )

    return {**data, "team_id": team_id}