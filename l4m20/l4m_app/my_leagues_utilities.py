
from .models import *
from django.db.models import Q
from .live_utilities import pick_worst_11
from l4m20 import constants as C
from .libs import *
from .utilities import *
import json


def get_panchina_doro_flat_data(day=None):
    flat_data = []

    # Configurazioni Pesi (P1, P2, P3)
    WEIGHTS = (C.Pdoro.WEIGHTS['P1'],
               C.Pdoro.WEIGHTS['P2'],
               C.Pdoro.WEIGHTS['P3'])

    curr_season = get_current_season()

    teams = team.Team.objects.filter(
        Series__Competition_id=1,
        Series__Season_id=curr_season.id,   
    ).distinct().order_by('Name')

    for t in teams:

        _series = get_my_series(t.id, competitionid=1)

        camp_res = matches_results.MatchesResults.objects.filter(
            Team_id=t.id,
            MatchesCalendar__Series__in=_series,
            MatchesCalendar__CompetitionCalendar__Day=day
        ).values('Fp').first()

        b11_res = b11_results.B11Results.objects.filter(
            Team_id=t.id,
            Day=day
        ).values('B11Fp').first()

        fp = float(camp_res['Fp']) if camp_res and camp_res['Fp'] is not None else 0.0
        b11_fp = float(b11_res['B11Fp']) if b11_res and b11_res['B11Fp'] is not None else 0.0

        # -------------------------------------------------------------
        # CALCOLO W11 AL VOLO
        # -------------------------------------------------------------
        w11_fp = 0.0

        # Recuperiamo i giocatori in rosa per la squadra nella stagione corrente
        squad_players = squads.Squads.objects.filter(
            Team_id=t.id,
            Quarantine=False,
            Season=curr_season
        ).select_related('Player')

        player_ids = [s.Player_id for s in squad_players]

        # Recuperiamo i voti per la giornata 'day'
        votes_qs = vote.Vote.objects.filter(
            Player_id__in=player_ids,
            Day=day
        )
        votes_dict = {v.Player_id: v for v in votes_qs}

        # Suddividiamo per ruolo ed associamo l'oggetto voti
        keepers, defenders, midfielders, attackers = [], [], [], []

        for s in squad_players:
            p = s.Player
            # Assegniamo l'oggetto voti al giocatore (o un mock vuoto se svincolato/senza voto)
            p.votes = votes_dict.get(p.id, vote.Vote(Vote=None, TotVote=None))

            if p.Role == 'P':
                keepers.append(p)
            elif p.Role == 'D':
                defenders.append(p)
            elif p.Role == 'C':
                midfielders.append(p)
            elif p.Role == 'A':
                attackers.append(p)

        # Ordiniamo in senso CRESCENTE per W11
        k_w = sorted(keepers, key=lambda p: (p.votes.TotVote if p.votes.TotVote is not None else C.Pdoro.MAX_VAL))
        d_w = sorted(defenders, key=lambda p: (p.votes.TotVote if p.votes.TotVote is not None else C.Pdoro.MAX_VAL))
        m_w = sorted(midfielders, key=lambda p: (p.votes.TotVote if p.votes.TotVote is not None else C.Pdoro.MAX_VAL))
        a_w = sorted(attackers, key=lambda p: (p.votes.TotVote if p.votes.TotVote is not None else C.Pdoro.MAX_VAL))

        worst_res = pick_worst_11(k_w, d_w, m_w, a_w)
        w11_fp = float(worst_res['score']) if worst_res else 0.0

        # ~ # -------------------------------------------------------------
        # PARAMETRO 1: (FP - W11) / (B11 - W11)
        # -------------------------------------------------------------
        if (b11_fp - w11_fp) > 0:
            param1 = round((fp - w11_fp) / (b11_fp - w11_fp), 3)
            param1 = max(0.0, min(param1, 1.0))
        else:
            param1 = 1.0

        # -------------------------------------------------------------
        # PARAMETRO 2: Profondità rosa (Voti movimento / 22)
        # -------------------------------------------------------------
        field_players_with_vote = 0
        lineup_obj = lineup.Lineup.objects.filter(
            Team_id=t.id,
            Series__in=_series,
            Day=day
        ).order_by('-Version').first()

        if lineup_obj and lineup_obj.Line:
            try:
                line_data = json.loads(cleanJSON(lineup_obj.Line))
                l_player_ids = [
                    int(v) for k, v in line_data.items()
                    if k not in ['mod', 'captain', 'ot', 'penalties'] and str(v).isdigit()
                ]
                if l_player_ids:
                    field_players_with_vote = vote.Vote.objects.filter(
                        Player_id__in=l_player_ids,
                        Day=day,
                        Player__Role__in=['D', 'C', 'A']
                    ).exclude(
                        Q(Vote__isnull=True) | Q(Vote=0)
                    ).values('Player_id').distinct().count()
            except Exception as e:
                logger.error(f"Error parsing lineup: {e}")

        param2 = round(min(field_players_with_vote / 22.0, 1.0), 3)

        # -------------------------------------------------------------
        # PARAMETRO 3: Relative B11 Scaling nella Serie
        # -------------------------------------------------------------
        param3 = 1.0
        series_teams = team.Team.objects.filter(Series__in=_series).values_list('id', flat=True)
        series_b11_qs = b11_results.B11Results.objects.filter(
            Team_id__in=series_teams,
            Day=day
        ).values_list('B11Fp', flat=True)

        series_b11s = [float(score) for score in series_b11_qs if score is not None]

        if series_b11s:
            high_b11, low_b11 = max(series_b11s), min(series_b11s)
            if high_b11 > low_b11:
                param3 = round((b11_fp - low_b11) / (high_b11 - low_b11), 3)

        # -------------------------------------------------------------
        # PUNTEGGIO DI GIORNATA
        # -------------------------------------------------------------
        w1, w2, w3 = WEIGHTS
        day_pdo_score = round((param1 * w1) + (param2 * w2) + (param3 * w3), 3)
        # dday = min(day-1,35)
        dday_score = ( day_pdo_score / day )

        daily_score = {
            'day': day,
            'pts': dday_score, #day_pdo_score, CHECK WITH GIAMBA
            'param1': param1,
            'param2': param2,
            'param3': param3,
            'fp': fp,
            'b11_fp': b11_fp,
            'w11_fp': w11_fp,
            'field_votes': field_players_with_vote,  # <-- Numero giocatori con voto
            'b11_low': low_b11,                      # <-- Minimo B11 di giornata nella Serie
            'b11_high': high_b11,                    # <-- Massimo B11 di giornata nella Serie
        }


        # avg_score = round(total_pdo_pts / len(daily_scores), 3) if daily_scores else 0.0

        flat_data.append({
            'team_id': t.id,
            'team': t.Name,
            # 'pdoav': avg_score,
            # 'total_pts': round(total_pdo_pts, 3),
            # 'dday_score': dday_score,
            'daily_score': daily_score
        })

    # flat_data.sort(key=lambda x: x['pdoav'], reverse=True)
    return flat_data

def retrieve_pdoro_data(day=None):
    """
    Retrieves Panchina d'Oro data for a specific day
    """
    if day is None:
        day = int(get_current_day())

    teams = team.Team.objects.filter(
        Active=True,
    )

    results = pdoro.Pdoro.objects.filter(
        Day__lte=int(day),
        Season__Active=True,
        )

    ordered_results = []
    daily_scores = []
    for t in teams:
        team_results = results.filter(Team_id=t.id).order_by('Day')
        if team_results.exists():

            for t_result in team_results:
                daily_scores.append({
                    'day': t_result.Day,
                    'pts': t_result.Pts,
                    'param1': t_result.C1,
                    'param2': t_result.C2,
                    'param3': t_result.C3,
                    'w11_fp': t_result.w11,
                    'v22_fp': t_result.v22,
                    'b11_fp': t_result.b11,
                    'b11_low': t_result.b11_low,
                    'b11_high': t_result.b11_high,
                    'fp': t_result.Fp,
                })

            ordered_results.append({
                'team': t.Name,
                'total_pts': sum(score['pts'] for score in daily_scores),
                'daily_scores': daily_scores,})
        else:
            # If no result exists for the team, append a default entry
            ordered_results.append({
                'team': t.Name,
                'total_pts': 0.0,
                'daily_scores': [],
            })

    return ordered_results
