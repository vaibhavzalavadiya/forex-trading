import os
import pandas as pd
import numpy as np
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# Folder where CSV files are stored
DATA_FOLDER = os.path.join(settings.BASE_DIR, "data")
STARTING_CAPITAL = 100000
RISK_PER_TRADE = 0.02
MAX_TRADE_SIZE = 100000
loaded_data = {}

def get_available_symbols(request):
    """Fetch available symbols & timeframes from the 'data/' folder."""
    symbol_data = {}
    pattern = re.compile(r"([A-Z]+)(\d+MIN|\d+H|DAY)\.csv")

    if not os.path.exists(DATA_FOLDER):
        return JsonResponse({"error": "Data folder not found"}, status=404)

    for filename in os.listdir(DATA_FOLDER):
        match = pattern.match(filename)
        if match:
            symbol, timeframe = match.groups()
            symbol_data.setdefault(symbol, {})[timeframe] = filename

    return JsonResponse(symbol_data)

def load_forex_data(symbol, timeframe):
    """Loads forex data from a CSV file and ensures correct headers."""
    if symbol in loaded_data and timeframe in loaded_data[symbol]:
        return loaded_data[symbol][timeframe]

    filename = f"{symbol}{timeframe}.csv"
    filepath = os.path.join(DATA_FOLDER, filename)

    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return None

    try:
        # Read CSV with explicit tab separator
        df = pd.read_csv(filepath, sep="\t", names=["timestamp", "open", "high", "low", "close", "volume"])

        # Ensure numeric columns are correctly parsed
        numeric_columns = ["open", "high", "low", "close", "volume"]
        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce")
        df.dropna(inplace=True)

        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df.dropna(subset=["timestamp"], inplace=True)
        df.sort_values(by="timestamp", inplace=True)

        if df.empty:
            print(f"⚠️ CSV {filename} is empty or has invalid data!")
            return None

        df["EMA"] = df["close"].ewm(span=5, adjust=False).mean()
        df.dropna(subset=["EMA"], inplace=True)

        loaded_data.setdefault(symbol, {})[timeframe] = df
        return df

    except Exception as e:
        print(f"❌ Error loading file {filepath}: {e}")
        return None

@csrf_exempt
def backtest_strategy(request):
    """Backtesting function with wick-to-body ratio check for stronger signals."""
    try:
        symbol = request.GET.get("symbol", "").upper()
        timeframe = request.GET.get("timeframe", "").upper()
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 20))

        print(f"📡 Received Request: symbol={symbol}, timeframe={timeframe}, page={page}, limit={limit}")

        if not symbol or not timeframe:
            return JsonResponse({"error": "Symbol and timeframe are required"}, status=400)

        filename = f"{symbol}{timeframe}.csv"
        filepath = os.path.join(DATA_FOLDER, filename)

        if not os.path.exists(filepath):
            return JsonResponse({"error": f"Invalid symbol or timeframe: {symbol}, {timeframe}"}, status=400)

        df = load_forex_data(symbol, timeframe)
        if df is None or df.empty:
            return JsonResponse({"error": "Data unavailable."}, status=400)

        all_signals = []
        capital = STARTING_CAPITAL

        for i in range(1, len(df) - 1):
            prev, curr, nxt = df.iloc[i - 1], df.iloc[i], df.iloc[i + 1]

            if np.isnan(prev["EMA"]):
                continue

            trade_type, entry_price, stop_loss, target, profit = None, None, None, None, None

            # Calculate wick and body size
            upper_wick = prev["high"] - max(prev["open"], prev["close"])
            lower_wick = min(prev["open"], prev["close"]) - prev["low"]
            body_size = abs(prev["open"] - prev["close"])

            # SELL SIGNAL - Candle fully above EMA, upper wick larger than body, next candle red
            if prev["close"] > prev["EMA"] and prev["open"] > prev["EMA"] and prev["low"] > prev["EMA"]:
                if upper_wick > body_size and nxt["close"] < nxt["open"]:  # Long wick & next red candle
                    trade_type = "SELL"
                    entry_price = nxt["open"]
                    stop_loss = entry_price * 1.01  # 1% Stop Loss
                    target = entry_price * 0.97  # 3% Target
                    profit = entry_price - target

            # BUY SIGNAL - Candle fully below EMA, lower wick larger than body, next candle green
            elif prev["close"] < prev["EMA"] and prev["open"] < prev["EMA"] and prev["high"] < prev["EMA"]:
                if lower_wick > body_size and nxt["close"] > nxt["open"]:  # Long wick & next green candle
                    trade_type = "BUY"
                    entry_price = nxt["open"]
                    stop_loss = entry_price * 0.99  # 1% Stop Loss
                    target = entry_price * 1.03  # 3% Target
                    profit = target - entry_price

            if trade_type:
                risk = abs(stop_loss - entry_price)
                if risk == 0:
                    continue

                risk_amount = capital * RISK_PER_TRADE
                trade_size = np.clip(risk_amount / risk, 1, MAX_TRADE_SIZE)
                trade_profit = trade_size * profit
                capital = max(capital + trade_profit, 0)

                all_signals.append({
                    "timestamp": nxt["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                    "type": trade_type,
                    "entry_price": round(entry_price, 5),
                    "stop_loss": round(stop_loss, 5),
                    "target": round(target, 5),
                    "profit_loss": round(trade_profit, 5),
                    "capital": round(capital, 2)
                })

        total_signals = len(all_signals)
        total_pages = (total_signals // limit) + (1 if total_signals % limit else 0)
        start_index = (page - 1) * limit
        end_index = min(start_index + limit, total_signals)
        paginated_signals = all_signals[start_index:end_index]

        return JsonResponse({
            "summary": {
                "total_profit_loss": round(sum(s["profit_loss"] for s in all_signals), 5),
                "final_capital": round(all_signals[-1]["capital"], 2) if all_signals else STARTING_CAPITAL,
                "total_signals": total_signals,
                "current_page": page,
                "total_pages": total_pages, 
            },
            "signals": paginated_signals
        })
    except Exception as e:
        print(f"❌ Server error: {e}") 
        return JsonResponse({"error": f"Server error: {e}"}, status=500)
