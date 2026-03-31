#!/usr/bin/env python3
import logging
import falcon
from bson.objectid import ObjectId
import services.team_service as team_service
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(BASE_DIR, "../logs")

os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, "teams.log")

log = logging.getLogger()
log.setLevel(logging.INFO)

handler = logging.FileHandler(log_file)
handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
))

log.addHandler(handler)

class TeamResource:
    def __init__(self, db):
        self.db = db

    # Create POST /
    async def on_post_collection(self, req, res):
        data = await req.media

        team_id = team_service.create_team(data, self.db)

        log.info(f"Team created: {team_id}")

        res.status = falcon.HTTP_201
        res.media = {"team": team_id}

    # Get all  GET /
    async def on_get_collection(self, req, res):
        teams = team_service.get_all_teams(self.db)

        log.info(f"Teams: {teams}")
        res.media = {"teams" : teams}

    # Get by Id  GET /{id}
    async def on_get(self, req, res, id):
        team = team_service.get_team_by_id(id, self.db)
        if team:
            log.info(f"Team: {team}")
            res.media = {"team": team}
        else:
            res.status = falcon.HTTP_404
            res.media = {"error": "Team not found"}

    # Update by Id  PUT /{id}
    async def on_put(self, req, res, id):
        data = await req.media
        updated_team = team_service.update_team_by_id(id, data, self.db)
        if updated_team:
            log.info(f"Team updated: {updated_team}")
            res.media = {"team": updated_team}
        else:
            res.status = falcon.HTTP_404
            res.media = {"error": "Team not found"}

    # Delete by Id  DELETE /{id}
    async def on_delete(self, req, res, id):
        deleted_team = team_service.delete_team_by_id(id, self.db)
        if deleted_team:
            log.info(f"Team deleted: {deleted_team}")
            res.media = {"team": deleted_team}
        else:
            res.status = falcon.HTTP_404
            res.media = {"error": "Team not found"}
