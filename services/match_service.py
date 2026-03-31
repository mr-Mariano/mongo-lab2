import falcon
from bson import ObjectId
from bson.errors import InvalidId

from validators import match_validator
from models.match_model import Match, TeamInfo, Balance, Stats, Player


# POST
def create_match(data, db):
    # Validate
    match_validator.validate_match_data(data)
    # Resolve references
    teams_map = get_teams_map_name_id(db)
    team_ids = set(teams_map.values())
    data = resolve_team_references(data, teams_map, team_ids)

    people_map = get_people_map_name_id(db)
    people_ids = set(people_map.values())
    data = resolve_mvp_player_reference(data, people_map, people_ids)

    tournament_map = get_tournament_map_name_id(db)
    tournament_ids = set(tournament_map.values())
    data = resolve_tournament_reference(data, tournament_map, tournament_ids)

    data = resolve_stats_references(data, people_map, people_ids)

    data = resolve_player_stats_references(data, people_map, people_ids)


    teamInfo_home = TeamInfo(data["home_team"]["team_id"], data["home_team"]["name"], data["home_team"]["goals"])
    teamInfo_away = TeamInfo(data["away_team"]["team_id"], data["away_team"]["name"], data["away_team"]["goals"])

    balance_possession = Balance(data["stats"]["possession"]["home"], data["stats"]["possession"]["away"])
    balance_shots_on_target = Balance(data["stats"]["shots_on_target"]["home"], data["stats"]["shots_on_target"]["away"])
    balance_corners = Balance(data["stats"]["corners"]["home"], data["stats"]["corners"]["away"])
    balance_fouls = Balance(data["stats"]["fouls"]["home"], data["stats"]["fouls"]["away"])

    stats = Stats(balance_possession, balance_shots_on_target, balance_corners, balance_fouls)
    player_stats = [Player(stat["player_id"], stat["goals"], stat["assists"], stat["shots_on_target"], stat["minutes_played"]) for stat in data.get("player_stats", [])]


    match = Match(
        tournament_id=data["tournament_id"],
        match_day=data["match_day"],
        date=data["date"],
        home_team=teamInfo_home,
        away_team=teamInfo_away,
        mvp_player_id=data["mvp_player_id"],
        stats=stats,
        player_stats=player_stats
    )

    result = db.matches.insert_one(match.to_dict())
    return str(result.inserted_id)


# GET ALL
def get_all_matches(db):
    matches = list(db.matches.find())
    team_names = get_teams_map_id_name(db)
    people_names = get_people_map_id_name(db)
    tournament_names = get_tournament_map_id_name(db) 

    for match in matches:
        match["_id"] = str(match["_id"])
        
        if "tournament_id" in match and match["tournament_id"] in tournament_names:
            match["tournament_id"] = tournament_names[match["tournament_id"]]

        for team_key in ["home_team", "away_team"]:
            team_info = match.get(team_key)
            if team_info and "team_id" in team_info:
                team_id = team_info["team_id"]
                if team_id in team_names:
                    match[team_key]["team_id"] = team_names[team_id]

        mvp_player_id = match.get("mvp_player_id")
        if mvp_player_id and mvp_player_id in people_names:
            match["mvp_player_id"] = people_names[mvp_player_id]

        player_stats = match.get("player_stats", [])
        for stat in player_stats:
            player_id = stat.get("player_id")
            if player_id and player_id in people_names:
                stat["player_id"] = people_names[player_id]
    
    return matches



# GET BY ID
def get_match_by_id(match_id, db):
    try:
        match_id = ObjectId(match_id)
    except InvalidId:
        raise falcon.HTTPBadRequest(title="Invalid ID", description="Invalid match id")

    match = db.matches.find_one({"_id": match_id})

    if not match:
        raise falcon.HTTPNotFound(description="Match not found")

    match["_id"] = str(match["_id"])

    team_names = get_teams_map_id_name(db)
    people_names = get_people_map_id_name(db)
    tournament_names = get_tournament_map_id_name(db)  

    if "tournament_id" in match and match["tournament_id"] in tournament_names:
        match["tournament_id"] = tournament_names[match["tournament_id"]]

    for team_key in ["home_team", "away_team"]:
        team_info = match.get(team_key)
        if team_info and "team_id" in team_info:
            team_id = team_info["team_id"]
            if team_id in team_names:
                match[team_key]["team_id"] = team_names[team_id]

    mvp_player_id = match.get("mvp_player_id")
    if mvp_player_id and mvp_player_id in people_names:
        match["mvp_player_id"] = people_names[mvp_player_id]

    player_stats = match.get("player_stats", [])
    for stat in player_stats:
        player_id = stat.get("player_id")
        if player_id and player_id in people_names:
            stat["player_id"] = people_names[player_id]

    return match



# UPDATE BY ID
def update_match(match_id, data, db):
    try:
        match_id = ObjectId(match_id)
    except InvalidId:
        raise falcon.HTTPBadRequest(title="Invalid ID", description="Invalid match id")

    existing_match = db.matches.find_one({"_id": match_id})
    if not existing_match:
        raise falcon.HTTPNotFound(description="Match not found")

    # Validate update data - only allow specific fields
    match_validator.validate_match_update_data(data)

    # Resolve mvp_player_id if being updated
    if "mvp_player_id" in data:
        mvp_player_id = data["mvp_player_id"]
        people_map = get_people_map_name_id(db)
        people_ids = set(people_map.values())
        
        if mvp_player_id in people_map:
            data["mvp_player_id"] = people_map[mvp_player_id]
        else:
            try:
                mvp_player_obj_id = ObjectId(mvp_player_id)
                if mvp_player_obj_id not in people_ids:
                    raise falcon.HTTPBadRequest(
                        title="Invalid MVP Player",
                        description=f"{mvp_player_id} is not a valid player id"
                    )
                data["mvp_player_id"] = mvp_player_obj_id
            except InvalidId:
                raise falcon.HTTPBadRequest(
                    title="Invalid MVP Player",
                    description=f"{mvp_player_id} is not a valid player name or id"
                )
    
    # Resolve player_stats references if being updated
    if "player_stats" in data:
        people_map = get_people_map_name_id(db)
        people_ids = set(people_map.values())
        
        for stat in data["player_stats"]:
            player_id = stat.get("player_id")
            if player_id in people_map:
                stat["player_id"] = people_map[player_id]
            else:
                try:
                    obj_id = ObjectId(player_id)
                    if obj_id not in people_ids:
                        raise falcon.HTTPBadRequest(
                            title="Invalid Player",
                            description=f"{player_id} is not a valid player id"
                        )
                    stat["player_id"] = obj_id
                except InvalidId:
                    raise falcon.HTTPBadRequest(
                        title="Invalid Player",
                        description=f"{player_id} is not a valid player name or id"
                    )
    
    # Update document
    update_data = {"$set": data}
    db.matches.update_one({"_id": match_id}, update_data)
    updated_match = db.matches.find_one({"_id": match_id})
    updated_match["_id"] = str(updated_match["_id"])

    # Convert ObjectIds back to names for response
    team_names = get_teams_map_id_name(db)
    people_names = get_people_map_id_name(db)
    tournament_names = get_tournament_map_id_name(db)

    # Convert tournament_id
    if "tournament_id" in updated_match and updated_match["tournament_id"] in tournament_names:
        updated_match["tournament_id"] = tournament_names[updated_match["tournament_id"]]

    # Convert team IDs
    for team_key in ["home_team", "away_team"]:
        team_info = updated_match.get(team_key)
        if team_info and "team_id" in team_info:
            team_id = team_info["team_id"]
            if team_id in team_names:
                updated_match[team_key]["team_id"] = team_names[team_id]
    
    # Convert MVP player ID
    mvp_player_id = updated_match.get("mvp_player_id")
    if mvp_player_id and mvp_player_id in people_names:
        updated_match["mvp_player_id"] = people_names[mvp_player_id]
    
    # Convert player stats player IDs
    player_stats = updated_match.get("player_stats", [])
    for stat in player_stats:
        player_id = stat.get("player_id")
        if player_id and player_id in people_names:
            stat["player_id"] = people_names[player_id]
    
    return updated_match


# DELETE BY ID
def delete_match(match_id, db):
    try:
        match_id = ObjectId(match_id)
        print(f"DEBUG: Deleting match with id: {match_id}")
    except InvalidId:
        raise falcon.HTTPBadRequest(title="Invalid ID", description="Invalid match id")

    print(f"DEBUG: Attempting to delete match with id: {match_id}")
    result = db.matches.delete_one({"_id": match_id})
    print(f"DEBUG: Delete result: {result.deleted_count} document(s) deleted")
    if result.deleted_count == 0:
        raise falcon.HTTPNotFound(description="Match not found")
    
    return True

# ---------- Helpers ----------

def get_tournament_map_name_id(db):
    tournaments = db.tournaments.find({}, {"name": 1})
    return {tournament["name"]: tournament["_id"] for tournament in tournaments}

def get_tournament_map_id_name(db):
    tournaments = db.tournaments.find({}, {"name": 1})
    return {tournament["_id"]: tournament["name"] for tournament in tournaments}

def get_teams_map_name_id(db):
    teams = db.teams.find({}, {"name": 1})
    return {team["name"]: team["_id"] for team in teams}

def get_teams_map_id_name(db):
    teams = db.teams.find({}, {"name": 1})
    return {team["_id"]: team["name"] for team in teams}


def get_people_map_name_id(db):
    people = db.people.find({}, {"first_name": 1, "last_name": 1})
    return {f"{person['first_name']} {person['last_name']}": person["_id"] for person in people}


def get_people_map_id_name(db):
    people = db.people.find({}, {"first_name": 1, "last_name": 1})
    return {person["_id"]: f"{person['first_name']} {person['last_name']}" for person in people}


def resolve_tournament_reference(data, tournament_map, tournament_ids):
    tournament_name = data.get("tournament_id")

    if tournament_name is None:
        raise falcon.HTTPBadRequest(
            title="Missing Tournament",
            description="tournament_id is required and must be a valid tournament name or id."
        )

    if tournament_name in tournament_map:
        tournament_id = tournament_map[tournament_name]
    else:

        try:
            tournament_id = ObjectId(tournament_name)
            if tournament_id not in tournament_ids:
                raise falcon.HTTPBadRequest(
                    title="Invalid Tournament",
                    description=f"{tournament_name} is not a valid tournament id"
                )
        except InvalidId:
            raise falcon.HTTPBadRequest(
                title="Invalid Tournament",
                description=f"{tournament_name} is not a valid tournament name or id"
            )

    return {**data, "tournament_id": tournament_id}


def resolve_player_stats_references(data, people_map, people_ids):
    # This function can be used to resolve any team references inside the stats field if needed
    stats = data.get("player_stats", [])
    for stat in stats:
        player_id = stat.get("player_id")
        if player_id in people_map:
            stat["player_id"] = people_map[player_id]
        else:
            try:
                obj_id = ObjectId(player_id)

                if obj_id not in people_ids:
                    raise falcon.HTTPBadRequest(
                        title="Invalid Player",
                        description=f"{player_id} is not a valid player id"
                    )

                stat["player_id"] = obj_id

            except InvalidId:
                raise falcon.HTTPBadRequest(
                    title="Invalid Player",
                    description=f"{player_id} is not a valid player name or id"
                )
    return data


def resolve_mvp_player_reference(data, people_map, people_ids):
    mvp_player = data.get("mvp_player_id")

    if mvp_player is None:
        raise falcon.HTTPBadRequest(
            title="Missing MVP Player",
            description="mvp_player_id is required and must be a valid player name or id."
        )
    if mvp_player in people_map:
        mvp_player_id = people_map[mvp_player]
    else:
        try:
            mvp_player_id = ObjectId(mvp_player)

            if mvp_player_id not in people_ids:
                raise falcon.HTTPBadRequest(
                    title="Invalid MVP Player",
                    description=f"{mvp_player} is not a valid player id"
                )

        except InvalidId:
            raise falcon.HTTPBadRequest(
                title="Invalid MVP Player",
                description=f"{mvp_player} is not a valid player name or id"
            )

    return {**data, "mvp_player_id": mvp_player_id}


def resolve_team_references(data, teams_map, team_ids):
    for team_key in ["home_team", "away_team"]:
        team_info = data.get(team_key)
        if team_info and "team_id" in team_info:
            team_id = team_info["team_id"]

            if team_id in teams_map:
                data[team_key]["team_id"] = teams_map[team_id]
            else:
                try:
                    obj_id = ObjectId(team_id)

                    if obj_id not in team_ids:
                        raise falcon.HTTPBadRequest(
                            title="Invalid Team",
                            description=f"{team_id} is not a valid team id"
                        )

                    data[team_key]["team_id"] = obj_id

                except InvalidId:
                    raise falcon.HTTPBadRequest(
                        title="Invalid Team",
                        description=f"{team_id} is not a valid team name or id"
                    )
        else:
            raise falcon.HTTPBadRequest(
                title="Missing Team",
                description=f"{team_key} must include a team_id field."
            )

    return data


def resolve_stats_references(data, people_map, people_ids):
    stats = data.get("stats", {})
    for stat_key in ["possession", "shots_on_target", "corners", "fouls"]:
        stat_info = stats.get(stat_key)
        if stat_info and "home" in stat_info and "away" in stat_info:
            # If there are any player references inside the stats, they can be resolved here
            pass  # In this case, there are no player references inside stats, so we just return the data as is
        else:
            raise falcon.HTTPBadRequest(
                title="Invalid Stats",
                description=f"{stat_key} must include home and away fields."
            )
    return data


def parse_pagination(req):
    """Parse and validate pagination parameters"""
    limit = req.get_param_as_int("limit")
    skip = req.get_param_as_int("skip")
    
    DEFAULT_LIMIT = 10
    MAX_LIMIT = 100
    DEFAULT_SKIP = 0
    
    if limit is None:
        limit = DEFAULT_LIMIT
    elif limit < 1:
        limit = DEFAULT_LIMIT
    elif limit > MAX_LIMIT:
        limit = MAX_LIMIT
    
    if skip is None:
        skip = DEFAULT_SKIP
    elif skip < 0:
        skip = DEFAULT_SKIP
    
    return limit, skip


def parse_filter_params(req):
    """Parse all filter parameters (numeric, text, sorting)"""
    return {
        "match_day": req.get_param_as_int("match_day"),
        "match_day_min": req.get_param_as_int("match_day_min"),
        "match_day_max": req.get_param_as_int("match_day_max"),
        "home_goals": req.get_param_as_int("home_goals"),
        "home_goals_min": req.get_param_as_int("home_goals_min"),
        "home_goals_max": req.get_param_as_int("home_goals_max"),
        "away_goals": req.get_param_as_int("away_goals"),
        "away_goals_min": req.get_param_as_int("away_goals_min"),
        "away_goals_max": req.get_param_as_int("away_goals_max"),
        "tournament": req.get_param("tournament"),
        "mvp": req.get_param("mvp"),
    }


def build_match_filter(params, db):
    """Build MongoDB query filter from parameters"""
    query_filter = {}
    
    # Match day filters
    if params["match_day"] is not None:
        query_filter["match_day"] = params["match_day"]
    elif params["match_day_min"] or params["match_day_max"]:
        query_filter["match_day"] = {}
        if params["match_day_min"]:
            query_filter["match_day"]["$gte"] = params["match_day_min"]
        if params["match_day_max"]:
            query_filter["match_day"]["$lte"] = params["match_day_max"]
    
    # Home goals filters
    if params["home_goals"] is not None:
        query_filter["home_team.goals"] = params["home_goals"]
    elif params["home_goals_min"] or params["home_goals_max"]:
        query_filter["home_team.goals"] = {}
        if params["home_goals_min"]:
            query_filter["home_team.goals"]["$gte"] = params["home_goals_min"]
        if params["home_goals_max"]:
            query_filter["home_team.goals"]["$lte"] = params["home_goals_max"]
    
    # Away goals filters
    if params["away_goals"] is not None:
        query_filter["away_team.goals"] = params["away_goals"]
    elif params["away_goals_min"] or params["away_goals_max"]:
        query_filter["away_team.goals"] = {}
        if params["away_goals_min"]:
            query_filter["away_team.goals"]["$gte"] = params["away_goals_min"]
        if params["away_goals_max"]:
            query_filter["away_team.goals"]["$lte"] = params["away_goals_max"]
    
    # Tournament filter
    if params["tournament"]:
        tournaments = list(db.tournaments.find({
            "name": {"$regex": params["tournament"], "$options": "i"}
        }, {"_id": 1}))
        if tournaments:
            query_filter["tournament_id"] = {"$in": [t["_id"] for t in tournaments]}
        else:
            return None  # No tournaments found
    
    # MVP filter
    if params["mvp"]:
        people = list(db.people.find({
            "$or": [
                {"first_name": {"$regex": params["mvp"], "$options": "i"}},
                {"last_name": {"$regex": params["mvp"], "$options": "i"}}
            ]
        }, {"_id": 1}))
        if people:
            query_filter["mvp_player_id"] = {"$in": [p["_id"] for p in people]}
        else:
            return None  # No people found
    
    return query_filter


def convert_matches_for_response(matches, db):
    """Convert ObjectIds to readable names in matches"""
    team_names = get_teams_map_id_name(db)
    people_names = get_people_map_id_name(db)
    tournament_names = get_tournament_map_id_name(db)
    
    for match in matches:
        match["_id"] = str(match["_id"])
        
        if "tournament_id" in match and match["tournament_id"] in tournament_names:
            match["tournament_id"] = tournament_names[match["tournament_id"]]

        for team_key in ["home_team", "away_team"]:
            team_info = match.get(team_key)
            if team_info and "team_id" in team_info:
                team_id = team_info["team_id"]
                if team_id in team_names:
                    match[team_key]["team_id"] = team_names[team_id]

        mvp_player_id = match.get("mvp_player_id")
        if mvp_player_id and mvp_player_id in people_names:
            match["mvp_player_id"] = people_names[mvp_player_id]

        player_stats = match.get("player_stats", [])
        for stat in player_stats:
            player_id = stat.get("player_id")
            if player_id and player_id in people_names:
                stat["player_id"] = people_names[player_id]
    
    return matches