from django.urls import path

from .single_views import login_views, auction_views, lineup_views, squad_views, allauction_views, live_views, rules_views, dashboard_views, admin_views

app_name = "l4m"

urlpatterns = [
    path("", login_views.LoginView.as_view(), name="login"),
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
    path("l4m/allauctions/", allauction_views.AllAuctionsView.as_view(), name="allauction"),
    path("l4m/allauctions/<int:series_id>/", allauction_views.AllAuctionsView.as_view(), name="allauction_series"),
    path("l4m/lineup/", lineup_views.LineupView.as_view(), name="lineup"),
    path("l4m/rules/", rules_views.RulesView.as_view(), name="rules"),
    path("l4m/squad/", squad_views.SquadView.as_view(), name="squad"),
    path("l4m/lineup/save/", lineup_views.SaveLineupView.as_view(), name="save_lineup"),
    path("l4m/lineup/getLast/", lineup_views.GetLastLineupView.as_view(), name="get_last_lineup"),
    path("l4m/live/", live_views.LiveView, name="live"),
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

]
