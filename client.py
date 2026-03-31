#!/usr/bin/env python3
import argparse
import csv
import os
import requests
from utils import load_data, FORBALL_API_URL, print_object, reset
import api


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--load", action="store_true")
    parser.add_argument("--reset", action="store_true")

    parser.add_argument("resource", nargs="?", choices=["teams", "tournaments", "matches", "people"])
    parser.add_argument("action", nargs="?", choices=["get", "search", "create", "update", "delete"])
    parser.add_argument("--search-params", nargs='*', help="Search parameters (e.g., --search-params rating=4.5 title=python)")

    parser.add_argument("--id")
    parser.add_argument("--name")
    parser.add_argument("--country")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--skip", type=int)

    args = parser.parse_args()

    if args.load:
        load_data()
        return
    elif args.reset:
        reset()
        return

    if args.id and args.action not in ["get", "update", "delete"]:
        print(f"ERROR: Can't use arg id with action {args.action}")
        exit(1)

    if args.action == "search":
        if args.resource != "matches":
            print("ERROR: Search action is only supported for matches resource")
            exit(1)
        
        search_params = {}
        if args.search_params:
            for param in args.search_params:
                if "=" in param:
                    key, value = param.split("=", 1)
                    search_params[key] = value
                else:
                    print(f"ERROR: Invalid search parameter format: {param}. Expected format is key=value.")
                    exit(1)
        
        if args.limit is not None:
            search_params["limit"] = args.limit
        if args.skip is not None:
            search_params["skip"] = args.skip
        
        api.search_matches(search_params)

    if args.action == "get" and not args.id:
        if args.resource == "teams":
            api.get_all("teams")
        elif args.resource == "tournaments":
            api.get_all("tournaments")
        elif args.resource == "people":
            api.get_all("people")
        elif args.resource == "matches":
            api.get_all("matches")
    elif args.action == "get" and args.id:
        if args.resource == "teams":
            api.get_by_id("teams", args.id)
        elif args.resource == "tournaments":
            api.get_by_id("tournaments", args.id)
        elif args.resource == "people":
            api.get_by_id("people", args.id)
        elif args.resource == "matches":
            api.get_by_id("matches", args.id)
    

    if args.action == "update" and args.id:
        if args.resource == "teams":
            data = build_team_update(name=args.name, country=args.country)
            api.update_by_id("teams", args.id, data)
        elif args.resource == "people":
            data = build_people_update()
            api.update_by_id("people", args.id, data)
        elif args.resource == "tournaments":
            data = build_tournament_update(name=args.name, country=args.country)
            api.update_by_id("tournaments", args.id, data)
        elif args.resource == "matches":
            data = build_match_update()
            api.update_by_id("matches", args.id, data)

    

    if args.action == "delete" and args.id:
        if args.resource == "teams":
            api.delete_by_id("teams", args.id)
        elif args.resource == "tournaments":
            api.delete_by_id("tournaments", args.id)
        elif args.resource == "people":
            api.delete_by_id("people", args.id)
        elif args.resource == "matches":
            api.delete_by_id("matches", args.id)
    
    if args.action == "create":
        if args.resource == "teams":
            create_team()
        elif args.resource == "tournaments":
            create_tournament()
        elif args.resource == "people":
            create_person()
        elif args.resource == "matches":
            create_match()
    




def create_team():
    print("Creating team...")
    name = input("Enter team name: ").strip()
    country = input("Enter team country: ").strip()

    if not name or not country:
        print("ERROR: Name and country are required")
        exit(1)
    
    if not name.strip() or not country.strip():
        print("ERROR: Name and country cannot be empty")
        exit(1)
    
    if name.isdigit() or country.isdigit():
        print("ERROR: Name and country cannot be numbers")
        exit(1)

    print("Do you have stats to add? (y/n)")
    if input("Enter choice: ").strip().lower() == "y":
        stats = {}
        wins = input("Enter wins: ").strip()
        draws = input("Enter draws: ").strip()
        losses = input("Enter losses: ").strip()
        goals_in_favor = input("Enter goals in favor: ").strip()
        goals_against = input("Enter goals against: ").strip()
        if wins.isdigit():
            stats["wins"] = int(wins)
        if draws.isdigit():
            stats["draws"] = int(draws)
        if losses.isdigit():
            stats["losses"] = int(losses)
        if goals_in_favor.isdigit():
            stats["goals_in_favor"] = int(goals_in_favor)
        if goals_against.isdigit():
            stats["goals_against"] = int(goals_against)
    else:
        stats = {
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_in_favor": 0,
            "goals_against": 0
        }


    data = {
        "name": name,
        "country": country,
        "stats": stats
    }

    api.create("teams", data)


def create_tournament():
    print("Creating tournament...")
    name = input("Enter tournament name: ").strip()
    country = input("Enter tournament country: ").strip()
    total_match_days = input("Enter total match days: ").strip()

    if total_match_days.isdigit():
        total_match_days = int(total_match_days)
    else:
        print("ERROR: Total match days must be an integer")
        exit(1)
    
    have_team_winner =  input("Do you have a winner team id to add? (y/n): ").strip().lower() == "y"

    if have_team_winner:
        winner_team_id = input("Enter winner team id: ").strip()
    else:
        winner_team_id = None

    if not name or not country:
        print("ERROR: Name and country are required")
        exit(1)
    
    print("Do you want to add teams now? (y/n)")
    teams = []
    if input("Enter choice: ").strip().lower() == "y":
        while True:
            team_name_or_id = input("Enter team name or id (or press Enter to stop adding teams): ").strip()
            if not team_name_or_id:
                break
            teams.append(team_name_or_id)
    


    data = {
        "name": name,
        "country": country,
        "teams": teams,
        "winner_team_id": winner_team_id,
        "total_match_days": total_match_days
    }

    api.create("tournaments", data)


def create_person():
    print("Creating person...")
    print("Do you want to create a player/manager? (Enter 'p' or 'm)")
    
    person_type = input("Enter type: ").strip()
    if person_type not in ["p", "m"]:
        print("ERROR: Invalid type. Please enter 'p' or 'm'.")
        exit(1)

    data = {
        "type": "player" if person_type == "p" else "manager"
    }

    first_name = input("Enter person's first name: ").strip()
    last_name = input("Enter person's last name: ").strip()

    if first_name.strip() == "" or last_name.strip() == "":
        print("ERROR: First name and last name cannot be empty")
        exit(1)

    if first_name.isdigit() or last_name.isdigit():
        print("ERROR: First name and last name cannot be numbers")
        exit(1)
    
    
    data["first_name"] = first_name
    data["last_name"] = last_name
    
    print("Do you want to add a team for this person? (y/n)")
    if input("Enter choice: ").strip().lower() == "y":
        team_name_or_id = input("Enter team name or id: ").strip()
        data["team_id"] = team_name_or_id
    

    if person_type == "p":
        shirt_number = input("Enter shirt number: ").strip()
        if shirt_number.isdigit():
            data["shirt_number"] = int(shirt_number)
        else:
            print("ERROR: Shirt number must be an integer")
            exit(1)

        print("Do you have attributes to add? (y/n)")
        if input("Enter choice: ").strip().lower() == "y":
            attributes = {}
            print("Attributes (leave blank to skip):")
            reflexes = input("  Reflexes: ").strip()
            positioning = input("  Positioning: ").strip()
            distribution = input("  Distribution: ").strip()
            dribbling = input("  Dribbling: ").strip()
            speed = input("  Speed: ").strip()
            shooting = input("  Shooting: ").strip()
            
            if reflexes.isdigit():
                attributes["reflexes"] = int(reflexes)
            if positioning.isdigit():
                attributes["positioning"] = int(positioning)
            if distribution.isdigit():
                attributes["distribution"] = int(distribution)
            if dribbling.isdigit():
                attributes["dribbling"] = int(dribbling)
            if speed.isdigit():
                attributes["speed"] = int(speed)
            if shooting.isdigit():
                attributes["shooting"] = int(shooting)
            
            if attributes:
                data["attributes"] = attributes
    

    api.create("people", data)


def create_match():
    print("Creating match...")
    
    # Tournament
    tournament_id = input("Enter tournament name or id: ").strip()
    if not tournament_id:
        print("ERROR: Tournament id/name is required")
        exit(1)
    
    # Match day
    match_day = input("Enter match day (integer): ").strip()
    if not match_day.isdigit():
        print("ERROR: Match day must be an integer")
        exit(1)
    match_day = int(match_day)
    
    # Date
    date = input("Enter match date (e.g., 2024-01-13): ").strip()
    if not date:
        print("ERROR: Date is required")
        exit(1)
    
    # Home team
    print("\n--- Home Team ---")
    home_team_id = input("Enter home team name or id: ").strip()
    home_team_name = input("Enter home team name (for display): ").strip()
    home_goals = input("Enter goals scored by home team: ").strip()
    
    if not home_team_id or not home_team_name or not home_goals.isdigit():
        print("ERROR: All home team fields are required, goals must be integer")
        exit(1)
    home_goals = int(home_goals)
    
    # Away team
    print("\n--- Away Team ---")
    away_team_id = input("Enter away team name or id: ").strip()
    away_team_name = input("Enter away team name (for display): ").strip()
    away_goals = input("Enter goals scored by away team: ").strip()
    
    if not away_team_id or not away_team_name or not away_goals.isdigit():
        print("ERROR: All away team fields are required, goals must be integer")
        exit(1)
    away_goals = int(away_goals)
    
    # MVP Player
    mvp_player = input("Enter MVP player (FirstName LastName or id): ").strip()
    if not mvp_player:
        print("ERROR: MVP player is required")
        exit(1)
    
    # Stats
    print("\n--- Match Statistics ---")
    print("Possession %:")
    poss_home = input("  Home: ").strip()
    poss_away = input("  Away: ").strip()
    if not poss_home.isdigit() or not poss_away.isdigit():
        print("ERROR: Possession values must be integers")
        exit(1)
    
    print("Shots on target:")
    shots_home = input("  Home: ").strip()
    shots_away = input("  Away: ").strip()
    if not shots_home.isdigit() or not shots_away.isdigit():
        print("ERROR: Shots on target must be integers")
        exit(1)
    
    print("Corners:")
    corners_home = input("  Home: ").strip()
    corners_away = input("  Away: ").strip()
    if not corners_home.isdigit() or not corners_away.isdigit():
        print("ERROR: Corners must be integers")
        exit(1)
    
    print("Fouls:")
    fouls_home = input("  Home: ").strip()
    fouls_away = input("  Away: ").strip()
    if not fouls_home.isdigit() or not fouls_away.isdigit():
        print("ERROR: Fouls must be integers")
        exit(1)
    
    # Player stats
    print("\n--- Player Statistics ---")
    player_stats = []
    while True:
        add_player = input("Add player stats? (y/n): ").strip().lower()
        if add_player != "y":
            break
        
        player_id = input("  Player (FirstName LastName or id): ").strip()
        goals = input("  Goals: ").strip()
        assists = input("  Assists: ").strip()
        shots = input("  Shots on target: ").strip()
        minutes = input("  Minutes played: ").strip()
        
        if not player_id or not all([goals.isdigit(), assists.isdigit(), shots.isdigit(), minutes.isdigit()]):
            print("ERROR: All player stats required, numbers must be integers")
            exit(1)
        
        player_stats.append({
            "player_id": player_id,
            "goals": int(goals),
            "assists": int(assists),
            "shots_on_target": int(shots),
            "minutes_played": int(minutes)
        })
    
    # Build nested structure
    data = {
        "tournament_id": tournament_id,
        "match_day": match_day,
        "date": date,
        "home_team": {
            "team_id": home_team_id,
            "name": home_team_name,
            "goals": home_goals
        },
        "away_team": {
            "team_id": away_team_id,
            "name": away_team_name,
            "goals": away_goals
        },
        "mvp_player_id": mvp_player,
        "stats": {
            "possession": {"home": int(poss_home), "away": int(poss_away)},
            "shots_on_target": {"home": int(shots_home), "away": int(shots_away)},
            "corners": {"home": int(corners_home), "away": int(corners_away)},
            "fouls": {"home": int(fouls_home), "away": int(fouls_away)}
        },
        "player_stats": player_stats
    }
    
    api.create("matches", data)


def build_match_update():
    """Build match update data - allows updating mvp_player_id, stats, player_stats, date"""
    data = {}
    
    print("What do you want to update? (Choose one or more)")
    print("1. MVP player")
    print("2. Match statistics")
    print("3. Player statistics")
    print("4. Match date")
    
    # MVP Player
    update_mvp = input("Update MVP player? (y/n): ").strip().lower() == "y"
    if update_mvp:
        mvp = input("Enter new MVP player name/id: ").strip()
        if mvp:
            data["mvp_player_id"] = mvp
        else:
            print("ERROR: MVP player cannot be empty")
            exit(1)
    
    # Stats
    update_stats = input("Update match statistics? (y/n): ").strip().lower() == "y"
    if update_stats:
        print("\n--- Match Statistics ---")
        print("Possession %:")
        poss_home = input("  Home: ").strip()
        poss_away = input("  Away: ").strip()
        if not poss_home.isdigit() or not poss_away.isdigit():
            print("ERROR: Possession values must be integers")
            exit(1)
        
        print("Shots on target:")
        shots_home = input("  Home: ").strip()
        shots_away = input("  Away: ").strip()
        if not shots_home.isdigit() or not shots_away.isdigit():
            print("ERROR: Shots on target must be integers")
            exit(1)
        
        print("Corners:")
        corners_home = input("  Home: ").strip()
        corners_away = input("  Away: ").strip()
        if not corners_home.isdigit() or not corners_away.isdigit():
            print("ERROR: Corners must be integers")
            exit(1)
        
        print("Fouls:")
        fouls_home = input("  Home: ").strip()
        fouls_away = input("  Away: ").strip()
        if not fouls_home.isdigit() or not fouls_away.isdigit():
            print("ERROR: Fouls must be integers")
            exit(1)
        
        data["stats"] = {
            "possession": {"home": int(poss_home), "away": int(poss_away)},
            "shots_on_target": {"home": int(shots_home), "away": int(shots_away)},
            "corners": {"home": int(corners_home), "away": int(corners_away)},
            "fouls": {"home": int(fouls_home), "away": int(fouls_away)}
        }
    
    # Player Stats
    update_player_stats = input("Update player statistics? (y/n): ").strip().lower() == "y"
    if update_player_stats:
        print("\n--- Player Statistics ---")
        player_stats = []
        while True:
            add_player = input("Add player stats? (y/n): ").strip().lower()
            if add_player != "y":
                break
            
            player_id = input("  Player name/id: ").strip()
            goals = input("  Goals: ").strip()
            assists = input("  Assists: ").strip()
            shots = input("  Shots on target: ").strip()
            minutes = input("  Minutes played: ").strip()
            
            if not player_id or not all([goals.isdigit(), assists.isdigit(), shots.isdigit(), minutes.isdigit()]):
                print("ERROR: All player stats required, numbers must be integers")
                exit(1)
            
            player_stats.append({
                "player_id": player_id,
                "goals": int(goals),
                "assists": int(assists),
                "shots_on_target": int(shots),
                "minutes_played": int(minutes)
            })
        
        data["player_stats"] = player_stats
    
    # Date
    update_date = input("Update match date? (y/n): ").strip().lower() == "y"
    if update_date:
        date = input("Enter new match date (e.g., 2024-01-13): ").strip()
        if not date:
            print("ERROR: Date cannot be empty")
            exit(1)
        data["date"] = date
    
    if not data:
        print("ERROR: No fields to update")
        exit(1)
    
    return data


def build_tournament_update(name=None, country=None):
    """Build tournament update data - allows updating name, country, teams, and winner"""
    data = {}

    # Update name
    if name is not None:
        data["name"] = name
    else:
        user_input = input("Enter new name (or press Enter to skip): ").strip()
        if user_input:
            if user_input.isdigit():
                print("ERROR: Name cannot be only numbers")
                exit(1)
            data["name"] = user_input

    # Update country
    if country is not None and country.strip():
        data["country"] = country
    else:
        user_input = input("Enter new country (or press Enter to skip): ").strip()
        if user_input:
            if user_input.isdigit():
                print("ERROR: Country cannot be only numbers")
                exit(1)
            data["country"] = user_input
    
    # Update teams
    user_input = input("Do you want to update teams? (y/n): ").strip().lower()
    if user_input == "y":
        teams = []
        while True:
            team = input("Enter team name or id (or press Enter to finish adding teams): ").strip()
            if not team:
                break
            teams.append(team)
        data["teams"] = teams
    
    # Update winner
    user_input = input("Do you want to update winner? (y/n): ").strip().lower()
    if user_input == "y":
        winner = input("Enter winner team name/id (or press Enter for None): ").strip()
        data["winner_team_id"] = winner if winner else None

    if not data:
        print("ERROR: No fields to update")
        exit(1)

    return data


def build_team_update(name=None, country=None):
    """Build team update data from arguments or console input"""
    data = {}

    if name is not None:
        data["name"] = name
    else:
        user_input = input("Enter new name (or press Enter to skip): ").strip()
        if user_input:
            data["name"] = user_input

    if country is not None:
        data["country"] = country
    else:
        user_input = input("Enter new country (or press Enter to skip): ").strip()
        if user_input:
            data["country"] = user_input

    if not data:
        print("ERROR: No fields to update")
        exit(1)

    return data


def build_people_update():
    """Build people update data from console input"""
    data = {}

    print("Are you updating a player or a manager? (Enter 'p' or 'm'): ")
    person_type = input().strip().lower()
    if person_type not in ["p", "m"]:
        print("ERROR: Invalid option")
        exit(1)

    if person_type == "p":
        print("Updating a player. You can update team, shirt number, and attributes.")
        team_input = input("New team name/id (or press Enter to skip): ").strip()
        if team_input:
            if not team_input.isdigit():
                data["team_id"] = team_input
            else:
                print("ERROR: Team ID cannot be only numbers")
                exit(1)
        
        shirt_number_input = input("New shirt number (or press Enter to skip): ").strip()
        if shirt_number_input:
            if shirt_number_input.isdigit():
                data["shirt_number"] = int(shirt_number_input)
            else:
                print("ERROR: Shirt number must be an integer")
                exit(1)
        
        print("Do you want to update attributes? (y/n): ")
        if input().strip().lower() == "y":
            attributes = {}
            print("Attributes (leave blank to skip):")
            reflexes = input("  Reflexes: ").strip()
            positioning = input("  Positioning: ").strip()
            distribution = input("  Distribution: ").strip()
            dribbling = input("  Dribbling: ").strip()
            speed = input("  Speed: ").strip()
            shooting = input("  Shooting: ").strip()
            
            if reflexes.isdigit():
                attributes["reflexes"] = int(reflexes)
            if positioning.isdigit():
                attributes["positioning"] = int(positioning)
            if distribution.isdigit():
                attributes["distribution"] = int(distribution)
            if dribbling.isdigit():
                attributes["dribbling"] = int(dribbling)
            if speed.isdigit():
                attributes["speed"] = int(speed)
            if shooting.isdigit():
                attributes["shooting"] = int(shooting)
            
            if attributes:
                data["attributes"] = attributes
    
    elif person_type == "m":
        print("Updating a manager. You can update team.")
        team_input = input("New team name/id (or press Enter to skip): ").strip()
        if team_input:
            if not team_input.isdigit():
                data["team_id"] = team_input
            else:
                print("ERROR: Team ID cannot be only numbers")
                exit(1)
    
    if not data:
        print("ERROR: No fields to update")
        exit(1)
    
    return data


if __name__ == "__main__":
    main()
