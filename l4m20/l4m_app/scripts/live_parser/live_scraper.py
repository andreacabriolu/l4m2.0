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
    # f = open('fake.json','r')
    f = open(CURRENT_FILE.parents[0] / 'fake.json', 'r')
    resp_json = json.loads(f.read())
    f.close()

#json marks: grades
#json roles: roles
#json day: current day
#json ranking: team results and ranking
#json scores: matches -> foreach json score general info, lineups and events
try:

    current_day = resp_json['day']
    grades = resp_json['marks']

    players = player.Player.objects.all().only('Surname', 'id', 'RealTeam_id')
    real_teams = real_team.RealTeam.objects.filter(Status='A').only('Name', 'id')
    _season = get_current_season()

    votes = {}

    #creating votes ONLY for playing players, warning!
    for name, grade in grades.items():
        name = U.clean_name(name)
        pl = players.filter(Surname=name).first()
        
        if pl is None:
            continue
        _vote = vote.Vote()
        _vote.Player = pl
        _vote.RealTeam = real_teams.filter(id=pl.RealTeam_id).first()
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

        votes[pl.id] = _vote

    for score in resp_json['scores']:
        isLive = score['time'] != C.Events.END_MATCH
        if (isLive): 
            U.set_live(score, votes, players)
        else:
            U.set_final(score, real_teams, current_day, _season)
        match_events = score['events']
        match_extra_events = score['extra_events']
        U.fill_with_events(match_events, 
                           match_extra_events, 
                           players, 
                           votes, 
                           real_teams)

    #complete votes
    for _vote in votes.values():
        _vote.Day = int(current_day)
        _vote.TotVote = U.calculate_totvote(_vote)

    #clean up the table
    U.delete_votes_of_day(current_day, _season)

    #write ONLY final votesName
    U.insert_votes(votes)
    logger.log(logging.INFO, f'executed at {datetime.datetime.now()}')

except Exception as e:
    logger.log(logging.CRITICAL, f'ERROR {e}')



