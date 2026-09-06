import datetime
import requests as req
import json
from db_connector import *
from vote_live import *
import constants as C
import utilities as U
import logging
logger = logging.getLogger("live_scraper")

logging.basicConfig(filename='log/scarper.log', level=logging.CRITICAL)

TEST = False

if(not TEST):
    url = "https://publicapi.fantamaster.it/livescores/?tcache=1756165942189"
    resp = req.get(url)
    resp_content = resp.content

    resp_json = json.loads(resp_content)
else:
    f = open('live_parser/fake.json','r')
    resp_json = json.loads(f.read())
    f.close()

#json marks: grades
#json roles: roles
#json day: current day
#json ranking: team results and ranking
#json scores: matches -> foreach json score general info, lineups and events
try:

    conn = DB_Connector()

    current_day = resp_json['day']
    grades = resp_json['marks']

    players = dict(U.get_players(conn))
    players_realteam = dict(U.get_players_realteam(conn))
    real_teams = dict(U.get_realteams(conn))
    season = U.get_current_season(conn)
    today_competitions = U.get_today_competitions(conn, current_day, season)

    votes = {}

    #creating votes ONLY for playing players, warning!
    for name, grade in grades.items():
        name = U.clean_name(name)
        if name not in players:
            continue
        vote = Vote_Live_Obj()
        vote.Player = players[name]
        vote.Vote = float(grade)
        vote.TotVote = 0.0
        vote.GoalSc = 0
        vote.GoalTa = 0
        vote.PenSc = 0
        vote.PenMi = 0
        vote.PenSa = 0
        vote.Own = 0
        vote.Yel = 0
        vote.Red = 0
        vote.YelRed = 0
        vote.AssS = 0
        vote.AssP = 0
        vote.Live = False
        vote.Sub = 0
        vote.RealTeam = players_realteam[players[name]]
        vote.Season = season

        votes[players[name]] = vote

    for score in resp_json['scores']:
        isLive = score['time'] != C.Events.END_MATCH
        if (isLive): 
            U.set_live(score, votes, players)
        else:
            U.set_final(conn, score, real_teams, current_day, season)
        match_events = score['events']
        U.fill_with_events(match_events, players, votes, players_realteam)

    #complete votes
    for _,vote in votes.items():
        vote.Day = int(current_day)
        vote.AssP = U.get_current_assp(conn, vote, season)
        vote.TotVote = U.calculate_totvote(vote)
        vote.Season = season

    #clean up the table
    U.delete_votes_of_day(conn, current_day, season)

    #write ONLY final votes
    U.insert_votes(conn, votes, today_competitions)
    conn.commit()
    logger.log(logging.INFO, f'executed at {datetime.datetime.now()}')

except Exception as e:
    logger.log(logging.CRITICAL, f'ERROR {e}')
    pass



