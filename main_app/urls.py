from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('accounts/signup/', views.signup, name='signup'),
    path('watchlists/', views.WatchlistIndex.as_view(), name='watchlist-index'),
    path('watchlists/<int:watchlist_id>/', views.WatchlistDetail.as_view(), name='watchlist-detail'),
    path('watchlists/create/', views.WatchlistCreate.as_view(), name='watchlist-create'),
    path('watchlists/<int:watchlist_id>/update/', views.WatchlistUpdate.as_view(), name='watchlist-update'),
    path('watchlists/<int:watchlist_id>/delete/', views.WatchlistDelete.as_view(), name='watchlist-delete'),
]
