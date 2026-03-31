

class Stats:
    def __init__(self,
                 wins : int,
                 draws : int,
                 losses : int,
                 goals_in_favor : int,
                 goals_against : int):
        self.wins = wins
        self.draws = draws
        self.losses = losses
        self.goals_in_favor = goals_in_favor
        self.goals_against = goals_against


    def to_dict(self):
        return {
             "wins" : self.wins,
             "draws" : self.draws,
             "losses" : self.losses,
             "goals_in_favor" : self.goals_in_favor,
             "goals_against" : self.goals_against
        }

class Team:

    def __init__(self,
                 name : str,
                 country : str,
                 stats : Stats ):
        self.name = name
        self.country = country
        self.stats = stats


    def to_dict(self):
        return {
             "name" : self.name,
             "country" : self.country,
             "stats" : self.stats.to_dict()
        }