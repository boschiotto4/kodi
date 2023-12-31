from bs4 import BeautifulSoup
import requests
from .config import CONF
from time import sleep
from datetime import datetime, timedelta
 
import xbmc

def log(strng):
    xbmc.log(str(strng), xbmc.LOGERROR)

class GetData:
    """
    A class that gets data/stats from the https://www.sports-reference.com/
    ...
    Attributes
    ----------
    league: str
        Bundesliga has only 18 teams instead of 20. So there is if statement to check if it is a Bundesliga
        to return 18 team stats.

    Methods
    ----------
    get_club_name: Gets name of the team. "[1:]" in "self.array.append(pos.get_text()[1:])" is to get rid of
    the whitespace that method returns.

    get_points: Simply, it's a method that gets the points.

    get_matches_played: Gets the number of matches they played.

    get_wins: Gets the number of wins.

    get_draws: Gets the number of draws.

    get_losses: Gets the number of losses.

    get_goals_for: Gets the number of scored goals.

    get_goals_against: Gets the number of conceded goals.

    get_goal_diff: Gets the difference of get_goals_for and get_goals_against.

    get_top_scorer: Gets the name of the team's top scorer.
    """
    def __init__(self, league):
        page = requests.get(CONF['url']+league)
        self.soup = BeautifulSoup(page.content, features="html.parser")
        self.league = ""
        self.array = []
        self.pos = []
        self.clubs = []
        self.points = []
        self.games = []
        self.wins = []
        self.draws = []
        self.losses = []
        self.goals_for = []
        self.goals_against = []
        self.goal_diff = []
        self.top_scorer = []
        self.league = league

    def get_position(self):
        raw_response = self.soup.find_all('th', {'data-stat': 'rank'})
        for pos in raw_response:
            self.array.append(pos.get_text())
        self.pos += self.array
        if self.league == "comps/20/Bundesliga-Stats" or self.league == "comps/23/Dutch-Eredivisie-Stats":

            return self.pos[-18:]
        elif self.league == "comps/30/Russian-Premier-League-Stats":

            return self.pos[-16:]
        elif self.league == "comps/10/Championship-Stats":

            return self.pos[-24:]

        return self.pos[-20:]


    def get_scheduling(self):
#        raw_response = self.soup.find_all('th', {'data-stat': 'gameweek'})
        ret = []
        gameWeekId = ''
        raw_response = self.soup.find_all('td', {'data-stat': 'date'})
        # Search for the next 4 days match
        today = datetime.now()
        mfounded = False
        for d in range(0,4):
            if mfounded:
                break
            evaluate = today + timedelta(d)
            tday = (evaluate).strftime("%Y%m%d")
            for dat in raw_response:
                if dat.has_attr('csk') and dat.attrs['csk'] == tday: #'20231021':
                    mfounded = True
                    # Get game week
                    el = dat.parent.find_all('th', {'data-stat' : 'gameweek'})
                    gameWeekId = el[0].contents[0]
                    break
           
        # Find all the match of the gameweek
        #log('resuyyy ' + str(gameWeekId))
        for match in raw_response:
            gw = match.parent.find_all('th', {'data-stat' : 'gameweek'})
            if len(gw[0].contents) and gw[0].contents[0] == str(gameWeekId):
                el = match.parent.find_all('td', {'data-stat' : 'home_team'})
                hn = el[0].select_one("a" , recursive=False).contents
                el = match.parent.find_all('td', {'data-stat' : 'away_team'})
                an = el[0].select_one("a" , recursive=False).contents
                el = match.parent.find_all('td', {'data-stat' : 'start_time'})
                hour = el[0].select_one("span" , recursive=False).contents[0]
                el = match.parent.find_all('td', {'data-stat' : 'date'})
                thedate = el[0].select_one("a" , recursive=False).contents[0]

                match_data = {
                    'home' : hn[0],
                    'away' : an[0],
                    'date' : thedate,
                    'time' : hour
                }
                ret.append(match_data)
        
        #log(str(ret))
        return ret
        
    def get_club_name(self):
        raw_response = self.soup.find_all('td', {'class': 'left'})
        for team in raw_response:
            self.array.append(team.get_text()[1:])
        self.clubs += self.array
        if self.league == "comps/20/Bundesliga-Stats" or self.league == "comps/23/Dutch-Eredivisie-Stats":

            return self.clubs[-18:]
        elif self.league == "comps/30/Russian-Premier-League-Stats":

            return self.clubs[-16:]
        elif self.league == "comps/10/Championship-Stats":

            return self.clubs[-24:]

        return self.clubs[-20:]

    def get_points(self):
        raw_response = self.soup.find_all('td', {'data-stat': 'points'})
        for points in raw_response:
            self.array.append(points.get_text())
        self.points += self.array
        if self.league == "comps/20/Bundesliga-Stats" or self.league == "comps/23/Dutch-Eredivisie-Stats":
            return self.points[-18:]
        elif self.league == "comps/30/Russian-Premier-League-Stats":

            return self.points[-16:]
        elif self.league == "comps/10/Championship-Stats":

            return self.points[-24:]

        return self.points[-20:]

    def get_matches_played(self):
        raw_response = self.soup.find_all('td', {'data-stat': 'games'})
        for games in raw_response:
            self.array.append(games.get_text())
            #xbmc.log(str(games.get_text()), xbmc.LOGERROR)

        self.games += self.array
        if self.league == "comps/20/Bundesliga-Stats" or self.league == "comps/23/Dutch-Eredivisie-Stats":
            return self.games[-18:]
        elif self.league == "comps/30/Russian-Premier-League-Stats":

            return self.games[-16:]
        elif self.league == "comps/10/Championship-Stats":

            return self.games[-24:]

        return self.games[-20:]

    def get_wins(self):
        raw_response = self.soup.find_all('td', {'data-stat': 'wins'})
        for wins in raw_response:
            self.array.append(wins.get_text())
        self.wins += self.array
        if self.league == "comps/20/Bundesliga-Stats" or self.league == "comps/23/Dutch-Eredivisie-Stats":
            return self.wins[-18:]
        elif self.league == "comps/30/Russian-Premier-League-Stats":

            return self.wins[-16:]
        elif self.league == "comps/10/Championship-Stats":

            return self.wins[-24:]

        return self.wins[-20:]

    def get_draws(self):
        raw_response = self.soup.find_all('td', {'data-stat': 'draws'})
        for draws in raw_response:
            self.array.append(draws.get_text())
        self.draws += self.array
        if self.league == "comps/20/Bundesliga-Stats" or self.league == "comps/23/Dutch-Eredivisie-Stats":
            return self.draws[-18:]
        elif self.league == "comps/30/Russian-Premier-League-Stats":

            return self.draws[-16:]
        elif self.league == "comps/10/Championship-Stats":

            return self.draws[-24:]

        return self.draws[-20:]

    def get_losses(self):
        raw_response = self.soup.find_all('td', {'data-stat': 'losses'})
        for losses in raw_response:
            self.array.append(losses.get_text())
        self.losses += self.array
        if self.league == "comps/20/Bundesliga-Stats" or self.league == "comps/23/Dutch-Eredivisie-Stats":
            return self.losses[-18:]
        elif self.league == "comps/30/Russian-Premier-League-Stats":

            return self.losses[-16:]
        elif self.league == "comps/10/Championship-Stats":

            return self.losses[-24:]

        return self.losses[-20:]

    def get_goals_for(self):
        raw_response = self.soup.find_all('td', {'data-stat': 'goals_for'})
        for gf in raw_response:
            self.array.append(gf.get_text())
        self.goals_for += self.array
        if self.league == "comps/20/Bundesliga-Stats" or self.league == "comps/23/Dutch-Eredivisie-Stats":
            return self.goals_for[-18:]
        elif self.league == "comps/30/Russian-Premier-League-Stats":

            return self.goals_for[-16:]
        elif self.league == "comps/10/Championship-Stats":

            return self.goals_for[-24:]

        return self.goals_for[-20:]

    def get_goals_against(self):
        raw_response = self.soup.find_all('td', {'data-stat': 'goals_against'})
        for ga in raw_response:
            self.array.append(ga.get_text())
        self.goals_against += self.array
        if self.league == "comps/20/Bundesliga-Stats" or self.league == "comps/23/Dutch-Eredivisie-Stats":
            return self.goals_against[-18:]
        elif self.league == "comps/30/Russian-Premier-League-Stats":

            return self.goals_against[-16:]
        elif self.league == "comps/10/Championship-Stats":

            return self.goals_against[-24:]

        return self.goals_against[-20:]

    def get_goal_diff(self):
        raw_response = self.soup.find_all('td', {'data-stat': 'goal_diff'})
        for gd in raw_response:
            self.array.append(gd.get_text())
        self.goal_diff += self.array
        if self.league == "comps/20/Bundesliga-Stats" or self.league == "comps/23/Dutch-Eredivisie-Stats":
            return self.goal_diff[-18:]
        elif self.league == "comps/30/Russian-Premier-League-Stats":

            return self.goal_diff[-16:]
        elif self.league == "comps/10/Championship-Stats":

            return self.goal_diff[-24:]

        return self.goal_diff[-20:]

    def get_top_scorer(self):
        raw_response = self.soup.find_all('td', {'data-stat': 'top_team_scorers'})
        for top_scorer in raw_response:
            self.array.append(top_scorer.get_text())
        self.top_scorer += self.array
        if self.league == "comps/20/Bundesliga-Stats" or self.league == "comps/23/Dutch-Eredivisie-Stats":
            return self.top_scorer[-18:]
        elif self.league == "comps/30/Russian-Premier-League-Stats":

            return self.top_scorer[-16:]
        elif self.league == "comps/10/Championship-Stats":

            return self.top_scorer[-24:]

        return self.top_scorer[-20:]
