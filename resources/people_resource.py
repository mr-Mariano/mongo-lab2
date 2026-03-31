#!/usr/bin/env python3
import logging
import falcon
from bson.objectid import ObjectId
from validators import team_validator
import os
from services import people_service

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(BASE_DIR, "../logs")

os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, "people.log")

log = logging.getLogger()
log.setLevel(logging.INFO)

handler = logging.FileHandler(log_file)
handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
))

log.addHandler(handler)


class PeopleResource:
    def __init__(self, db):
        self.db = db

    # Create POST /
    async def on_post_collection(self, req, res):
        data = await req.media

        people_id = people_service.create_people(data, self.db)

        if not people_id:
            log.error("Failed to create person")
            res.status = falcon.HTTP_400
            res.media = { "error" : "Invalid data" }
            return
        
        log.info(f"Person created: {people_id}")
        res.status = falcon.HTTP_201
        res.media = { "person" : people_id }

    # Get all  GET /
    async def on_get_collection(self, req, res):
        people = people_service.get_all_people(self.db)
        log.info(f"People: {people}")
        res.media = { "people" : people}


    # Get by Id  GET /{id}
    async def on_get(self, req, res, id):
        person = people_service.get_people_by_id(id, self.db)
        if person:
            log.info(f"Person: {person}")
            res.media = { "person" : person }
        else:
            log.info(f"Person with id {id} not found")
            res.status = falcon.HTTP_404
            res.media = { "error" : "Person not found" }


    # Update by Id  PUT /{id}
    async def on_put(self, req, res, id):
        try:
            data = await req.media
            result = people_service.update_people_by_id(id, data, self.db)
            res.media = {"person": result}
        except ValueError as e:
            log.error(f"Failed to update person: {e}")
            res.status = falcon.HTTP_400
            res.media = {"error": str(e)}

    # Delete by Id  DELETE /{id}
    async def on_delete(self, req, res, id):
        result = people_service.delete_people_by_id(id, self.db)
        if result:
            log.info(f"Person with id {id} deleted")
            res.media = {"people": "Person deleted"}
        else:
            log.info(f"Person with id {id} not found for deletion")
            res.status = falcon.HTTP_404
            res.media = {"error": "Person not found"}
