import requests
from utils import FORBALL_API_URL, print_object

def get_all(resource):
    endpoint = f"{FORBALL_API_URL}/{resource}"
    response = requests.get(endpoint)
    if response.ok:
        json_resp = response.json()
        items = json_resp.get(resource, [])
        for item in items:
            print_object(item)
    else:
        print(f"Error: {response.status_code} - {response.text}")



def get_by_id(resource, item_id):
    endpoint = f"{FORBALL_API_URL}/{resource}/{item_id}"
    response = requests.get(endpoint)
    if response.ok:
        json_resp = response.json()

        singular_map = {
            "teams": "team",
            "tournaments": "tournament",
            "people": "person",
            "matches": "match"
        }

        singular = singular_map.get(resource, resource[:-1])
        item = json_resp.get(singular) or json_resp.get(resource)
        if item:
            print_object(item)
        else:
            print(f"{singular.capitalize()} not found in response")
    else:
        print(f"Error: {response.status_code} - {response.text}")


# UPDATE by ID
def update_by_id(resource, item_id, data):
    endpoint = f"{FORBALL_API_URL}/{resource}/{item_id}"
    response = requests.put(endpoint, json=data)
    if response.ok:
        json_resp = response.json()
        singular_map = {
            "teams": "team",
            "tournaments": "tournament",
            "people": "person",
            "matches": "match"
        }
        singular = singular_map.get(resource, resource[:-1])
        item = json_resp.get(singular) or json_resp.get(resource)
        if item:
            print_object(item)
        else:
            print(f"{singular.capitalize()} not found in response")
    else:
        print(f"Error: {response.status_code} - {response.text}")


# DELETE by ID
def delete_by_id(resource, item_id):
    endpoint = f"{FORBALL_API_URL}/{resource}/{item_id}"
    response = requests.delete(endpoint)
    if response.ok:
        json_resp = response.json()

        singular_map = {
            "teams": "team",
            "tournaments": "tournament",
            "people": "person",
            "matches": "match"
        }

        item = json_resp.get(singular_map.get(resource, resource[:-1])) or json_resp.get(resource)
        if item:
            print(f"{singular_map.get(resource, resource[:-1]).capitalize()} deleted successfully:")
            print_object(item)
        else:
            print(f"{singular_map.get(resource, resource[:-1]).capitalize()} not found in response")
    else:
        print(f"Error: {response.status_code} - {response.text}")


# CREATE
def create(resource, data):
    endpoint = f"{FORBALL_API_URL}/{resource}"
    response = requests.post(endpoint, json=data)
    if response.ok:
        json_resp = response.json()

        singular_map = {
            "teams": "team",
            "tournaments": "tournament",
            "people": "person",
            "matches": "match"
        }

        item = json_resp.get(singular_map.get(resource, resource[:-1])) or json_resp.get(resource)
        if item:
            print_object(item)
        else:
            print(f"{singular_map.get(resource, resource[:-1]).capitalize()} not found in response")
    else:
        print(f"Error: {response.status_code} - {response.text}")


def search_matches(search_params):
    """Search matches with filter parameters"""
    endpoint = f"{FORBALL_API_URL}/matches"
    
    query_string = "&".join([f"{key}={value}" for key, value in search_params.items()])
    if query_string:
        endpoint = f"{endpoint}?{query_string}"
    
    response = requests.get(endpoint)
    if response.ok:
        json_resp = response.json()
        matches = json_resp.get("matches", [])
        metadata = {k: v for k, v in json_resp.items() if k != "matches"}
        
        for match in matches:
            print_object(match)
        
        if metadata:
            print(f"\nMetadata: {metadata}")
    else:
        print(f"Error: {response.status_code} - {response.text}")