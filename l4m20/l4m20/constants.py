from dataclasses import dataclass
from typing import Optional


class Constant_Strings:
    player = "Player"
    bet = "Bet"
    competition = "Competition"
    market = "Market"
    real_team = "Realteam"
    season = "Season"
    series = "Series"
    session = "Session"
    team = "Team"
    balance = "Balance"
    user = "User"
    mark_players = "Mark_Players"
    team_competition = "Team_Competition"
    campionato = "Campionato"

class Constant_Dicts:
    RoleNames = {'P':'PORTIERE', 'D':'DIFENSORE','C':'CENTROCAMPISTA','A':'ATTACCANTE'}
    RoleEnum = {'1':'PORTIERE', '2':'DIFENSORE','3':'CENTROCAMPISTA','4':'ATTACCANTE'}
    RoleChars = {'POR': 'P', 'DIF': 'D', 'CC': 'C', 'ATT': 'A'}
    RoleInts = {'P': 0, 'D': 1, 'C': 2, 'A': 3}

class Constant_Lists:
    Modules = ['3-5-2','3-4-3','4-4-2','4-3-3','4-5-1','5-3-2','5-4-1']

class Stages_sorting:
    stages = {
        'Girone': 0,
        'Ottavi': 1,
        'Quarti': 2,
        'Semifinale': 3,
        'Finale': 4
    }

NUM_GK = 3
NUM_DEF = 8
NUM_CC = 8
NUM_FW = 6
NUM_SLOTS = 25
MAX_CAROGNATE = 3
MAX_SVINCOLI = 3
MAX_SUBS = 5
MAX_NON_SCHIERATE = 1
WIN_PT = 3
DRAW_PT = 1
LOSE_PT = 0
WAGE_MULTIPLIER = 0.5
MAX_TRIENNAL_CONTRACTS_PER_ROLE = 1
MIN_ANNUAL_CONTRACTS_PER_ROLE = 1
BID_CANCEL_TIMEOUT = 20

NUM_DAYS_AUCTION = 2

class CancelBidResult:
    CANCEL_OK = 0
    CANCEL_EXPIRED = -1
    CANCEL_NOT_FOUND = -2
    CANCEL_BET_OVERCOME = -3

class SendBetResult:
    BET_OK = 0
    BET_OVERFLOW = -1
    BET_UNDERFLOW = -2
    BET_EXPIRED = -3
    BET_SLOT_EXCEED = -4

@dataclass
class SendBetReturnValues:
    bet_result: int
    bet_id: Optional[int] = None
    residual: Optional[int] = None
    new_balance_for_bets: Optional[int] = None
    n_carognate: Optional[int] = None
    total: Optional[int] = None

class ErrorCodes:
    ALREADY_OFFICIAL = -1
    PLAYER_NOT_IN_SQUAD = -2

class Events:
    GOAL_TAKEN = 'GG'
    GOAL = 'G'
    END_MATCH = 'FT'
    ASS_LOW = ''
    ASS_HIGH = ''
    ASS_STD = ''
    CAP = ''
    GOAL_DECIDER = ''
    PENALTY_SCORED = 'PEN'
    PENALTY_MISSED = 'MP'
    PENALTY_SAVED = 'SP'
    OWN_GOAL = 'OG'
    YELLOW_CARD = 'YC'
    RED_CARD = 'RC'
    YELLOW_RED_CARD = 'RYC'
    PENALTY_PROCURED = ''
    SUB = 'S'

class Scores:
    ASS_LOW = 1
    ASS_HIGH = 1
    ASS_STD = 1
    CAP = 0.5
    GOAL = 3
    GOAL_TAKEN = -1
    GOAL_DECIDER = 1
    PENALTY_SCORED = 2
    PENALTY_MISSED = -2
    PENALTY_SAVED = 3
    OWN_GOAL = -2
    YELLOW = -0.5
    RED = -1
    PENALTY_PROCURED = 1

class Modifier_Scores_4:
    _LT_6 = 0
    _6_625 = 0.5
    _625_65 = 1.5
    _65_675 = 3
    _675_7 = 4.5
    _7_75 = 6
    _GT_75 = 9

class Modifier_Scores_5:
    _LT_6 = 0
    _6_625 = 1
    _625_65 = 2
    _65_675 = 4.5
    _675_7 = 7
    _7_75 = 10
    _GT_75 = 13

class Various:
    OT_BASE_SCORE = 36
    OT_THRESHOLD_GOL = 3
    BASE_SCORE = 66
    THRESHOLD_GOL = 6

class PlayerStatus:
    PLAYING = 0
    NOT_PLAYED = 1
    PLAYED = 2
    YET_TO_PLAY = 3
    NO_PLAY_AT_ALL = 4

class LiveStatus:
    NOTHING = -1
    STARTING = 0
    BENCH = 1
    NO_CALLED = 2

class Modules:
    _352 = '352'
    _343 = '343'
    _442 = '442'
    _433 = '433'
    _451 = '451'
    _532 = '532'
    _541 = '541'

    matrix = {
        _343: 
                {
                    ('D','C'):'KO', 
                    ('D','A'):'KO', 
                    ('C','D'):_433, 
                    ('C','A'):'KO', 
                    ('A','D'):_442, 
                    ('A','C'):_352, 
                },
        _352: 
                {
                    ('D','C'):'KO', 
                    ('D','A'):'KO', 
                    ('C','D'):_442, 
                    ('C','A'):_343, 
                    ('A','D'):_451, 
                    ('A','C'):'KO', 
                },
        _442: 
                {
                    ('D','C'):_352, 
                    ('D','A'):_343, 
                    ('C','D'):_532, 
                    ('C','A'):_433, 
                    ('A','D'):_541, 
                    ('A','C'):_451, 
                },
        _433: 
                {
                    ('D','C'):_343, 
                    ('D','A'):'KO', 
                    ('C','D'):'KO', 
                    ('C','A'):'KO', 
                    ('A','D'):_532, 
                    ('A','C'):_442, 
                },
        _451: 
                {
                    ('D','C'):'KO', 
                    ('D','A'):_352, 
                    ('C','D'):_541, 
                    ('C','A'):_442, 
                    ('A','D'):'KO', 
                    ('A','C'):'KO', 
                },
        _541: 
                {
                    ('D','C'):_451, 
                    ('D','A'):_442, 
                    ('C','D'):'KO', 
                    ('C','A'):_532, 
                    ('A','D'):'KO', 
                    ('A','C'):'KO', 
                },
        _532: 
                {
                    ('D','C'):_442, 
                    ('D','A'):_433, 
                    ('C','D'):'KO', 
                    ('C','A'):'KO', 
                    ('A','D'):'KO', 
                    ('A','C'):_541, 
                }
        
        }
