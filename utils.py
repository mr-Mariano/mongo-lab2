import argparse
import csv
import json
import os
import requests
import falcon

FORBALL_API_URL = os.getenv("FORBALL_API_URL", "http://localhost:8000")


def load_data():
    load_teams()
    load_tournaments()
    load_people()
    load_matches()


def get_error_message(response):
    """Extract error message from response"""
    try:
        return response.json().get('title') or response.json().get('description') or response.text
    except:
        return response.text or f"HTTP {response.status_code}"

def load_teams():
    suffix = f"/teams"
    endpoint = FORBALL_API_URL + suffix
    teams_map = {}
    # Creates endpoint http://localhost:8000/teams -> so requests are performed on that endpoint
    with open("data/teams.json") as f:
        teams_json = json.load(f)
        for team in teams_json:
            x = requests.post(endpoint, json=team)
            if x.ok:
                print(f"Team {team['name']} created with id {x.json()['team']}")
            else:
                error = get_error_message(x)
                print(f"Failed to post team {x} - {error} - {team}")


def load_tournaments():
    suffix = f"/tournaments"
    endpoint = FORBALL_API_URL + suffix
    # Creates endpoint http://localhost:8000/tournaments -> so requests are performed on that endpoint
    with open("data/tournaments.json") as f:
        tournaments_json = json.load(f)
        for tournament in tournaments_json:
            x = requests.post(endpoint, json=tournament)
            if x.ok:
                print(f"Tournament {tournament['name']} created with id {x.json()['tournament']}")
            else:
                error = get_error_message(x)
                print(f"Failed to create tournament {x} - {error} - {tournament}")


def load_people():
    suffix = f"/people"
    endpoint = FORBALL_API_URL + suffix
    # Creates endpoint http://localhost:8000/people -> so requests are performed on that endpoint
    with open("./data/people.json") as f:
        people_json = json.load(f)
        for person in people_json:
            x = requests.post(endpoint, json=person)
            if x.ok:
                print(f"Person {person['first_name']} created with id {x.json()['person']}")
            else:
                error = get_error_message(x)
                print(f"Failed to create person {x} - {person} - {error}")


def load_matches():
    suffix = f"/matches"
    endpoint = FORBALL_API_URL + suffix
    # Creates endpoint http://localhost:8000/matches -> so requests are performed on that endpoint
    with open("./data/matches.json") as f:
        matches_json = json.load(f)
        for match in matches_json:
            x = requests.post(endpoint, json=match)
            if x.ok:
                print(f"Match created with id {x.json()['match']}")
            else:
                error = get_error_message(x)
                print(f"Failed to create match {x} - {match} - {error}")


def reset():
    confirm = input("This will DELETE all data. Are you sure? (yes/no): ")

    if confirm.lower() != "yes":
        print("Reset cancelled.")
        return

    endpoint = f"{FORBALL_API_URL}/reset"

    response = requests.delete(endpoint)

    if response.ok:
        print("Database reset successfully.")
    else:
        print(f"Error: {response.status_code} - {response.text}")




def print_object(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def validate_exact_match(required, data):
    for field in data:
        if field not in required:
            raise falcon.HTTPBadRequest(title="Extra fields",
                                        description=f"{field} is an extra field not valid.")


def validate_required_fields(required, data):
    for field in required:
        if field not in data:
            raise falcon.HTTPBadRequest(title="Missing field",
                                        description=f"{field} is required.")
