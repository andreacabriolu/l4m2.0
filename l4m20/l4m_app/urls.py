from django.urls import path

from l4m_app.single_views import other_views

from .single_views import login_views, auction_views, lineup_views, squad_views, \
allauction_views, live_views, rules_views, dashboard_views, admin_views, my_leagues_views, \
statistics_views

app_name = "l4m"

urlpatterns = [
    path("", login_views.LoginView.as_view(), name="login"),
    path("accounts/login/", login_views.LoginView.as_view(), name="login"),
    path("login/", login_views.LoginView.as_view(), name="login"),
    path("logout/", login_views.LogoutView.as_view(), name="logout"),
    path("register/", login_views.RegisterView.as_view(), name="register"),
    path("l4m/auction/", auction_views.AuctionView.as_view(), name="auction"),
    path("l4m/auction/sendBet/", auction_views.SendBetView.as_view(), name="send_bet"),
    path("l4m/auction/finalizeBet/", auction_views.FinBetView.as_view(), name="finalize_bet"),
    path("l4m/auction/freePlayer/", auction_views.FreePlayerView.as_view(), name="free_player"),
    path("l4m/auction/getPlayerInfo/", auction_views.GetPlayerInfoView.as_view(), name="get_player_info"),
    path("l4m/auction/getBalance/", auction_views.GetBalanceView.as_view(), name="get_balance"),
    path("l4m/auction/getBalanceForBets/", auction_views.GetBalanceForBetsView.as_view(), name="get_balance_for_bets"),
    path("l4m/auction/signContract/", auction_views.SignContractView.as_view(), name="sign_contract"),
    path("l4m/auction/undoBet/", auction_views.UndoBetView.as_view(), name="undo_bet"),
    path("l4m/auction/quarantinePlayer/", auction_views.QuarantinePlayerView.as_view(), name="quarantine_player"),
    path("l4m/allauctions/", allauction_views.AllAuctionsView.as_view(), name="allauction"),
    path("l4m/allauctions/<int:series_id>/", allauction_views.AllAuctionsView.as_view(), name="allauction_series"),
    path("l4m/lineup_/", lineup_views.LineupView.as_view(), name="lineup_"),
    path("l4m/lineup/", lineup_views.LineupView_, name="lineup"),
    path("l4m/rules/", rules_views.RulesView.as_view(), name="rules"),
    path("l4m/squad/", squad_views.SquadView.as_view(), name="squad"),
    path("l4m/lineup/save/", lineup_views.SaveLineupView.as_view(), name="save_lineup"),
    path("l4m/lineup/saveMultiple/", lineup_views.SaveMultipleLineupView.as_view(), name="save_multiple_lineup"),
    path("l4m/lineup/getLast/", lineup_views.GetLastLineupView.as_view(), name="get_last_lineup"),
    path("l4m/live/<int:competition_id>/<int:series_id>/<int:day>/", live_views.LiveView, name="live"),
    path("l4m/live_default/", live_views.LiveDefaultView, name="live_default"),
    path("l4m/mylive/", live_views.MyLiveView.as_view(), name="mylive"),
    path("l4m/live_b11/", live_views.LiveB11View.as_view(), name="live_b11"),
    path("l4m/getLineupsByTeam/", live_views.GetLineupsByTeamView.as_view(), name="get_lineups_by_team"),
    path("l4m/", dashboard_views.DashboardView.as_view(), name="dashboard"),
    path("l4m/calculate/", admin_views.CalculateView.as_view(), name="calculate"),
    path("l4m/calculate/getCurrentDayByCompetition/", admin_views.GetCurrentDayByCompetition.as_view(), name="get_current_day"),
    path("l4m/calculate/calculateDay/", admin_views.CalculateDayView.as_view(), name="calculate_day"),
    path("l4m/calculate/setDay/", admin_views.SetDayView.as_view(), name="set_day"),
    path("l4m/retrieveRankingInfo/", dashboard_views.RetrieveRankingInfoView.as_view(), name="retrieve_ranking_info"),
    path("l4m/retrieveb11RankingInfo/", dashboard_views.RetrieveB11RankingInfoView.as_view(), name="retrieve_b11_ranking_info"),
    path("l4m/getSeriesByCompetition/", dashboard_views.GetSeriesByCompetitionView.as_view(), name="get_series_by_competition"),
    path("l4m/getTeamSeriesByCompetition/", dashboard_views.GetTeamSeriesByCompetitionView.as_view(), name="get_team_series_by_competition"),
    path("l4m/getDaysByCompetition/", dashboard_views.GetDaysByCompetitionView.as_view(), name="get_days_by_competition"),
    path("l4m/myleagues/<int:competition_id>/", my_leagues_views.MyLeaguesView.as_view(), name="my_leagues"),
    path("l4m/myleagues_no_match/<int:competition_id>/", my_leagues_views.MyLeaguesNoMatchView.as_view(), name="my_leagues_no_match"),
    path("l4m/retrieveCalendarInfo/", my_leagues_views.RetrieveCalendarInfoView.as_view(), name="retrieve_calendar_info"),
    path("l4m/calculate/getMissingLineups/", admin_views.GetMissingLineupsView.as_view(), name="get_missing_lineups"),
    path("l4m/get_live_ranking/", live_views.GetLiveRankingView.as_view(), name="get_live_ranking"),
    path("l4m/player_statistics/<int:player_id>/", statistics_views.StatisticsView.as_view(), name="player_statistics"),
    path("l4m/player_statistics/getBasicStats", statistics_views.GetBasicStatisticsView.as_view(), name="player_basic_statistics"),
    path("l4m/get_extratime/", live_views.GetExtraTimeView.as_view(), name="get_extratime"),
    path("l4m/get_penalties/", live_views.GetPenaltiesView.as_view(), name="get_penalties"),
    path("l4m/other/route66/", other_views.Route66View.as_view(), name="r66"),
    path("l4m/other/angel_butcher/", other_views.AngelButcherView.as_view(), name="angel_butcher"),
    path("l4m/showcase/", statistics_views.ShowcaseView.as_view(), name="showcase"),
    path("l4m/hall_of_fame/", statistics_views.HallOfFameView.as_view(), name="hall_of_fame"),
    path("l4m/heartbeat/", statistics_views.heartbeat, name="heartbeat")


]
