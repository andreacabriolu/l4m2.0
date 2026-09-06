import io
import os
import sys
from pathlib import Path

CURRENT_FILE = Path(__file__).resolve()

for parent in CURRENT_FILE.parents:
    if (parent / "manage.py").exists():
        PROJECT_ROOT = parent
        break
else:
    raise RuntimeError(
        "Django project root not found"
    )

sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "l4m20.settings"
)

import django
django.setup()

import datetime
import requests as req
import json
from db_connector import *
from vote_live import *
import constants as C
import utilities as U
import logging
logger = logging.getLogger("live_scraper")
from l4m_app.single_models import competition_calendar, player, vote, real_team, season
from l4m_app.utilities import get_current_season


logging.basicConfig(filename='scarper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') #TODO: check path

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

    players = player.Player.objects.all().values_list('Surname', 'id')
    real_teams = real_team.RealTeam.objects.filter(Status='A').values_list('Name', 'id')
    _season = get_current_season()
    today_competitions = competition_calendar.CompetitionCalendar.objects.filter(Day=current_day, Season=_season).values_list('Competition_id', flat=True)
    # players = dict(U.get_players(conn))
    # players_realteam = dict(U.get_players_realteam(conn))
    # real_teams = dict(U.get_realteams(conn))
    # season = U.get_current_season(conn)
    # today_competitions = U.get_today_competitions(conn, current_day, season)

    votes = {}

    #creating votes ONLY for playing players, warning!
    for name, grade in grades.items():
        name = U.clean_name(name)
        if name not in players:
            continue
        # _vote = Vote_Live_Obj()
        _vote = vote.Vote()
        _player = players.filter(Surname=name).first()
        _vote.Player = _player
        _vote.RealTeam = _player.RealTeam
        _vote.Vote = float(grade)
        _vote.TotVote = 0.0
        _vote.GoalSc = 0
        _vote.GoalTa = 0
        _vote.PenSc = 0
        _vote.PenMi = 0
        _vote.PenSa = 0
        _vote.Own = 0
        _vote.Yel = 0
        _vote.Red = 0
        _vote.YelRed = 0
        _vote.AssS = 0
        _vote.AssP = 0
        _vote.Live = False
        _vote.Sub = 0
        _vote.Season = _season

        votes[_player.id] = _vote

    for score in resp_json['scores']:
        isLive = score['time'] != C.Events.END_MATCH
        if (isLive): 
            U.set_live(score, votes, players)
        else:
            U.set_final(conn, score, real_teams, current_day, _season)
        match_events = score['events']
        U.fill_with_events(match_events, players, votes)

    #complete votes
    for _,vote in votes.items():
        vote.Day = int(current_day)
        vote.AssP = U.get_current_assp(conn, vote)
        vote.TotVote = U.calculate_totvote(vote)
        vote.Season = _season

    #clean up the table
    U.delete_votes_of_day(conn, current_day, _season)

    #write ONLY final votes
    U.insert_votes(conn, votes, today_competitions)
    conn.commit()
    logger.log(logging.INFO, f'executed at {datetime.datetime.now()}')

except Exception as e:
    logger.log(logging.CRITICAL, f'ERROR {e}')
    pass



