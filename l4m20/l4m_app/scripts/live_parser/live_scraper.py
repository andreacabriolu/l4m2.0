import requests as req
import json
from db_connector import *
from vote_live import *
import constants as C
import utilities as U

TEST = False

#google-chrome --headless --dump-dom 'http://lega4mori.com/l4m/live/' > file.html
url_fg = "https://www.fantacalcio.it/serie-a/calendario/1/2025-26/atalanta-pisa/16670/voti"


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

conn = DB_Connector()

current_day = resp_json['day']
grades = resp_json['marks']

players = dict(U.get_players(conn))

votes = {}

#creating votes ONLY for playing players, warning!
for name, grade in grades.items():
    name = name.replace(' ','_')
    #FOOL name exceptions
    # name = U.manage_fool_name_exceptions(name)
    if name not in players:
        continue
    vote = Vote_Live_Obj()
    vote.Player = players[name]
    vote.Vote = float(grade)
    vote.GoalSc = 0
    vote.GoalTa = 0
    vote.PenSc = 0
    vote.PenMi = 0
    vote.PenSa = 0
    vote.Own = 0
    vote.Yel = 0
    vote.Red = 0
    vote.AssS = 0
    vote.Live = False
    vote.Sub = 0

    votes[players[name]] = vote

for score in resp_json['scores']:
    isLive = score['time'] != C.Events.END_MATCH
    if (isLive): 
        U.set_live(score, votes, players)
    match_events = score['events']
    U.fill_with_events(match_events, players, votes)

#complete votes
for _,vote in votes.items():
    vote.Day = int(current_day)
    vote.Competition = int(1) #TODO magic number: campionato


#write ONLY final votes
U.insert_votes(conn, votes)
conn.commit()





