import constants as C
from db_connector import *

def clean_name(name):
    return name.replace(' ','_').replace('\'','')

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
    if name=='Nico_Paz':
        return 'Paz_N'

    return name

def set_live(score, votes, players):
    hlineup = score['home_lineups']
    hbench = score['home_bench']
    alineup = score['away_lineups']
    abench = score['away_bench']

    for hl in hlineup:
        hl = clean_name(hl)
        if hl not in players:
            continue
        pl_id = players[hl]
        if(pl_id not in votes):
            continue
        vote = votes[pl_id]
        vote.Live = True

    for hp in hbench:
        hp = clean_name(hp)
        if hp not in players:
            continue
        pl_id = players[hp]
        if(pl_id not in votes):
            continue
        vote = votes[pl_id]
        vote.Live = True

    for al in alineup:
        al = clean_name(al)
        if al not in players:
            continue
        pl_id = players[al]
        if(pl_id not in votes):
            continue
        vote = votes[pl_id]
        vote.Live = True

    for ap in abench:
        ap = clean_name(ap)
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
        if 'player' in event and clean_name(event['player']) not in players:
            continue
        if 'in' in event and clean_name(event['in']) not in players:
            continue
        if 'out' in event and clean_name(event['out']) not in players:
            continue
        if 'details' in event and event['details'] != '' and clean_name(event['details']) not in players:
            continue
        
        _type = event['type']
        match _type:
            case C.Events.YELLOW_CARD:
                pl_id = players[clean_name(event['player'])]
                if pl_id is None:
                    continue

                vote = votes[pl_id]
                vote.Yel = 1
            case C.Events.RED_CARD:
                pl_id = players[clean_name(event['player'])]
                if pl_id is None:
                    continue

                vote = votes[pl_id]
                vote.Red = 1

            case C.Events.YELLOW_RED_CARD:
                pl_id = players[clean_name(event['player'])]
                if pl_id is None:
                    continue

                vote = votes[pl_id]
                vote.YelRed = 1

            case C.Events.GOAL:
                pl_id = players[clean_name(event['player'])]
                if pl_id is None:
                    continue
                if event['details'] != '':
                    pl_assist_id = players[clean_name(event['details'])]
                    vote = votes[pl_assist_id]
                    vote.AssS = vote.AssS + 1

                vote = votes[pl_id]
                vote.GoalSc = vote.GoalSc + 1

            case C.Events.GOAL_TAKEN:
                pl_id = players[clean_name(event['player'])]
                if pl_id is None:
                    continue

                vote = votes[pl_id]
                vote.GoalTa = vote.GoalTa + 1

            case C.Events.OWN_GOAL:
                pl_id = players[clean_name(event['player'])]
                if pl_id is None:
                    continue

                vote = votes[pl_id]
                vote.Own = vote.Own + 1

            case C.Events.PENALTY_SCORED:
                pl_id = players[clean_name(event['player'])]
                if pl_id is None:
                    continue

                vote = votes[pl_id]
                vote.PenSc = vote.PenSc + 1

            case C.Events.PENALTY_MISSED:
                pl_id = players[clean_name(event['player'])]
                if pl_id is None:
                    continue

                vote = votes[pl_id]
                vote.PenMi = vote.PenMi + 1

            case C.Events.PENALTY_SAVED:
                pl_id = players[clean_name(event['player'])]
                if pl_id is None:
                    continue

                vote = votes[pl_id]
                vote.PenSa = vote.PenSa + 1

            case C.Events.SUB:
                continue

def delete_votes_of_day(conn:DB_Connector, day):
    if day == "":
        return
    
    try:
        conn.delete("l4m_app_vote", conditions=f"\"Day\"={day}")
    except Exception as e:
        raise e

def insert_votes(conn:DB_Connector, votes):
    try:
        for _,vote in votes.items():
            if vote.Live:
                continue
            data_vote = (vote.Day, 
                         vote.Vote, 
                         vote.GoalSc, 
                         vote.GoalTa, 
                         0, #GoalDe 
                         vote.PenSc, 
                         vote.PenMi,
                         vote.PenSa,
                         vote.Own, 
                         vote.Yel, 
                         vote.Red, 
                         vote.YelRed, 
                         vote.AssS,
                         0, #vote.AssH,
                         0, #vote.AssL,
                         vote.AssP,
                         0, #vote.SubJ,
                         vote.Sub, 
                         vote.Competition,
                         vote.Player,
                         vote.RealTeam,
                         vote.Live)
            conn.insert(table="l4m_app_vote", data=data_vote)
    except Exception as e:
        raise e
    
def get_players_realteam(conn:DB_Connector):
    try:
        return conn.select(table="l4m_app_player", cols='\"id\",\"RealTeam_id\"', conditions='"Status"=%s', data='A')
    except Exception as e:
        raise e
    

def get_players(conn:DB_Connector):
    try:
        return conn.select(table="l4m_app_player", cols='\"Surname\",\"id\"', conditions='"Status"=%s', data='A')
    except Exception as e:
        raise e
    
def get_current_assp(conn:DB_Connector, vote):
    try:
        rows = conn.select(table="l4m_app_vote", cols='\"AssP\"', conditions='"Day"=%s and "Player_id"=%s', data=(vote.Day, vote.Player))
        if len(rows) <= 0:
            return 0
        return rows[0][0]

    except Exception as e:
        raise e