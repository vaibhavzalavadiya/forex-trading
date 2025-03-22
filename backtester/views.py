import requests
import numpy as np
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from .models import ForexData

# Replace with your actual Twelve Data API Key
API_KEY = '05767e9cf5f44b6aa42ad342d4955fc8'
BASE_URL = 'https://api.twelvedata.com/time_series'

# Define all valid Forex pairs
VALID_PAIRS = {"EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "XAUUSD"}

# Starting capital for backtesting
STARTING_CAPITAL = 100000
RISK_PER_TRADE = 0.02  # 2% of capital per trade


@csrf_exempt
def fetch_forex_data(request):
    """Fetches Forex data for all valid pairs and stores new records in the database."""
    interval = request.GET.get('interval', '5min')
    total_fetched = 0

    for pair in VALID_PAIRS:
        params = {
            'symbol': pair,
            'interval': interval,
            'apikey': API_KEY,
            'outputsize': '100'
        }

        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            return JsonResponse({"error": f"API request failed for {pair}", "details": str(e)}, status=500)

        if "values" not in data or not data["values"]:
            continue  # Skip if no data found

        # Store only new records
        existing_timestamps = set(ForexData.objects.filter(currency_pair=pair).values_list('timestamp', flat=True))
        records = [
            ForexData(
                currency_pair=pair,
                timestamp=parse_datetime(entry["datetime"]),
                open_price=float(entry["open"]),
                high_price=float(entry["high"]),
                low_price=float(entry["low"]),
                close_price=float(entry["close"]),
                volume=float(entry.get("volume", 0))
            )
            for entry in data["values"]
            if parse_datetime(entry["datetime"]) not in existing_timestamps
        ]

        if records:
            ForexData.objects.bulk_create(records)
            total_fetched += len(records)

    return JsonResponse({"message": f"Fetched {total_fetched} new records across all pairs."})


@csrf_exempt
def backtest_strategy(request):
    """Backtests the 5 EMA strategy on all stored Forex data for all available pairs."""
    all_pairs = ForexData.objects.values_list("currency_pair", flat=True).distinct()
    all_signals = []
    capital = STARTING_CAPITAL  # Start with $100,000
    total_profit_loss = 0.0

    if not all_pairs:
        return JsonResponse({"error": "No forex data available in the database."}, status=404)

    for pair in all_pairs:
        forex_data = ForexData.objects.filter(currency_pair=pair).order_by("timestamp")
        if not forex_data.exists():
            continue  # Skip if no data found for this pair

        df = pd.DataFrame(list(forex_data.values()))
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.sort_values(by='timestamp', inplace=True)

        # Compute 5 EMA
        df['EMA'] = df['close_price'].ewm(span=5, adjust=False).mean()

        pair_signals = []
        pair_profit_loss = 0.0

        for i in range(1, len(df) - 1):
            prev, curr, nxt = df.iloc[i - 1], df.iloc[i], df.iloc[i + 1]
            if np.isnan(prev['EMA']):
                continue  # Skip if EMA not yet calculated

            trade_type = None
            entry_price = None
            stop_loss = None
            target = None
            profit = None

            # Buy Entry Condition
            if prev['low_price'] > prev['EMA'] and nxt['close_price'] > nxt['open_price']:
                trade_type = "BUY"
                entry_price = nxt['open_price']
                stop_loss = entry_price * 0.95
                target = entry_price * 1.15
                profit = target - entry_price

            # Sell Entry Condition
            elif prev['high_price'] < prev['EMA'] and nxt['close_price'] < nxt['open_price']:
                trade_type = "SELL"
                entry_price = nxt['open_price']
                stop_loss = entry_price * 1.05
                target = entry_price * 0.85
                profit = entry_price - target

            if trade_type:
                risk = abs(stop_loss - entry_price)
                risk_reward = round(profit / risk, 2) if risk != 0 else None
                risk_amount = capital * RISK_PER_TRADE  # 2% of capital risked per trade
                trade_size = risk_amount / risk if risk != 0 else 0
                trade_profit = trade_size * profit if trade_size != 0 else 0

                capital += trade_profit  # Update capital based on profit/loss
                pair_profit_loss += trade_profit

                pair_signals.append({
                    "pair": pair,
                    "type": trade_type,
                    "timestamp": nxt['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
                    "entry_price": round(entry_price, 5),
                    "target": round(target, 5),
                    "stop_loss": round(stop_loss, 5),
                    "profit_loss": round(trade_profit, 5),
                    "risk_reward": risk_reward,
                    "capital": round(capital, 2)
                })

        total_profit_loss += pair_profit_loss
        all_signals.append({
            "pair": pair,
            "total_trades": len(pair_signals),
            "total_profit_loss": round(pair_profit_loss, 5),
            "signals": pair_signals
        })

    return JsonResponse({
        "summary": {"total_profit_loss": round(total_profit_loss, 5), "final_capital": round(capital, 2)},
        "details": all_signals
    })
