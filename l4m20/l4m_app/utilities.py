from .models import *
from django.db.models import Q

# SELECT
# 	"pl"."id","pl."Surname","pl."Role,
# 	"r"."Name" AS REALTEAMNAME,
# 	"b"."Amount","b"."Expiration_Date",
# 	"t"."Name" AS TEAMNAME
# FROM
# 	PUBLIC.L4M_APP_PLAYER PL
# 	LEFT JOIN L4M_APP_BET B ON "pl"."id" = "b"."Player_id"
# 	JOIN L4M_APP_REALTEAM R ON "pl"."RealTeam_id" = "r"."id"
# 	LEFT JOIN L4M_APP_TEAM T ON "b"."Team_id" = "t"."id"
# WHERE
# 	"pl"."Role" = filter_role
# 	AND (
# 		"b"."Best" = TRUE
# 		OR "b"."Best" IS NULL
# 	)
def get_players(filter_role):
    return player.Player.objects.\
        filter(Q(bet__Best=True) | Q(bet__Best=None)).\
        filter(Role=filter_role).\
        filter(RealTeam__isnull=False).\
        values('id','Surname','Name','Role','RealTeam__Name','bet__Amount','bet__Expiration_Date','bet__Team_id__Name')

def get_my_best_bets(teamid):
    return bet.Bet.objects.\
        filter(Q(Best=True) & Q(Team_id=teamid)).\
        values('Amount','Player_id__Surname','Expiration_Date','Slot')