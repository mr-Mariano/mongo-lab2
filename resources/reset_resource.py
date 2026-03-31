import falcon


class ResetResource:
    def __init__(self, db):
        self.db = db

    async def on_delete(self, req, res):
        self.db.teams.delete_many({})
        self.db.tournaments.delete_many({})
        self.db.matches.delete_many({})
        self.db.people.delete_many({})

        res.media = {"message": "Database reset"}
        res.status = falcon.HTTP_200