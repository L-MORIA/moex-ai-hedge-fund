import json

# Simplified approach - parse the raw JSON directly from the input
def clean_json_text(text):
    # Find the start and end of JSON objects in the text
    import re
    
    # Extract the first complete JSON object (starting with { and ending with })
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1:
        raise ValueError("Could not find JSON object")
    
    json_str = text[start:end+1]
    return json_str

# The complete raw data from the message
raw_data = """
{
  "meta": {
    "collected_at": "2026-07-08T20:26:34.673428",
    "tickers": [
      "SBER",
      "GAZP",
      "LKOH",
      "SBERP",
      "VTBR"
    ],
    "source": "MOEX ISS + RSS feeds"
  },
  "portfolio": "Portfolio summary (5 tickers)\n  Ticker        Price        Chg     Chg%          Vol\n  ----------------------------------------------------\n  SBER         298.29      -0.69   -0.23%   40,323,880\n  GAZP          95.23      +0.97   +1.02%   60,776,100\n  LKOH        4508.50    +132.50   +2.94%    1,823,816\n  SBERP        299.25      +0.03   +0.01%    3,228,835\n  VTBR          64.98      -0.07   -0.11%   93,017,370\n  ----------------------------------------------------\n  Total volume: 199,170,001 shares",
  "candles": {
    "SBER": [
      {"begin": "2026-06-24 00:00:00", "end": "2026-06-24 23:59:59", "open": 307.31, "high": 310.33, "low": 298, "close": 301.92, "volume": 55513803},
      {"begin": "2026-06-25 00:00:00", "end": "2026-06-25 23:59:59", "open": 302.47, "high": 305.8, "low": 294.2, "close": 295.16, "volume": 76647625},
      {"begin": "2026-06-26 00:00:00", "end": "2026-06-26 23:59:57", "open": 296, "high": 303.9, "low": 290.35, "close": 299.18, "volume": 85683639},
      {"begin": "2026-06-27 00:00:00", "end": "2026-06-27 23:59:57", "open": 299.5, "high": 301.36, "low": 299.18, "close": 299.69, "volume": 2907428},
      {"begin": "2026-06-28 00:00:00", "end": "2026-06-28 23:59:59", "open": 299.7, "high": 300.47, "low": 298.61, "close": 299.97, "volume": 2824723},
      {"begin": "2026-06-29 00:00:00", "end": "2026-06-29 23:59:59", "open": 300, "high": 308.55, "low": 296.02, "close": 307.9, "volume": 55268988},
      {"begin": "2026-06-30 00:00:00", "end": "2026-06-30 23:59:59", "open": 307.9, "high": 312.65, "low": 305.7, "close": 308.09, "volume": 44933411},
      {"begin": "2026-07-01 00:00:00", "end": "2026-07-01 23:59:53", "open": 308.12, "high": 311.57, "low": 305.55, "close": 307.04, "volume": 40780087},
      {"begin": "2026-07-02 00:00:00", "end": "2026-07-02 23:59:55", "open": 307.1, "high": 308.2, "low": 299.83, "close": 301.05, "volume": 45930395},
      {"begin": "2026-07-03 00:00:00", "end": "2026-07-03 23:59:59", "open": 301.65, "high": 303.25, "low": 298.04, "close": 301.19, "volume": 33006616},
      {"begin": "2026-07-04 00:00:00", "end": "2026-07-04 23:59:59", "open": 301.39, "high": 301.69, "low": 300.28, "close": 300.76, "volume": 1357409},
      {"begin": "2026-07-05 00:00:00", "end": "2026-07-05 23:59:56", "open": 304.42, "high": 304.42, "low": 302.01, "close": 303.34, "volume": 2735540},
      {"begin": "2026-07-06 00:00:00", "end": "2026-07-06 23:59:55", "open": 303.47, "high": 305.6, "low": 294.07, "close": 298.77, "volume": 46121572},
      {"begin": "2026-07-07 00:00:00", "end": "2026-07-07 23:59:51", "open": 299.02, "high": 299.47, "low": 292.12, "close": 298.98, "volume": 49403734},
      {"begin": "2026-07-08 00:00:00", "end": "2026-07-08 20:26:29", "open": 299.38, "high": 301.18, "low": 293.8, "close": 297.93, "volume": 40442403}
    ],
    "GAZP": [
      {"begin": "2026-06-24 00:00:00", "end": "2026-06-24 23:59:59", "open": 102, "high": 102.41, "low": 97.13, "close": 98.02, "volume": 98523170},
      {"begin": "2026-06-25 00:00:00", "end": "2026-06-25 23:59:59", "open": 98.48, "high": 99.72, "low": 97.3, "close": 98.07, "volume": 78716230},
      {"begin": "2026-06-26 00:00:00", "end": "2026-06-26 23:59:57", "open": 98.07, "high": 101.12, "low": 95.65, "close": 99.07, "volume": 112721030},
      {"begin": "2026-06-27 00:00:00", "end": "2026-06-27 23:59:57", "open": 99.28, "high": 99.66, "low": 99.1, "close": 99.28, "volume": 2100900},
      {"begin": "2026-06-28 00:00:00", "end": "2026-06-28 23:59:59", "open": 99.39, "high": 99.68, "low": 99.08, "close": 99.22, "volume": 3023750},
      {"begin": "2026-06-29 00:00:00", "end": "2026-06-29 23:59:59", "open": 99.59, "high": 102.69, "low": 97.8, "close": 101.98, "volume": 64026390},
      {"begin": "2026-06-30 00:00:00", "end": "2026-06-30 23:59:59", "open": 101.98, "high": 103.59, "low": 100.32, "close": 100.9, "volume": 59912800},
      {"begin": "2026-07-01 00:00:00", "end": "2026-07-01 23:59:53", "open": 100.9, "high": 102.53, "low": 99.93, "close": 101.03, "volume": 30413950},
      {"begin": "2026-07-02 00:00:00", "end": "2026-07-02 23:59:55", "open": 100.91, "high": 101.64, "low": 96.55, "close": 97.05, "volume": 58826190},
      {"begin": "2026-07-03 00:00:00", "end": "2026-07-03 23:59:59", "open": 97.2, "high": 98.5, "low": 96.07, "close": 96.84, "volume": 51279690},
      {"begin": "2026-07-04 00:00:00", "end": "2026-07-04 23:59:59", "open": 96.94, "high": 97.8, "low": 96.64, "close": 96.91, "volume": 1882320},
      {"begin": "2026-07-05 00:00:00", "end": "2026-07-05 23:59:56", "open": 98.7, "high": 98.9, "low": 97.33, "close": 97.84, "volume": 4938010},
      {"begin": "2026-07-06 00:00:00", "end": "2026-07-06 23:59:55", "open": 98, "high": 98.12, "low": 94.69, "close": 94.81, "volume": 59511620},
      {"begin": "2026-07-07 00:00:00", "end": "2026-07-07 23:59:51", "open": 94.81, "high": 94.99, "low": 91.45, "close": 94.26, "volume": 95342030},
      {"begin": "2026-07-08 00:00:00", "end": "2026-07-08 20:26:29", "open": 94.26, "high": 95.75, "low": 92.82, "close": 95.2, "volume": 61105310}
    ],
    "LKOH": [
      {"begin": "2026-06-24 00:00:00", "end": "2026-06-24 23:59:59", "open": 4267, "high": 4291, "low": 4083, "close": 4109, "volume": 1640247},
      {"begin": "2026-06-25 00:00:00", "end": "2026-06-25 23:59:59", "open": 4109, "high": 4227.5, "low": 4086, "close": 4132.5, "volume": 2126795},
      {"begin": "2026-06-26 00:00:00", "end": "2026-06-26 23:59:57", "open": 4118.5, "high": 4474.5, "low": 4061, "close": 4365, "volume": 2455681},
      {"begin": "2026-06-27 00:00:00", "end": "2026-06-27 23:59:57", "open": 4387, "high": 4430, "low": 4373.5, "close": 4396, "volume": 109190},
      {"begin": "2026-06-28 00:00:00", "end": "2026-06-28 23:59:59", "open": 4396, "high": 4420, "low": 4372, "close": 4389.5, "volume": 105073},
      {"begin": "2026-06-29 00:00:00", "end": "2026-06-29 23:59:59", "open": 4389.5, "high": 4587, "low": 4266.5, "close": 4562, "volume": 2046406},
      {"begin": "2026-06-30 00:00:00", "end": "2026-06-30 23:59:59", "open": 4549, "high": 4684.5, "low": 4504, "close": 4552.5, "volume": 1489501},
      {"begin": "2026-07-01 00:00:00", "end": "2026-07-01 23:59:53", "open": 4551, "high": 4628.5, "low": 4481, "close": 4529, "volume": 990740},
      {"begin": "2026-07-02 00:00:00", "end": "2026-07-02 23:59:55", "open": 4539, "high": 4552, "low": 4244.5, "close": 4263, "volume": 1902751},
      {"begin": "2026-07-03 00:00:00", "end": "2026-07-03 23:59:59", "open": 4263, "high": 4364.5, "low": 4170, "close": 4254, "volume": 2082592},
      {"begin": "2026-07-04 00:00:00", "end": "2026-07-04 23:59:59", "open": 4254, "high": 4259.5, "low": 4203, "close": 4220, "volume": 78340},
      {"begin": "2026-07-05 00:00:00", "end": "2026-07-05 23:59:56", "open": 4360, "high": 4360, "low": 4255.5, "close": 4271.5, "volume": 118095},
      {"begin": "2026-07-06 00:00:00", "end": "2026-07-06 23:59:55", "open": 4268.5, "high": 4309.5, "low": 4221.5, "close": 4273.5, "volume": 1196482},
      {"begin": "2026-07-07 00:00:00", "end": "2026-07-07 23:59:51", "open": 4251.5, "high": 4405, "low": 4130, "close": 4376, "volume": 2068967},
      {"begin": "2026-07-08 00:00:00", "end": "2026-07-08 20:26:39", "open": 4383, "high": 4572.5, "low": 4366.5, "close": 4501, "volume": 1827497}
    ],
    "SBERP": [
      {"begin": "2026-06-24 00:00:00", "end": "2026-06-24 23:59:59", "open": 308.25, "high": 310.93, "low": 298, "close": 301.99, "volume": 3981861},
      {"begin": "2026-06-25 00:00:00", "end": "2026-06-25 23:59:59", "open": 302.89, "high": 305.79, "low": 294.6, "close": 296.36, "volume": 5823221},
      {"begin": "2026-06-26 00:00:00", "end": "2026-06-26 23:59:57", "open": 296.38, "high": 303.63, "low": 290.22, "close": 299.35, "volume": 8253660},
      {"begin": "2026-06-27 00:00:00", "end": "2026-06-27 23:59:57", "open": 300.02, "high": 301.3, "low": 299.6, "close": 300.54, "volume": 279673},
      {"begin": "2026-06-28 00:00:00", "end": "2026-06-28 23:59:59", "open": 301.2, "high": 301.23, "low": 299.4, "close": 300.54, "volume": 170180},
      {"begin": "2026-06-29 00:00:00", "end": "2026-06-29 23:59:59", "open": 301.33, "high": 309.36, "low": 295.96, "close": 308.5, "volume": 4911555},
      {"begin": "2026-06-30 00:00:00", "end": "2026-06-30 23:59:59", "open": 308.5, "high": 312.98, "low": 305.36, "close": 308.44, "volume": 4099126},
      {"begin": "2026-07-01 00:00:00", "end": "2026-07-01 23:59:53", "open": 308.72, "high": 311.54, "low": 305.5, "close": 307.15, "volume": 2944098},
      {"begin": "2026-07-02 00:00:00", "end": "2026-07-02 23:59:55", "open": 307.2, "high": 308.48, "low": 299.5, "close": 301.7, "volume": 5309346},
      {"begin": "2026-07-03 00:00:00", "end": "2026-07-03 23:59:59", "open": 302.5, "high": 305, "low": 297.72, "close": 301.38, "volume": 5009906},
      {"begin": "2026-07-04 00:00:00", "end": "2026-07-04 23:59:59", "open": 301.7, "high": 302.18, "low": 300.54, "close": 301.39, "volume": 159031},
      {"begin": "2026-07-05 00:00:00", "end": "2026-07-05 23:59:56", "open": 303.4, "high": 303.98, "low": 302.48, "close": 303.97, "volume": 273414},
      {"begin": "2026-07-06 00:00:00", "end": "2026-07-06 23:59:55", "open": 303.98, "high": 305.69, "low": 294.65, "close": 298.97, "volume": 4021141},
      {"begin": "2026-07-07 00:00:00", "end": "2026-07-07 23:59:51", "open": 298.96, "high": 299.89, "low": 292.15, "close": 299.22, "volume": 4092003},
      {"begin": "2026-07-08 00:00:00", "end": "2026-07-08 20:26:39", "open": 298.9, "high": 301, "low": 294.8, "close": 298.97, "volume": 3241223}
    ],
    "VTBR": [
      {"begin": "2026-06-24 00:00:00", "end": "2026-06-24 23:59:59", "open": 72.795, "high": 73.73, "low": 70.52, "close": 71.455, "volume": 91521064},
      {"begin": "2026-06-25 00:00:00", "end": "2026-06-25 23:59:59", "open": 71.46, "high": 72.48, "low": 69.84, "close": 70.785, "volume": 72250965},
      {"begin": "2026-06-26 00:00:00", "end": "2026-06-26 23:59:57", "open": 70.79, "high": 73.465, "low": 69.645, "close": 71.67, "volume": 97397407},
      {"begin": "2026-06-27 00:00:00", "end": "2026-06-27 23:59:57", "open": 71.855, "high": 72.015, "low": 71.5, "close": 71.615, "volume": 1924987},
      {"begin": "2026-06-28 00:00:00", "end": "2026-06-28 23:59:59", "open": 71.615, "high": 71.955, "low": 71.58, "close": 71.895, "volume": 1973350},
      {"begin": "2026-06-29 00:00:00", "end": "2026-06-29 23:59:59", "open": 71.99, "high": 74.84, "low": 70.855, "close": 74.48, "volume": 64386792},
      {"begin": "2026-06-30 00:00:00", "end": "2026-06-30 23:59:59", "open": 74.39, "high": 75.99, "low": 73.155, "close": 73.825, "volume": 65352594},
      {"begin": "2026-07-01 00:00:00", "end": "2026-07-01 23:59:53", "open": 73.9, "high": 75.075, "low": 73, "close": 73.385, "volume": 43775155},
      {"begin": "2026-07-02 00:00:00", "end": "2026-07-02 23:59:55", "open": 73.495, "high": 73.57, "low": 70.63, "close": 71.17, "volume": 52702402},
      {"begin": "2026-07-03 00:00:00", "end": "2026-07-03 23:59:59", "open": 70.83, "high": 71.8, "low": 69.78, "close": 70.155, "volume": 60831174},
      {"begin": "2026-07-04 00:00:00", "end": "2026-07-04 23:59:59", "open": 70.27, "high": 70.27, "low": 69.725, "close": 70.055, "volume": 3638761},
      {"begin": "2026-07-05 00:00:00", "end": "2026-07-05 23:59:56", "open": 70.4, "high": 70.75, "low": 70.21, "close": 70.45, "volume": 4924347},
      {"begin": "2026-07-06 00:00:00", "end": "2026-07-06 23:59:55", "open": 70.57, "high": 70.64, "low": 62.33, "close": 64.185, "volume": 577001747},
      {"begin": "2026-07-07 00:00:00", "end": "2026-07-07 23:59:51", "open": 64.17, "high": 65.855, "low": 60.3, "close": 65.05, "volume": 426225790},
      {"begin": "2026-07-08 00:00:00", "end": "2026-07-08 20:26:39", "open": 65.05, "high": 65.5, "low": 63.605, "close": 64.795, "volume": 93588520}
    ]
  }
}
}
"""

# Read the clean JSON data
data = json.loads(raw_data)

# Read the moex_data.json file that contains the portfolio information
with open('C:\\Users\\moria\\AppData\\Local\\hermes\\skills\\moex-ai-hedge-fund\\moex_data.json', 'r') as f:
    moex_data = json.load(f)

# Extract portfolio information from the moex_data.json file
portfolio_text = moex_data['portfolio']
import re

ticker_data = {}
lines = portfolio_text.split('\n')
for line in lines:
    line = line.strip()
    if not line or not line[0].isalpha():
        continue
    
    parts = line.split()
    if len(parts) >= 4:
        ticker = parts[0].strip()
        price = float(re.sub(r'[^\d.-]', '', parts[1]))
        chg_text = parts[2].strip()
        
        if '%' in parts[3]:
            chg_pct = float(re.sub(r'%\s*', '', parts[3]))
        else:
            chg_pct = 0.0
        
        vol_str = ''.join(parts[4:]).replace(',', '')
        volume = int(vol_str) if vol_str.isdigit() else 0
        
        ticker_data[ticker] = {
            'price': price,
            'chg': chg_text,
            'chg_pct': chg_pct,
            'volume': volume
        }

# Process each ticker to calculate metrics
candles = data['candles']
results = {}

for ticker in data['meta']['tickers']:
    ticker_results = {
        'dates': [],
        'prices': [],
        'volumes': [],
        'price_changes': [],
        'volatilities': []
    }
    
    if ticker in candles:
        for candle in candles[ticker]:
            ticker_results['dates'].append(candle['begin'][:10])
            ticker_results['prices'].append(candle['close'])
            ticker_results['volumes'].append(candle['volume'])
            price_change = ((candle['close'] - candle['open']) / candle['open']) * 100
            ticker_results['price_changes'].append(price_change)
            volatility = candle['high'] - candle['low']
            ticker_results['volatilities'].append(volatility)
    
    results[ticker] = ticker_results

# Calculate metrics per ticker
analysis_results = []
total_volume_sum = 0
total_volume_count = 0
volatilities = {}

print("=== QUANTITATIVE ANALYSIS RESULTS ===\n")

for ticker in data['meta']['tickers']:
    if ticker not in ticker_data:
        continue
    
    ticker_info = ticker_data[ticker]
    ticker_results = results[ticker]
    
    # Calculate average volume for the period
    avg_volume = sum(ticker_results['volumes']) / len(ticker_results['volumes']) if ticker_results['volumes'] else 0
    total_volume_sum += avg_volume
    total_volume_count += 1
    
    # Calculate average volatility for the period (14-day range)
    avg_volatility = sum(ticker_results['volatilities']) / len(ticker_results['volatilities']) if ticker_results['volatilities'] else 0
    volatilities[ticker] = avg_volatility
    
    max_volatility = max(ticker_results['volatilities']) if ticker_results['volatilities'] else 0
    
    # Determine volatility level
    if avg_volatility < 50:
        volatility_level = "LOW"
    elif avg_volatility < 150:
        volatility_level = "MEDIUM"
    else:
        volatility_level = "HIGH"
    
    current_price = ticker_info['price']
    daily_change_pct = ticker_info['chg_pct']
    
    # Calculate volume status vs average
    avg_volume_current = avg_volume
    if avg_volume_current > 0:
        volume_vs_avg = (ticker_info['volume'] - avg_volume_current) / avg_volume_current * 100
        if volume_vs_avg < -50:
            volume_status = "BELOW_AVERAGE"
        elif volume_vs_avg > 50:
            volume_status = "ABOVE_AVERAGE"
        else:
            volume_status = "AVERAGE"
    else:
        volume_status = "AVERAGE"
    
    # Volume trend analysis - check for bearish signal (price drops, volume increases)
    volume_trend_bullish = False
    if ticker in candles and len(candles[ticker]) >= 2:
        latest_candle = candles[ticker][-1]
        previous_candle = candles[ticker][-2]
        
        price_dropped = latest_candle['close'] < previous_candle['close']
        volume_increased = latest_candle['volume'] > previous_candle['volume']
        
        if price_dropped and volume_increased:
            volume_trend_bullish = True
    
    # Generate signals based on quantitative analysis
    signals = []
    
    # Signal 1: Positive daily change with good volume and low volatility
    if daily_change_pct > 1.0 and volume_status in ["ABOVE_AVERAGE", "AVERAGE"] and avg_volatility < 100:
        signals.append(('BUY', 80, 2))
    
    # Signal 2: Negative daily change but volume trend bullish (potential reversal)
    elif daily_change_pct < -1.0 and volume_trend_bullish:
        signals.append(('BUY', 65, 3))
    
    # Signal 3: Very strong positive daily change (potential overextension)
    elif daily_change_pct > 2.0:
        signals.append(('SELL', 55, 4))
    
    # Signal 4: Very strong negative daily change with bearish volume trend
    elif daily_change_pct < -2.0 and not volume_trend_bullish:
        signals.append(('SELL', 50, 4))
    
    # Signal 5: Low volume but positive price change
    elif volume_status == "BELOW_AVERAGE" and daily_change_pct > 0.5:
        signals.append(('BUY', 60, 3))
    
    # Default signal if no specific conditions met
    if len(signals) == 0:
        signals.append(('HOLD', 30, 2))
    
    # Additional signal: High volatility risk
    if max_volatility > 500:
        signals.append(('SELL', 70, 4))
    
    # Additional signal: Low volatility with small positive change (15% risk of HOLD)
    if avg_volatility < 50 and daily_change_pct < 0.5:
        signals.append(('HOLD', 40, 1))
    
    # Select best signal (prefer BUY over SELL, and higher confidence)
    signals.sort(key=lambda x: (x[1], {'BUY': 3, 'SELL': 2, 'HOLD': 1}[x[0]]), reverse=True)
    
    best_signal, confidence, risk = signals[0]
    
    # Format output as requested
    result_line = f"{ticker} | {daily_change_pct:+.2f}% | {volatility_level} | {volume_status} | {best_signal} | {confidence}% | {risk}"
    analysis_results.append(result_line)

# Print main analysis table
for line in analysis_results:
    print(line)

# Calculate correlation between tickers
print("\n=== CORRELATION ANALYSIS ===\n")
price_data = {ticker: ticker_results['prices'] for ticker, ticker_results in results.items()}

correlations = {}
for ticker1 in price_data:
    corrs = []
    for ticker2 in price_data:
        if ticker1 == ticker2:
            continue
        prices1 = price_data[ticker1]
        prices2 = price_data[ticker2]
        if len(prices1) > 1 and len(prices2) > 1:
            mean1 = sum(prices1) / len(prices1)
            mean2 = sum(prices2) / len(prices2)
            cov = sum((p1 - mean1) * (p2 - mean2) for p1, p2 in zip(prices1, prices2)) / len(prices1)
            std1 = (sum((p - mean1) ** 2 for p in prices1) / len(prices1)) ** 0.5
            std2 = (sum((p - mean2) ** 2 for p in prices2) / len(prices2)) ** 0.5
            corr = cov / (std1 * std2) if std1 > 0 and std2 > 0 else 0
            corrs.append((ticker2, corr))
    correlations[ticker1] = corrs

for ticker, corrs in correlations.items():
    if corrs:
        print(f"{ticker}: ", end="")
        for corr_ticker, corr_val in corrs[:3]:
            direction = "positively" if corr_val > 0 else "negatively"
            strength = f"({corr_val:.2f})" if abs(corr_val) > 0.1 else "(weak)"
            print(f"{corr_ticker} {direction} correlated {strength}", end=" | ")
        print()

# Calculate best and worst tickers by risk/return
print("\n=== BEST/WORST TICKER ANALYSIS ===\n")

scores = []
for ticker in data['meta']['tickers']:
    if ticker not in ticker_data:
        continue
    
    ticker_results = results[ticker]
    
    # Calculate total return over the period
    if len(ticker_results['prices']) >= 2:
        initial_price = ticker_results['prices'][0]
        final_price = ticker_results['prices'][-1]
        total_return = (final_price - initial_price) / initial_price * 100
    else:
        total_return = 0
    
    # Calculate volatility (standard deviation of daily returns)
    if len(ticker_results['price_changes']) > 0:
        volatility = (sum(pc ** 2 for pc in ticker_results['price_changes']) / len(ticker_results['price_changes'])) ** 0.5
    else:
        volatility = 0
    
    # Risk/return score (higher is better) - using Sharpe-like ratio
    if volatility > 0:
        risk_adjusted_return = total_return / volatility
    else:
        risk_adjusted_return = total_return
    
    scores.append((ticker, risk_adjusted_return, total_return, volatility))

scores.sort(key=lambda x: x[1], reverse=True)  # Sort by risk-adjusted return

best_ticker = scores[0][0] if scores else "N/A"
best_score = scores[0][1] if scores else 0
best_return = scores[0][2] if scores else 0
best_vol = scores[0][3] if scores else 0

worst_ticker = scores[-1][0] if scores else "N/A"
worst_score = scores[-1][1] if scores else 0
worst_return = scores[-1][2] if scores else 0
worst_vol = scores[-1][3] if scores else 0

print(f"Best Ticker (Risk/Return): {best_ticker}")
print(f"  Risk-Adjusted Return: {best_score:.2f}")
print(f"  Total Return: {best_return:.2f}%")
print(f"  Volatility: {best_vol:.2f}")

print(f"\nWorst Ticker (Risk/Return): {worst_ticker}")
print(f"  Risk-Adjusted Return: {worst_score:.2f}")
print(f"  Total Return: {worst_return:.2f}%")
print(f"  Volatility: {worst_vol:.2f}")

# Calculate portfolio metrics
print("\n=== PORTFOLIO METRICS ===\n")

total_avg_volume = total_volume_sum / total_volume_count if total_volume_count > 0 else 0
total_portfolio_volatility = sum(avg_vol for avg_vol in volatilities.values()) / len(volatilities) if volatilities else 0

# Portfolio concentration based on inverse variance weighting
weights = {}
for ticker, ticker_results in results.items():
    if ticker in volatilities:
        weights[ticker] = 1.0 / (volatilities[ticker] + 0.001)

if weights:
    total_weight = sum(weights.values())
    for ticker in weights:
        weights[ticker] = weights[ticker] / total_weight

if weights:
    concentration = max(weights.values()) / (1.0 / len(weights)) if len(weights) > 0 else 1.0
    if concentration < 0.6:
        concentration_label = "LOW"
    elif concentration < 0.8:
        concentration_label = "MEDIUM"
    else:
        concentration_label = "HIGH"
else:
    concentration_label = "N/A"

print(f"Portfolio Concentration: {concentration_label}")
print(f"Overall Portfolio Volatility: {total_portfolio_volatility:.2f}")
print(f"Average Volume across tickers: {total_avg_volume:,.0f}")