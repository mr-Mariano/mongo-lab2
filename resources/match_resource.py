#!/usr/bin/env python3
import logging
import falcon
from bson.objectid import ObjectId
from validators import team_validator
import os
from services import match_service

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(BASE_DIR, "../logs")

os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, "matches.log")

log = logging.getLogger()
log.setLevel(logging.INFO)

handler = logging.FileHandler(log_file)
handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
))

log.addHandler(handler)


class MatchResource:
    def __init__(self, db):
        self.db = db

    # Create POST /
    async def on_post_collection(self, req, res):
        data = await req.media

        match_id = match_service.create_match(data, self.db)

        res.status = falcon.HTTP_201
        res.media = {"match": match_id}

    # Get all  GET /
    async def on_get_collection(self, req, res):
        """GET /matches - Get all matches with filters and pagination"""
        try:
            # Parse parameters
            limit, skip = match_service.parse_pagination(req)
            params = match_service.parse_filter_params(req)
            
            # Build filter
            query_filter = match_service.build_match_filter(params, self.db)
            if query_filter is None:
                res.media = {"matches": [], "limit": limit, "skip": skip, "total": 0, "returned": 0}
                return
            
            # Execute query
            total_count = self.db.matches.count_documents(query_filter)
            matches = list(self.db.matches.find(query_filter).skip(skip).limit(limit))
            
            # Convert for response
            matches = match_service.convert_matches_for_response(matches, self.db)
            
            res.media = {
                "matches": matches,
                "limit": limit,
                "skip": skip,
                "total": total_count,
                "returned": len(matches)
            }
            
        except Exception as e:
            log.error(f"ERROR in on_get_collection: {str(e)}", exc_info=True)
            raise falcon.HTTPInternalServerError(
                title="Internal Server Error",
                description=str(e)
            )


    # Get by Id  GET /{id}
    async def on_get(self, req, res, id):
        match = match_service.get_match_by_id(id, self.db)
        if match:
            log.info(f"Match: {match}")
            res.media = {"match": match}
        else:
            res.status = falcon.HTTP_404
            res.media = {"error": "Match not found"}


    # Update by Id  PUT /{id}
    async def on_put(self, req, res, id):
        data = await req.media
        updated_match = match_service.update_match(id, data, self.db)
        if updated_match:
            log.info(f"Updated Match: {updated_match}")
            res.media = {"match": updated_match}
        else:
            res.status = falcon.HTTP_404
            res.media = {"error": "Match not found"}

    # Delete by Id  DELETE /{id}
    async def on_delete(self, req, res, id):
        deleted = match_service.delete_match(id, self.db)
        if deleted:
            log.info(f"Deleted Match with id: {id}")
            res.status = falcon.HTTP_200
            res.media = {"match": "Match deleted successfully"}
        else:
            res.status = falcon.HTTP_404
            res.media = {"error": "Match not found"}

