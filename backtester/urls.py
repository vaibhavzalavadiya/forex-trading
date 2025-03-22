from django.urls import path
from .views import fetch_forex_data, backtest_strategy

urlpatterns = [
    path('fetch_data/', fetch_forex_data, name='fetch_forex_data'),  # No extra "api/"
    path('backtest/', backtest_strategy, name='backtest'),  # No extra "api/"
]
