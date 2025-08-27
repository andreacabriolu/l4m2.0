import urllib
import requests as req
from urllib.request import urlopen
import html.parser as hp
from html_parser import LiveHTMLParser
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import constants as C
from live_parser import vote_live
from live_parser.db_connector import DB_Connector

def manage_fool_name_exceptions(name):
    if name=='Ederson_J':
        return 'Ederson_DS'
    if name=='Anguissa':
        return 'Zambo_Anguissa'
    if name=='Ndicka':
        return 'NDicka'
    if name=='Pellegrino_Ma':
        return 'Pellegrino_M'
    if name=='Iker_Bravo':
        return 'Bravo'
    if name=='Pedro R':
        return 'Pedro'
    if name=='Bernabe\'':
        return 'Bernabè'
    if name=='Giovane_S':
        return 'Giovane'
    if name=='N\'Dri':
        return 'NDri'
    if name=='Davis':
        return 'Davis_K'
    if name=='Dele_Bashiru':
        return 'Dele-Bashiru'
    if name=='Bradaric_D':
        return 'Bradaric'
    if name=='Vitinha':
        return 'Vitinha_O'
    if name=='Locatelli_M':
        return 'Locatelli'
    if name=='Lazzari_M':
        return 'Lazzari'
    if name=='Danilo_Veiga':
        return 'Veiga_D'
    if name=='Wesley_F':
        return 'Wesley'
    if name=='Ranieri':
        return 'Ranieri_L'


    return name

def set_live(score, votes, players):
    hlineup = score['home_lineups']
    hbench = score['home_bench']
    alineup = score['away_lineups']
    abench = score['away_bench']

    for hl in hlineup:
        if hl not in players:
            continue
        pl_id = players[hl]
        if(pl_id not in votes):
            continue
        vote = votes[pl_id]
        vote.Live = True

    for hp in hbench:
        if hp not in players:
            continue
        pl_id = players[hp]
        if(pl_id not in votes):
            continue
        vote = votes[pl_id]
        vote.Live = True

    for al in alineup:
        if al not in players:
            continue
        pl_id = players[al]
        if(pl_id not in votes):
            continue
        vote = votes[pl_id]
        vote.Live = True

    for ap in abench:
        if ap not in players:
            continue
        pl_id = players[ap]
        if(pl_id not in votes):
            continue
        vote = votes[pl_id]
        vote.Live = True

def fill_with_events(events, players, votes):
    for event in events:
        
        #TODO: absolutely improve
        if 'player' in event and event['player'] not in players:
            continue
        if 'in' in event and event['in'] not in players:
            continue
        if 'out' in event and event['out'] not in players:
            continue
        if 'details' in event and event['details'] != '' and event['details'] not in players:
            continue
        
        _type = event['type']
        match _type:
            case C.Events.YELLOW_CARD:
                pl_id = players[event['player']]
                if pl_id is None:
                    continue

                vote = votes[pl_id]
                vote.Yel = 1
            case C.Events.RED_CARD:
                pl_id = players[event['player']]
                if pl_id is None:
                    continue

                vote = votes[pl_id]
                vote.Red = 1

            case C.Events.GOAL:
                pl_id = players[event['player']]
                if pl_id is None:
                    continue
                if event['details'] != '':
                    pl_assist_id = players[event['details']]
                    vote = votes[pl_assist_id]
                    vote.AssS = vote.AssS + 1

                vote = votes[pl_id]
                vote.GoalSc = vote.GoalSc + 1

            case C.Events.GOAL_TAKEN:
                pl_id = players[event['player']]
                if pl_id is None:
                    continue

                vote = votes[pl_id]
                vote.GoalTa = vote.GoalTa + 1

            case C.Events.OWN_GOAL:
                pl_id = players[event['player']]
                if pl_id is None:
                    continue

                vote = votes[pl_id]
                vote.Own = vote.Own + 1

            case C.Events.SUB:
                pl_in_id = players[event['in']]
                pl_out_id = players[event['out']]
                vote_in = votes[pl_in_id]
                vote_out = votes[pl_out_id]
                vote_in.Sub = int(event['minute'])
                vote_out.Sub = int(event['minute']) * (-1)
    

def get_players(conn:DB_Connector):
    try:
        return conn.select(table="l4m_app_player", cols='\"Surname\",\"id\"', conditions='"Status"=\'A\'')
    except Exception as e:
        raise e
    