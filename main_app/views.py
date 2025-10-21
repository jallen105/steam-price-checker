from django.shortcuts import render, redirect
from asgiref.sync import sync_to_async
import httpx
import logging
from .models import Game, Watchlist, PriceCheck
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.http import HttpResponse 

logger = logging.getLogger(__name__)
STEAM_SEARCH = 'https://steamcommunity.com/actions/SearchApps/'
STEAM_STORE_SEARCH = 'https://store.steampowered.com/api/storesearch/'
STEAM_GET_APP_DETAIL = 'https://store.steampowered.com/api/appdetails?appids='
# Create your views here.

def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'signup.html', context)

async def game_list(request):
    query = request.GET.get('query')
    search_data = None
    if query:
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                resp = await client.get(f'{STEAM_STORE_SEARCH}?term={query}&l=english&cc=NA')
                resp.raise_for_status()
                search_data = resp.json()
            except httpx.HTTPError:
                logger.exception('Async Steam lookup failed for %s', query)
                search_data = {'error': 'Could not fetch search data at this time.'}
    return await sync_render(request, 'game_list.html', {'search_data': search_data})

class Home(LoginView):
    template_name = 'home.html'

class WatchlistCreate(LoginRequiredMixin, CreateView):
    model = Watchlist
    fields = ['name']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
class WatchlistUpdate(LoginRequiredMixin, UpdateView):
    model = Watchlist
    fields = ['name']

class WatchlistIndex(LoginRequiredMixin, ListView):
    model = Watchlist

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_watchlists'] = Watchlist.objects.filter(user = self.request.user)
        return context

class WatchlistDetail(LoginRequiredMixin, DetailView):
    model = Watchlist

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['games'] = Watchlist.objects.get(id=self.kwargs['pk']).games.all
        context['target_price'] = PriceCheck.objects.filter(watchlist_id=self.kwargs['pk'])
        return context

class WatchlistDelete(LoginRequiredMixin, DeleteView):
    model = Watchlist
    success_url = '/watchlists/'

@sync_to_async
def sync_render(request, template_name, context):
    '''passes the async view into a sync view. This is to prevent the async to sync errors'''
    context['watchlists'] = Watchlist.objects.filter(user = request.user)
    return render(request, template_name, context)

@sync_to_async
def sync_redirect_add(game_data, template_name, watchlist_id):
    game_appid = game_data['steam_appid']
    game_name = game_data['name']
    game_img = game_data['capsule_image']

    if not game_data['is_free']:
        game_price = game_data['price_overview']['final']
    else:
        game_price = 0

    if Game.objects.filter(appid=game_appid):
        game = Game.objects.get(appid=game_appid)
    else:
        game = Game.objects.create(appid = game_appid, name = game_name, thumb_nail = game_img, price = game_price)
    
    Watchlist.objects.get(id=watchlist_id).games.add(game.id)

    return redirect(template_name)

async def fetch_game_data(game_id):
    game_data = None
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(f'{STEAM_GET_APP_DETAIL}{game_id}')
            resp.raise_for_status()
            game_data = resp.json()
        except httpx.HTTPError:
            logger.exception('Async Steam lookup failed for %s', game_id)
            game_data = {'error': 'Could not fetch game data at this time.'}
    return game_data[f"{game_id}"]["data"]

@login_required
async def add_game(request, game_id):
    watchlist_id = request.POST.get('watchlist')
    game_data = await fetch_game_data(game_id)
    if watchlist_id:
        return await sync_redirect_add(game_data, 'game-list', watchlist_id)
    else:
        return redirect('game-list')

@login_required
def remove_game(request, watchlist_id, game_id):
    Watchlist.objects.get(id=watchlist_id).games.remove(game_id)
    return redirect('watchlist-detail', pk=watchlist_id)

@login_required
def update_target_price(request, watchlist_id, game_id):
    target_price = request.POST.get('price')
    update_price = PriceCheck.objects.get(watchlist_id=watchlist_id, game_id=game_id)
    update_price.target_price = target_price
    update_price.save()

    return redirect('watchlist-detail', pk=watchlist_id)

async def check_prices(request):
    async for game in Game.objects.all():
        game_data = await fetch_game_data(game.appid)
        if game_data['is_free']:
            continue
        elif not game_data['price_overview']['final'] == game.price:
            game.price = game_data['price_overview']['final']
            game.save()
    return redirect('home')