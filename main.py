#!/usr/bin/env python3
import falcon.asgi as falcon
from pymongo import MongoClient
import logging

from resources.team_resource import TeamResource
from resources.tournament_resource import TournamentResource
from resources.people_resource import PeopleResource
from resources.match_resource import MatchResource
from resources.reset_resource import ResetResource


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoggingMiddleware:
    async def process_request(self, req, resp):
        logger.info(f"Request: {req.method} {req.uri}")

    async def process_response(self, req, resp, resource, req_succeeded):
        logger.info(f"Response debug: {resp.status} for {req.method} {req.uri}")


# Initialize MongoDB client and database
client = MongoClient('mongodb://localhost:27017/')
db = client.ForbAll

# Create the Falcon application
app = falcon.App(middleware=[LoggingMiddleware()])

# Instantiate the resources
team_resource = TeamResource(db)
tournament_resource = TournamentResource(db)
match_resource = MatchResource(db)
people_resource = PeopleResource(db)
reset_resource = ResetResource(db)

# Add routes to serve the resources
"""
    Operation	Endpoint Example
    Create	    POST /resource
    Get all	    GET /resource
    Get by ID	GET /resource/{id}
    Update	    PUT /resource/{id}
    Delete	    DELETE /resource/{id}
"""

app.add_route('/reset', reset_resource)

app.add_route('/teams', team_resource, suffix="collection")
app.add_route('/teams/{id}', team_resource)

app.add_route('/tournaments', tournament_resource, suffix="collection")
app.add_route('/tournaments/{id}', tournament_resource)

app.add_route('/people', people_resource, suffix="collection")
app.add_route('/people/{id}', people_resource)

app.add_route('/matches', match_resource, suffix="collection")
app.add_route('/matches/{id}', match_resource)

