#!/usr/bin/env python3
import logging
import falcon
import os
import services.tournament_service as tournament_service

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(BASE_DIR, "../logs")

os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, "tournaments.log")

log = logging.getLogger()
log.setLevel(logging.INFO)

handler = logging.FileHandler(log_file)
handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
))

log.addHandler(handler)


class TournamentResource:
    def __init__(self, db):
        self.db = db

    # Create POST /
    async def on_post_collection(self, req, res):
        data = await req.media
        tournament_id = tournament_service.create_tournament(data, self.db)

        log.info(f"Tournament created: {tournament_id}")

        res.status = falcon.HTTP_201
        res.media = {"tournament": tournament_id}

    # Get all  GET /
    async def on_get_collection(self, req, res):
        tournaments = tournament_service.get_all_tournaments(self.db)
        res.media = { "tournaments" : tournaments }

    # Get by Id  GET /{id}
    async def on_get(self, req, res, id):
        tournament = tournament_service.get_tournament_by_id(id, self.db)
        res.media = { "tournament" : tournament }

    # Update by Id  PUT /{id}
    async def on_put(self, req, res, id):
        data = await req.media
        tournament = tournament_service.update_tournament(id, data, self.db)
        log.info(f"Tournament updated: {id}")
        res.media = { "tournament" : tournament}

    # Delete by Id  DELETE /{id}
    async def on_delete(self, req, res, id):
        deleted = tournament_service.delete_tournament(id, self.db)
        if deleted:
            log.info(f"Tournament deleted with id: {id}")
            res.status = falcon.HTTP_200
            res.media = {"tournament": "Tournament deleted successfully"}
        else:
            res.status = falcon.HTTP_404
            res.media = {"error": "Tournament not found"}


