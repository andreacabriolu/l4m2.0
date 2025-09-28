from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _
from . import player


class Vote(models.Model):

    Competition = models.ForeignKey(on_delete=models.CASCADE,to=C.Constant_Strings.competition, null=True)
    Player = models.ForeignKey(on_delete=models.CASCADE, to=C.Constant_Strings.player, null=True)
    RealTeam = models.ForeignKey(on_delete=models.CASCADE,to=C.Constant_Strings.real_team, null=True)
    Day = models.IntegerField()              # day of play
    Vote = models.FloatField(default=0.0)    # vote
    GoalSc = models.IntegerField(default=0)  # gol scored
    GoalTa = models.IntegerField(default=0)  # gol taken
    GoalDe = models.IntegerField(default=0)  # bonus: decider, gol partita, not used, maybe one day, maybe not
    PenSc = models.IntegerField(default=0)   # penalty scored
    PenMi = models.IntegerField(default=0)   # penalty missed
    PenSa = models.IntegerField(default=0)   # penalty saved
    Own = models.IntegerField(default=0)     # own goal
    Yel = models.IntegerField(default=0)     # yellow card
    Red = models.IntegerField(default=0)     # red card
    AssS = models.IntegerField(default=0)    # assist standard
    AssH = models.IntegerField(default=0)    # assist high # not necessarily to be used
    AssL = models.IntegerField(default=0)    # assist low # not necessarily to be used
    AssP = models.IntegerField(default=0)    # penalty procured
    SubJ = models.IntegerField(default=0)    # sub-judice: all bonuses are to be confirmed
    Sub = models.FloatField(default=0.0)     # substitution: +30 in at minute 30, -87 out at minute 87
    Live = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.Player} - Giornata {self.Day} ({self.Vote})"
    
    class Vote_Obj():
        Competition = str
        Player = player
        Day : int=0             
        Vote = float   
        GoalSc : int=0   
        GoalTa : int=0 
        GoalDe : int=0 
        PenSc : int=0 
        PenMi : int=0 
        PenSa : int=0 
        Own : int=0 
        Yel : int=0 
        Red : int=0   
        YelRed : int=0   
        AssS : int=0
        AssH : int=0  
        AssL : int=0  
        AssP : int=0 
        SubJ : int=0 
        Sub : int=0 
        Cap : bool=False
        TotVote = float
        Status = int
        LiveStatus = int
        ChangedIn = str
        ChangedOut = str
        Msg = str

