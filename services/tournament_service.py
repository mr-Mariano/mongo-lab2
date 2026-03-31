from validators.tournament_validator import validate_tournament_data, validate_partial_tournament_data
from models.tournament_model import Tournament

from bson.objectid import ObjectId
from bson.errors import InvalidId
import falcon


# ---------- HELPERS ----------

def get_teams_map_name_id(db):
    teams = db.teams.find({}, {"name": 1})
    return {team["name"]: team["_id"] for team in teams}


def get_teams_map_id_name(db):
    teams = db.teams.find({}, {"name": 1})
    return {team["_id"]: team["name"] for team in teams}

def resolve_team_references(data, teams_map, team_ids):
    validated_ids = []

    for team in data["teams"]:
        if team in teams_map:
            validated_ids.append(teams_map[team])
        else:
            try:
                obj_id = ObjectId(team)

                if obj_id not in team_ids:
                    raise falcon.HTTPBadRequest(
                        title="Invalid Team",
                        description=f"{team} is not a valid team id"
                    )

                validated_ids.append(obj_id)

            except InvalidId:
                raise falcon.HTTPBadRequest(
                    title="Invalid Team",
                    description=f"{team} is not a valid team name or id"
                )

    return {**data, "teams": validated_ids}


def resolve_winner_team(data, teams_map, team_ids):
    winner = data.get("winner_team_id")

    if winner is None:
        return data

    if winner in teams_map:
        winner_id = teams_map[winner]
    else:
        try:
            winner_id = ObjectId(winner)

            if winner_id not in team_ids:
                raise falcon.HTTPBadRequest(
                    title="Invalid Winner",
                    description=f"{winner} is not a valid team id"
                )

        except InvalidId:
            raise falcon.HTTPBadRequest(
                title="Invalid Winner",
                description=f"{winner} is not a valid team name or id"
            )

    if winner_id not in data["teams"]:
        raise falcon.HTTPBadRequest(
            title="Invalid Winner",
            description="Winner must be part of tournament teams"
        )

    return {**data, "winner_team_id": winner_id}


# ---------- CRUD ----------

def create_tournament(data, db):
    teams_map = get_teams_map_name_id(db)
    team_ids = set(teams_map.values())

    validate_tournament_data(data)
    
    # Solo resolver referencias si teams está presente
    if "teams" in data:
        data = resolve_team_references(data, teams_map, team_ids)
    else:
        data["teams"] = []  # Si no hay teams, asigna array vacío
    
    # Solo resolver winner si está presente
    if "winner_team_id" in data:
        data = resolve_winner_team(data, teams_map, team_ids)

    tournament = Tournament(**data)

    result = db.tournaments.insert_one(tournament.to_dict())
    return str(result.inserted_id)

def get_tournament_by_id(tournament_id, db):
    try:
        obj_id = ObjectId(tournament_id)
    except InvalidId:
        raise falcon.HTTPBadRequest(title="Invalid ID", description="Invalid tournament id") 
    
    tournament = db.tournaments.find_one({"_id": obj_id})
    if not tournament:
        raise falcon.HTTPNotFound(description="Tournament not found")
    
    team_names = get_teams_map_id_name(db)
    tournament["_id"] = str(tournament["_id"])
    teams = []
    for team_id in tournament["teams"]:
        if team_id in team_names:
            teams.append(team_names[team_id])
    tournament["teams"] = teams
    if "winner_team_id" in tournament:
        winner_team_id = tournament["winner_team_id"]
        if winner_team_id in team_names:
            tournament["winner_team_id"] = team_names[winner_team_id]
    
    return tournament



def get_all_tournaments(db):
    tournaments = list(db.tournaments.find())
    team_names = get_teams_map_id_name(db)

    for t in tournaments:
        t["_id"] = str(t["_id"])
        teams = []
        for team_id in t["teams"]:
            if team_id in team_names:
                teams.append(team_names[team_id])
        t["teams"] = teams
        if "winner_team_id" in t:
            winner_team_id = t["winner_team_id"]
            if winner_team_id in team_names:
                t["winner_team_id"] = team_names[winner_team_id]


    return tournaments


def delete_tournament(tournament_id, db):
    try:
        obj_id = ObjectId(tournament_id)
    except InvalidId:
        raise falcon.HTTPBadRequest(title="Invalid ID", description="Invalid tournament id")
    
    tournament = db.tournaments.find_one({"_id": obj_id})
    if not tournament:
        raise falcon.HTTPNotFound(description="Tournament not found")
    
    # Check if tournament is linked to any match
    match = db.matches.find_one({"tournament_id": obj_id})
    if match:
        raise falcon.HTTPConflict(
            title="Cannot Delete",
            description="Cannot delete tournament that has matches"
        )
    
    # If no matches linked, proceed with deletion
    result = db.tournaments.delete_one({"_id": obj_id})

    if result.deleted_count == 0:
        raise falcon.HTTPNotFound(description="Tournament not found")

    tournament["_id"] = str(tournament["_id"])
    return tournament


def update_tournament(tournament_id, data, db):
    try:
        obj_id = ObjectId(tournament_id)
    except InvalidId:
        raise falcon.HTTPBadRequest(title="Invalid ID", description="Invalid tournament id")

    teams_map = get_teams_map_name_id(db)
    team_ids = set(teams_map.values())

    data = validate_partial_tournament_data(data)

    if "teams" in data:
        data = resolve_team_references(data, teams_map, team_ids)

    if "winner_team_id" in data:
        data = resolve_winner_team(data, teams_map, team_ids)

    result = db.tournaments.update_one(
        {"_id": obj_id},
        {"$set": data}
    )

    if result.matched_count == 0:
        raise falcon.HTTPNotFound(title="Tournament not found", description="Tournament not found")

    updated = db.tournaments.find_one({"_id": obj_id})

    team_names = get_teams_map_id_name(db)
    updated["_id"] = str(updated["_id"])
    teams = []
    for team_id in updated["teams"]:
        if team_id in team_names:
            teams.append(team_names[team_id])
    updated["teams"] = teams
    if "winner_team_id" in updated:
        winner_team_id = updated["winner_team_id"]
        if winner_team_id in team_names:
            updated["winner_team_id"] = team_names[winner_team_id]
    

    return updated