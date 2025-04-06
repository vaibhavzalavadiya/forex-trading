from django.urls import path
from .views import load_forex_data, backtest_strategy, get_available_symbols
from django.http import HttpResponse

def home(request):
    return HttpResponse("🎯 Forex Backtester API is Live!")

urlpatterns = [
    path('', home, name='home'),  # Home route
    path('fetch-data/', load_forex_data, name='load_forex_data'),
    path('get_symbols/', get_available_symbols, name='get_symbols'),
    path('backtest/', backtest_strategy, name='backtest'),
]
