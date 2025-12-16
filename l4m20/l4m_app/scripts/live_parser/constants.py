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
    