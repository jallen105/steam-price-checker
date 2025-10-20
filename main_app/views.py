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

logger = logging.getLogger(__name__)
STEAM_SEARCH = 'https://steamcommunity.com/actions/SearchApps/'

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

class WatchlistDelete(LoginRequiredMixin, DeleteView):
    model = Watchlist
    success_url = '/watchlists/'

@sync_to_async
def sync_render(request, template_name, context):
    '''passes the async view into a sync view. This is to prevent the async to sync errors'''
    return render(request, template_name, context)

async def game_list(request):
    query = request.GET.get('query')
    search_data = None
    if query:
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                resp = await client.get(f'{STEAM_SEARCH}{query}')
                resp.raise_for_status()
                search_data = resp.json()
            except httpx.HTTPError:
                logger.exception('Async Steam lookup failed for %s', query)
                search_data = {'error': 'Could not fetch search data at this time.'}
    return await sync_render(request, 'game_list.html', {'search_data': search_data})
