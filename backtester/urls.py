from django.urls import path
from .views import load_forex_data, backtest_strategy,get_available_symbols # Ensure correct imports

urlpatterns = [
    path('fetch-data/', load_forex_data, name='load_forex_data'),  # Standardized naming
    path("get_symbols/", get_available_symbols, name="get_symbols"),
    path('backtest/', backtest_strategy, name='backtest'),
]
