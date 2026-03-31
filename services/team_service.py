import validators.team_validator as team_validator
from models.team_model import Team, Stats
import falcon
from bson.objectid import ObjectId, InvalidId


#POST
def create_team(data, db):
    team_validator.validate_team_data(data)
    team_stats = Stats(**data["stats"])
    team = Team(name=data["name"], country=data["country"], stats=team_stats)

    result = db.teams.insert_one(team.to_dict())
    return str(result.inserted_id)


#GET ALL
def get_all_teams(db):
    teams = list(db.teams.find())

    for t in teams:
        t["_id"] = str(t["_id"])

    return teams


#GET BY ID
def get_team_by_id(team_id, db):
    
    try:
        team_id = ObjectId(team_id)
    except InvalidId:
        raise falcon.HTTPBadRequest(title="Invalid ID", description="Invalid team id")
    
    team = db.teams.find_one({"_id": team_id})
    
    if not team:
        raise falcon.HTTPNotFound(description="Team not found")
    
    team["_id"] = str(team["_id"])
    return team


#UPDATE BY ID
def update_team_by_id(team_id, data, db):    
    try:
        obj_id = ObjectId(team_id)
        print(f"DEBUG 2: ObjectId created: {obj_id}")
    except InvalidId:
        raise falcon.HTTPBadRequest(title="Invalid ID", description="Invalid team id")
    
    team_validator.validate_team_data(data, update=True)
    result = db.teams.update_one({"_id": obj_id}, {"$set": data})

    if result.matched_count == 0:
        raise falcon.HTTPNotFound(description="Team not found")

    team = db.teams.find_one({"_id": obj_id})
    team["_id"] = str(team["_id"])
    return team


# DELETE BY ID
def delete_team_by_id(team_id, db):
    try:
        obj_id = ObjectId(team_id)
    except InvalidId:
        raise falcon.HTTPBadRequest(title="Invalid ID", description="Invalid team id")
    
    team = db.teams.find_one({"_id": obj_id})
    if not team:
        raise falcon.HTTPNotFound(description="Team not found")
    
    # Check if team is in any tournament
    tournament = db.tournaments.find_one({"teams": obj_id})
    if tournament:
        raise falcon.HTTPConflict(
            title="Cannot Delete",
            description="Cannot delete team that is part of a tournament"
        )
    
    # Check if team has any people associated
    person = db.people.find_one({"team_id": obj_id})
    if person:
        raise falcon.HTTPConflict(
            title="Cannot Delete",
            description="Cannot delete team that has players or managers"
        )
    
    # Check if team is in any match (home_team or away_team)
    match = db.matches.find_one({
        "$or": [
            {"home_team.team_id": obj_id},
            {"away_team.team_id": obj_id}
        ]
    })
    if match:
        raise falcon.HTTPConflict(
            title="Cannot Delete",
            description="Cannot delete team that has matches"
        )
    
    # If no references found, proceed with deletion
    db.teams.delete_one({"_id": obj_id})
    team["_id"] = str(team["_id"])
    return team