from django.urls import path

from .single_views import login_views, auction_views, lineup_views

app_name = "l4m"

urlpatterns = [
    path("", login_views.LoginView.as_view(), name="login"),
    path("login/", login_views.LoginView.as_view(), name="login"),
    path("logout/", login_views.LogoutView.as_view(), name="logout"),
    path("register/", login_views.RegisterView.as_view(), name="register"),
    path("l4m/", auction_views.AuctionView.as_view(), name="auction"),
    path("l4m/auction/sendBet/", auction_views.SendBetView.as_view(), name="send_bet"),
    path("l4m/auction/finalizeBet/", auction_views.FinBetView.as_view(), name="finalize_bet"),
    path("l4m/auction/getPlayerInfo/", auction_views.GetPlayerInfoView.as_view(), name="get_player_info"),
    path("l4m/auction/getBalance/", auction_views.GetBalanceView.as_view(), name="get_balance"),
    path("l4m/auction/getBalanceForBets/", auction_views.GetBalanceForBetsView.as_view(), name="get_balance_for_bets"),
    path("l4m/allauctions/", auction_views.AllAuctionsView.as_view(), name="allauction"),
    path("l4m/lineup/", lineup_views.LineupView.as_view(), name="lineup"),
    path("l4m/lineup/save/", lineup_views.SaveLineupView.as_view(), name="save_lineup"),
    path("l4m/lineup/getLast/", lineup_views.GetLastLineupView.as_view(), name="get_last_lineup"),

]
