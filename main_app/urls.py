from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('accounts/signup/', views.signup, name='signup'),
    path('watchlists/', views.WatchlistIndex.as_view(), name='watchlist-index'),
    path('watchlists/<int:pk>/', views.WatchlistDetail.as_view(), name='watchlist-detail'),
    path('watchlists/create/', views.WatchlistCreate.as_view(), name='watchlist-create'),
    path('watchlists/<int:pk>/update/', views.WatchlistUpdate.as_view(), name='watchlist-update'),
    path('watchlists/<int:pk>/delete/', views.WatchlistDelete.as_view(), name='watchlist-delete'),
    path('game-list/', views.game_list, name='game-list'),
    path('game-list/<int:game_id>/add-game/', views.add_game, name='add-game'),
    path('watchlists/<int:watchlist_id>/games/<int:game_id>/remove-game', views.remove_game, name='remove-game'),
    path('watchlists/<int:watchlist_id>/games/<int:game_id>/target-price', views.update_target_price, name='update-target-price'),
]
