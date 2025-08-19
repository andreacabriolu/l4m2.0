class Constant_Strings:
    player = "Player"
    bet = "Bet"
    competition = "Competition"
    market = "Market"
    real_team = "Realteam"
    series = "Series"
    session = "Session"
    team = "Team"
    balance = "Balance"
    user = "User"
    mark_players = "Mark_Players"

class Constant_Dicts:
    RoleNames = {'P':'PORTIERE', 'D':'DIFENSORE','C':'CENTROCAMPISTA','A':'ATTACCANTE'}
    RoleEnum = {'1':'PORTIERE', '2':'DIFENSORE','3':'CENTROCAMPISTA','4':'ATTACCANTE'}
    RoleChars = {'POR': 'P', 'DIF': 'D', 'CC': 'C', 'ATT': 'A'}

class Constant_Lists:
    Modules = ['3-5-2','3-4-3','4-4-2','4-3-3','4-5-1','5-3-2','5-4-1']

NUM_GK = 3
NUM_DEF = 8
NUM_CC = 8
NUM_FW = 6
NUM_SLOTS = 25
MAX_CAROGNATE = 3

NUM_DAYS_AUCTION = 2

class SendBetResult:
    BET_OK = 0
    BET_OVERFLOW = -1
    BET_UNDERFLOW = -2
    BET_EXPIRED = -3
    BET_SLOT_EXCEED = -4

class ErrorCodes:
    ALREADY_OFFICIAL = -1

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

class Modifier_Scores:
    _LT_6 = 0
    _6_625 = 0.5
    _625_65 = 1
    _65_675 = 2
    _675_7 = 3
    _7_725 = 4
    _725_75 = 4.5
    _GT_75 = 6

class Various:
    BASE_SCORE = 66
    THRESHOLD_GOL = 6

class PlayerStatus:
    PLAYING = 0
    NOT_PLAYED = 1
    PLAYED = 2
    YET_TO_PLAY = 3

class Modules:
    _352 = '3-5-2'
    _343 = '3-4-3'
    _442 = '4-4-2'
    _433 = '4-3-3'
    _451 = '4-5-1'
    _532 = '5-3-2'
    _541 = '5-4-1'

