from django.urls import path

from . import views

app_name = "l4m"

urlpatterns = [
    path("", views.LoginView.as_view(), name="login"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("l4m/", views.IndexView.as_view(), name="index"),

]
