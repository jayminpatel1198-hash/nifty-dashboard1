from flask import Flask
import requests
import os
from datetime import datetime

app = Flask(__name__)

ACCESS_TOKEN = os.environ.get("UPSTOX_TOKEN")

stocks = {
    "RELIANCE":"NSE_EQ|INE002A01018",
    "HDFCBANK":"NSE_EQ|INE040A01034",
    "BHARTIARTL":"NSE_EQ|INE397D01024",
    "SBIN":"NSE_EQ|INE062A01020",
    "ICICIBANK":"NSE_EQ|INE090A01021",
    "TCS":"NSE_EQ|INE467B01029",
    "BAJFINANCE":"NSE_EQ|INE296A01032",
    "LT":"NSE_EQ|INE018A01030",
    "INFY":"NSE_EQ|INE009A01021",
    "HINDUNILVR":"NSE_EQ|INE030A01027",
    "SUNPHARMA":"NSE_EQ|INE044A01036",
    "ADANIPORTS":"NSE_EQ|INE742F01042",
    "MARUTI":"NSE_EQ|INE585B01010",
    "AXISBANK":"NSE_EQ|INE238A01034",
    "ADANIENT":"NSE_EQ|INE423A01024",
    "KOTAKBANK":"NSE_EQ|INE237A01036",
    "M&M":"NSE_EQ|INE101A01026",
    "TITAN":"NSE_EQ|INE280A01028",
    "NTPC":"NSE_EQ|INE733E01010",
    "ITC":"NSE_EQ|INE154A01025",
    "ONGC":"NSE_EQ|INE213A01029",
    "ULTRACEMCO":"NSE_EQ|INE481G01011",
    "JSWSTEEL":"NSE_EQ|INE019A01038",
    "HCLTECH":"NSE_EQ|INE860A01027",
    "BEL":"NSE_EQ|INE263A01024",
    "COALINDIA":"NSE_EQ|INE522F01014",
    "BAJAJ-AUTO":"NSE_EQ|INE917I01010",
    "BAJAJFINSV":"NSE_EQ|INE918I01026",
    "POWERGRID":"NSE_EQ|INE752E01010",
    "TATASTEEL":"NSE_EQ|INE081A01020",
    "HINDALCO":"NSE_EQ|INE038A01020",
    "ASIANPAINT":"NSE_EQ|INE021A01026",
    "ETERNAL":"NSE_EQ|INE758T01015",
    "SHRIRAMFIN":"NSE_EQ|INE721A01047",
    "WIPRO":"NSE_EQ|INE075A01022",
    "GRASIM":"NSE_EQ|INE047A01021",
    "EICHERMOT":"NSE_EQ|INE066A01021",
    "SBILIFE":"NSE_EQ|INE123W01016",
    "JIOFIN":"NSE_EQ|INE758E01017",
    "TRENT":"NSE_EQ|INE849A01020",
    "HDFCLIFE":"NSE_EQ|INE795G01014",
    "APOLLOHOSP":"NSE_EQ|INE437A01024",
    "TATACONSUM":"NSE_EQ|INE192A01025",
    "CIPLA":"NSE_EQ|INE059A01026",
    "NESTLEIND":"NSE_EQ|INE239A01024",
    "DRREDDY":"NSE_EQ|INE089A01031",
    "TECHM":"NSE_EQ|INE669C01036",
    "INDUSINDBK":"NSE_EQ|INE095A01012",
    "HEROMOTOCO":"NSE_EQ|INE158A01026"
}

weights = {
    "RELIANCE":9.47, "HDFCBANK":6.19, "BHARTIARTL":5.93, "SBIN":4.78,
    "ICICIBANK":4.75, "TCS":4.32, "BAJFINANCE":2.91, "LT":2.90,
    "INFY":2.64, "HINDUNILVR":2.62, "SUNPHARMA":2.29, "ADANIPORTS":2.21,
    "MARUTI":2.19, "AXISBANK":2.08, "ADANIENT":2.03, "KOTAKBANK":2.02,
    "M&M":2.00, "TITAN":1.93, "NTPC":1.90, "ITC":1.85,
    "ONGC":1.80, "ULTRACEMCO":1.74, "JSWSTEEL":1.71, "HCLTECH":1.70,
    "BEL":1.58, "COALINDIA":1.55, "BAJAJ-AUTO":1.53, "BAJAJFINSV":1.48,
    "POWERGRID":1.41, "TATASTEEL":1.41, "HINDALCO":1.36, "ASIANPAINT":1.36,
    "ETERNAL":1.27, "SHRIRAMFIN":1.14, "WIPRO":1.14, "GRASIM":1.13,
    "EICHERMOT":1.04, "SBILIFE":0.95, "JIOFIN":0.83, "TRENT":0.81,
    "HDFCLIFE":0.66, "APOLLOHOSP":0.63, "TATACONSUM":0.60, "CIPLA":0.59,
    "NESTLEIND":0.76, "DRREDDY":0.64
}
@app.route("/")
def home():
    if not ACCESS_TOKEN:
        return "<h2>UPSTOX_TOKEN not found in Render Environment Variables</h2>"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    nifty_url = "https://api.upstox.com/v2/market-quote/ltp?instrument_key=NSE_INDEX|Nifty%2050"
    nifty_value = "NA"

    try:
        nifty_data = requests.get(nifty_url, headers=headers, timeout=10).json()
        nifty_value = nifty_data["data"]["NSE_INDEX:Nifty 50"]["last_price"]
    except Exception:
        nifty_value = "Error"

    instrument_keys = ",".join(stocks.values())
    quote_url = f"https://api.upstox.com/v2/market-quote/quotes?instrument_key={instrument_keys}"

    try:
        q = requests.get(quote_url, headers=headers, timeout=15).json()
        data = q["data"]
    except Exception as e:
        return f"<h2>Upstox API Error</h2><p>{str(e)}</p>"

    green = 0
    red = 0
    flat = 0
    weighted_score = 0
    rows = []

    for item in data.values():
        symbol = item.get("symbol")
        last_price = item.get("last_price", 0)
        close = item.get("ohlc", {}).get("close", 0)
        net_change = item.get("net_change", 0)

        if close:
            pct = round((net_change / close) * 100, 2)
        else:
            pct = 0

        if net_change > 0:
            green += 1
            direction = "GREEN"
            weighted_score += weights.get(symbol, 0)
        elif net_change < 0:
            red += 1
            direction = "RED"
            weighted_score -= weights.get(symbol, 0)
        else:
            flat += 1
            direction = "FLAT"

        rows.append({
            "symbol": symbol,
            "price": last_price,
            "change": net_change,
            "pct": pct,
            "direction": direction,
            "weight": weights.get(symbol, 0)
        })

    total = green + red + flat
    green_pct = round((green / total) * 100, 1) if total else 0
    red_pct = round((red / total) * 100, 1) if total else 0
    adv_dec = round(green / red, 2) if red else green

    bull_score = round(50 + weighted_score, 1)
    if bull_score > 100:
        bull_score = 100
    if bull_score < 0:
        bull_score = 0

    call_bias = bull_score
put_bias = round(100 - bull_score, 1)

if green_pct >= 65 and bull_score >= 75:
    market_mode = "TRENDING BULLISH"
    signal = "STRONG CALL BUY BIAS"
    signal_class = "bull"
    strength = "STRONG"
    risk = "LOW"
elif red_pct >= 65 and bull_score <= 25:
    market_mode = "TRENDING BEARISH"
    signal = "STRONG PUT BUY BIAS"
    signal_class = "bear"
    strength = "STRONG"
    risk = "LOW"
elif 45 <= green_pct <= 55:
    market_mode = "CHOPPY / SIDEWAYS"
    signal = "NO TRADE - OPTION BUYING AVOID"
    signal_class = "neutral"
    strength = "WEAK"
    risk = "HIGH"
elif bull_score >= 60:
    market_mode = "MILD BULLISH"
    signal = "CALL SIDE BIAS - WAIT FOR BREAKOUT"
    signal_class = "bull"
    strength = "MEDIUM"
    risk = "MEDIUM"
elif bull_score <= 40:
    market_mode = "MILD BEARISH"
    signal = "PUT SIDE BIAS - WAIT FOR BREAKDOWN"
    signal_class = "bear"
    strength = "MEDIUM"
    risk = "MEDIUM"
else:
    market_mode = "SIDEWAYS"
    signal = "NO TRADE"
    signal_class = "neutral"
    strength = "WEAK"
    risk = "HIGH"

    gainers = sorted(rows, key=lambda x: x["pct"], reverse=True)[:5]
    losers = sorted(rows, key=lambda x: x["pct"])[:5]

    def make_table(items):
        html = ""
        for r in items:
            cls = "green" if r["pct"] > 0 else "red"
            html += f"<tr><td>{r['symbol']}</td><td>{r['price']}</td><td class='{cls}'>{r['pct']}%</td></tr>"
        return html

    time_now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    return f"""
    <html>
    <head>
        <title>Nifty Option Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta http-equiv="refresh" content="5">
        <style>
            body {{ font-family: Arial; background:#f4f6f8; margin:0; padding:14px; }}
            h2 {{ text-align:center; }}
            .grid {{ display:grid; grid-template-columns: repeat(2, 1fr); gap:10px; }}
            .card {{ background:white; padding:15px; border-radius:12px; box-shadow:0 2px 6px #ddd; }}
            .big {{ font-size:26px; font-weight:bold; }}
            .green {{ color:#0a9f45; font-weight:bold; }}
            .red {{ color:#d93025; font-weight:bold; }}
            .bull {{ background:#d9fbe6; color:#078b3e; }}
            .bear {{ background:#ffe1e1; color:#b00020; }}
            .neutral {{ background:#fff3cd; color:#8a6d00; }}
            .signal {{ padding:18px; border-radius:14px; text-align:center; font-size:24px; font-weight:bold; margin:12px 0; }}
            table {{ width:100%; border-collapse:collapse; }}
            td, th {{ padding:8px; border-bottom:1px solid #eee; text-align:left; }}
            .full {{ grid-column:1 / 3; }}
            small {{ color:#666; }}
        </style>
    </head>
    <body>
        <h2>NIFTY OPTION DASHBOARD</h2>
        <div class="signal {signal_class}">{signal}</div>

        <div class="grid">
            <div class="card"><div>Nifty 50</div><div class="big">{nifty_value}</div></div>
            <div class="card"><div>Bull Score</div><div class="big">{bull_score}/100</div></div>
            <div class="card"><div>Green</div><div class="big green">{green} ({green_pct}%)</div></div>
            <div class="card"><div>Red</div><div class="big red">{red} ({red_pct}%)</div></div>
            <div class="card"><div>Advance / Decline</div><div class="big">{adv_dec}</div></div>
            <div class="card"><div>Weight Score</div><div class="big">{round(weighted_score,2)}</div></div>
            <div class="card"><div>Call Bias</div><div class="big green">{call_bias}/100</div></div>
<div class="card"><div>Put Bias</div><div class="big red">{put_bias}/100</div></div>
<div class="card"><div>Market Mode</div><div class="big">{market_mode}</div></div>
<div class="card"><div>Signal Strength</div><div class="big">{strength}</div></div>
<div class="card"><div>Risk</div><div class="big">{risk}</div></div>
            <div class="card full">
                <h3>Top 5 Gainers</h3>
                <table><tr><th>Stock</th><th>Price</th><th>%</th></tr>{make_table(gainers)}</table>
            </div>

            <div class="card full">
                <h3>Top 5 Losers</h3>
                <table><tr><th>Stock</th><th>Price</th><th>%</th></tr>{make_table(losers)}</table>
            </div>
        </div>

        <p style="text-align:center;"><small>Auto refresh every 5 sec | Last update: {time_now}</small></p>
    </body>
    </html>
    """
