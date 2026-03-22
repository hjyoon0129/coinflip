from django.urls import path
from .views import base_views

app_name = "main"

urlpatterns = [
    path("", base_views.coinflip_page, name="home"),
    path("subscribe/", base_views.subscribe, name="subscribe"),

    path("coinflip/", base_views.coinflip_page, name="coinflip"),

    path("api/coin/play/", base_views.api_can_play, name="api_coin_play"),
    path("api/consume-play/", base_views.api_consume_play, name="api_consume_play"),

    path("api/leaderboard/", base_views.api_leaderboard, name="api_leaderboard"),
    path(
        "api/leaderboard/weekly-best",
        base_views.api_leaderboard_weekly_best,
        name="api_leaderboard_weekly_best",
    ),
    path(
        "api/leaderboard/my-rank/",
        base_views.api_my_rank_weekly_best,
        name="api_my_rank_weekly_best",
    ),

    path("api/submit-score/", base_views.api_submit_score, name="api_submit_score"),

    path(
        "api/lemon/create-checkout-session/",
        base_views.api_create_checkout_session,
        name="lemon_create_checkout_session",
    ),
    path("lemon/webhook/", base_views.lemon_webhook, name="lemon_webhook"),

    path("api/adjust-capital/", base_views.api_adjust_capital, name="api_adjust_capital"),
]
