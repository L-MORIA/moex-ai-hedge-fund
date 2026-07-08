import json
import pandas as pd
import numpy as np

# Parse portfolio data from the message
portfolio_lines = """Portfolio summary (5 tickers)
  Ticker        Price        Chg     Chg%          Vol
  ----------------------------------------------------
  SBER         298.34      -0.64   -0.21%   40,643,658
  GAZP          95.39      +1.13   +1.18%   61,557,540
  LKOH        4515.50    +139.50   +3.09%    1,839,712
  SBERP        299.34      +0.12   +0.04%    3,279,938
  VTBR          64.83      -0.21   -0.33%   94,091,139
  ----------------------------------------------------
  Total volume: 201,411,987 shares"""

# Parse portfolio data
portfolio_data = {}
for line in portfolio_lines.split('\n'):
    if line.strip() and not line.startswith('---') and not line.startswith('Portfolio') and not line.startswith('Total'):
        parts = line.split()
        if len(parts) >= 5:
            ticker = parts[0]
            price = float(parts[1])
            chg_pct = float(parts[3].replace('%', ''))
            volume = int(parts[4].replace(',', ''))
            portfolio_data[ticker] = {
                'price': price,
                'chg_pct': chg_pct,
                'volume': volume
            }

# Candles data (already parsed earlier)
candles = {
    "SBER": [
        {"open": 307.31, "high": 310.33, "low": 298, "close": 301.92, "volume": 55513803},
        {"open": 302.47, "high": 305.8, "low": 294.2, "close": 295.16, "volume": 76647625},
        {"open": 296, "high": 303.9, "low": 290.35, "close": 299.18, "volume": 85683639},
        {"open": 299.5, "high": 301.36, "low": 299.18, "close": 299.69, "volume": 2907428},
        {"open": 299.7, "high": 300.47, "low": 298.61, "close": 299.97, "volume": 2824723},
        {"open": 300, "high": 308.55, "low": 296.02, "close": 307.9, "volume": 55268988},
        {"open": 307.9, "high": 312.65, "low": 305.7, "close": 308.09, "volume": 44933411},
        {"open": 308.12, "high": 311.57, "low": 305.55, "close": 307.04, "volume": 40780087},
        {"open": 307.1, "high": 308.2, "low": 299.83, "close": 301.05, "volume": 45930395},
        {"open": 301.65, "high": 303.25, "low": 298.04, "close": 301.19, "volume": 33006616},
        {"open": 301.39, "high": 301.69, "low": 300.28, "close": 300.76, "volume": 1357409},
        {"open": 304.42, "high": 304.42, "low": 302.01, "close": 303.34, "volume": 2735540},
        {"open": 303.47, "high": 305.6, "low": 294.07, "close": 298.77, "volume": 46121572},
        {"open": 299.02, "high": 299.47, "low": 292.12, "close": 298.98, "volume": 49403734},
        {"open": 299.38, "high": 301.18, "low": 293.8, "close": 297.92, "volume": 40754476}
    ],
    "GAZP": [
        {"open": 102, "high": 102.41, "low": 97.13, "close": 98.02, "volume": 98523170},
        {"open": 98.48, "high": 99.72, "low": 97.3, "close": 98.07, "volume": 78716230},
        {"open": 98.07, "high": 101.12, "low": 95.65, "close": 99.07, "volume": 112721030},
        {"open": 99.28, "high": 99.66, "low": 99.1, "close": 99.28, "volume": 2100900},
        {"open": 99.39, "high": 99.68, "low": 99.08, "close": 99.22, "volume": 3023750},
        {"open": 99.59, "high": 102.69, "low": 97.8, "close": 101.98, "volume": 64026390},
        {"open": 101.98, "high": 103.59, "low": 100.32, "close": 100.9, "volume": 59912800},
        {"open": 100.9, "high": 102.53, "low": 99.93, "close": 101.03, "volume": 30413950},
        {"open": 100.91, "high": 101.64, "low": 96.55, "close": 97.05, "volume": 58826190},
        {"open": 97.2, "high": 98.5, "low": 96.07, "close": 96.84, "volume": 51279690},
        {"open": 96.94, "high": 97.8, "low": 96.64, "close": 96.91, "volume": 1882320},
        {"open": 98.7, "high": 98.9, "low": 97.33, "close": 97.84, "volume": 4938010},
        {"open": 98, "high": 98.12, "low": 94.69, "close": 94.81, "volume": 59511620},
        {"open": 94.81, "high": 94.99, "low": 91.45, "close": 94.26, "volume": 95342030},
        {"open": 94.26, "high": 95.75, "low": 92.82, "close": 95.25, "volume": 61708660}
    ],
    "LKOH": [
        {"open": 4267, "high": 4291, "low": 4083, "close": 4109, "volume": 1640247},
        {"open": 4109, "high": 4227.5, "low": 4086, "close": 4132.5, "volume": 2126795},
        {"open": 4118.5, "high": 4474.5, "low": 4061, "close": 4365, "volume": 2455681},
        {"open": 4387, "high": 4430, "low": 4373.5, "close": 4396, "volume": 109190},
        {"open": 4396, "high": 4420, "low": 4372, "close": 4389.5, "volume": 105073},
        {"open": 4389.5, "high": 4587, "low": 4266.5, "close": 4562, "volume": 2046406},
        {"open": 4549, "high": 4684.5, "low": 4504, "close": 4552.5, "volume": 1489501},
        {"open": 4551, "high": 4628.5, "low": 4481, "close": 4529, "volume": 990740},
        {"open": 4539, "high": 4552, "low": 4244.5, "close": 4263, "volume": 1902751},
        {"open": 4263, "high": 4364.5, "low": 4170, "close": 4254, "volume": 2082592},
        {"open": 4254, "high": 4259.5, "low": 4203, "close": 4220, "volume": 78340},
        {"open": 4360, "high": 4360, "low": 4255.5, "close": 4271.5, "volume": 118095},
        {"open": 4268.5, "high": 4309.5, "low": 4221.5, "close": 4273.5, "volume": 1196482},
        {"open": 4251.5, "high": 4405, "low": 4130, "close": 4376, "volume": 2068967},
        {"open": 4383, "high": 4572.5, "low": 4366.5, "close": 4509, "volume": 1844489}
    ],
    "SBERP": [
        {"open": 308.25, "high": 310.93, "low": 298, "close": 301.99, "volume": 3981861},
        {"open": 302.89, "high": 305.79, "low": 294.6, "close": 296.36, "volume": 5823221},
        {"open": 296.38, "high": 303.63, "low": 290.22, "close": 299.35, "volume": 8253660},
        {"open": 300.02, "high": 301.3, "low": 299.6, "close": 300.54, "volume": 279673},
        {"open": 301.2, "high": 301.23, "low": 299.4, "close": 300.54, "volume": 170180},
        {"open": 301.33, "high": 309.36, "low": 295.96, "close": 308.5, "volume": 4911555},
        {"open": 308.5, "high": 312.98, "low": 305.36, "close": 308.44, "volume": 4099126},
        {"open": 308.72, "high": 311.54, "low": 305.5, "close": 307.15, "volume": 2944098},
        {"open": 307.2, "high": 308.48, "low": 299.5, "close": 301.7, "volume": 5309346},
        {"open": 302.5, "high": 305, "low": 297.72, "close": 301.38, "volume": 5009906},
        {"open": 301.7, "high": 302.18, "low": 300.54, "close": 301.39, "volume": 159031},
        {"open": 303.4, "high": 303.98, "low": 302.48, "close": 303.97, "volume": 273414},
        {"open": 303.98, "high": 305.69, "low": 294.65, "close": 298.97, "volume": 4021141},
        {"open": 298.96, "high": 299.89, "low": 292.15, "close": 299.22, "volume": 4092003},
        {"open": 298.9, "high": 301, "low": 294.8, "close": 298.95, "volume": 3294820}
    ],
    "VTBR": [
        {"open": 72.795, "high": 73.73, "low": 70.52, "close": 71.455, "volume": 91521064},
        {"open": 71.46, "high": 72.48, "low": 69.84, "close": 70.785, "volume": 72250965},
        {"open": 70.79, "high": 73.465, "low": 69.645, "close": 71.67, "volume": 97397407},
        {"open": 71.855, "high": 72.015, "low": 71.5, "close": 71.615, "volume": 1924987},
        {"open": 71.615, "high": 71.955, "low": 71.58, "close": 71.895, "volume": 1973350},
        {"open": 71.99, "high": 74.84, "low": 70.855, "close": 74.48, "volume": 64386792},
        {"open": 74.39, "high": 75.99, "low": 73.155, "close": 73.825, "volume": 65352594},
        {"open": 73.9, "high": 75.075, "low": 73, "close": 73.385, "volume": 43775155},
        {"open": 73.495, "high": 73.57, "low": 70.63, "close": 71.17, "volume": 52702402},
        {"open": 70.83, "high": 71.8, "low": 69.78, "close": 70.155, "volume": 60831174},
        {"open": 70.27, "high": 70.27, "low": 69.725, "close": 70.055, "volume": 3638761},
        {"open": 70.4, "high": 70.75, "low": 70.21, "close": 70.45, "volume": 4924347},
        {"open": 70.57, "high": 70.64, "low": 62.33, "close": 64.185, "volume": 577001747},
        {"open": 64.17, "high": 65.855, "low": 60.3, "close": 65.05, "volume": 426225790},
        {"open": 65.05, "high": 65.5, "low": 63.605, "close": 64.765, "volume": 94192537}
    ]
}

# Create portfolio list for analysis
portfolio = []
for ticker in ['SBER', 'GAZP', 'LKOH', 'SBERP', 'VTBR']:
    data = portfolio_data[ticker]
    df = pd.DataFrame(candles[ticker])
    
    # Calculate volatility based on 14-day high-low range
    df['price_range'] = df['high'] - df['low']
    avg_range = df['price_range'].mean()
    volatility_percent = (avg_range / df['close'].iloc[-1]) * 100
    
    # Determine volatility rating
    if volatility_percent < 2:
        volatility_rating = 'LOW'
    elif volatility_percent < 5:
        volatility_rating = 'MEDIUM'
    else:
        volatility_rating = 'HIGH'
    
    # Volume analysis
    current_volume = data['volume']
    avg_volume = df['volume'].mean()
    if current_volume > avg_volume * 1.5:
        volume_status = 'ABOVE_AVG'
    elif current_volume < avg_volume * 0.5:
        volume_status = 'BELOW_AVG'
    else:
        volume_status = 'AVG'
    
    # Generate signal based on daily price change and volume
    if data['chg_pct'] > 1 and volume_status in ['ABOVE_AVG', 'AVG']:
        signal = 'BUY'
        confidence = 70 + min(abs(data['chg_pct']) * 10, 30)
    elif data['chg_pct'] < -1 and volume_status == 'ABOVE_AVG':
        signal = 'SELL'
        confidence = 70 + min(abs(data['chg_pct']) * 10, 30)
    else:
        signal = 'HOLD'
        confidence = 40 + min(abs(data['chg_pct']) * 5, 30)
    
    # Risk assessment based on volatility and price movement
    if volatility_rating == 'HIGH' or abs(data['chg_pct']) > 3:
        risk = 5
    elif volatility_rating == 'MEDIUM' or abs(data['chg_pct']) > 2:
        risk = 4
    elif volatility_rating == 'LOW':
        risk = 1
    else:
        risk = 2
    
    portfolio.append({
        'ticker': ticker,
        'price': data['price'],
        'daily_chg_pct': data['chg_pct'],
        'volume': data['volume'],
        'volatility_rating': volatility_rating,
        'volatility_percent': volatility_percent,
        'volume_status': volume_status,
        'signal': signal,
        'confidence': int(confidence),
        'risk': risk
    })

# Calculate correlations between tickers
price_data = {ticker: pd.DataFrame(candles[ticker])['close'] for ticker in ['SBER', 'GAZP', 'LKOH', 'SBERP', 'VTBR']}
price_df = pd.DataFrame(price_data)
correlations = price_df.corr()

# Find best and worst tickers by risk/return
best_ticker = max(portfolio, key=lambda x: (x['daily_chg_pct'] / x['risk']) if x['risk'] > 0 else 0)
worst_ticker = min(portfolio, key=lambda x: (x['daily_chg_pct'] / x['risk']) if x['risk'] > 0 else 0)

# Portfolio metrics
volumes = [p['volume'] for p in portfolio]
concentration = max([(v / sum(volumes)) * 100 for v in volumes])

avg_volume = np.mean(volumes)
total_volume = sum(volumes)

total_volatility = np.mean([p['volatility_percent'] for p in portfolio])

# Print results
print("=== QUANTITATIVE ANALYZER ===")
print()

# Individual ticker analysis
print("INDIVIDUAL TICKER ANALYSIS:")
print("TICKER | Δ% | VOLATILITY | VOLUME_VS_AVG | SIGNAL | CONFIDENCE% | RISK")
print("-" * 80)
for p in portfolio:
    print(f"{p['ticker']} | {p['daily_chg_pct']:+.2f}% | {p['volatility_rating']} | {p['volume_status']} | {p['signal']} | {p['confidence']}% | {p['risk']}")
print()

# Correlation matrix
print("CORRELATIONS:")
print(correlations.round(2).to_string())
print()

# Best/worst performers
print("PERFORMANCE ANALYSIS:")
print(f"Best risk/return: {best_ticker['ticker']} (Δ%{best_ticker['daily_chg_pct']:.2f}, Risk {best_ticker['risk']})")
print(f"Worst risk/return: {worst_ticker['ticker']} (Δ%{worst_ticker['daily_chg_pct']:.2f}, Risk {worst_ticker['risk']})")
print()

# Portfolio metrics
print("PORTFOLIO METRICS:")
print(f"Concentration: {concentration:.1f}% (lower is better)")
print(f"Total Volume: {total_volume:,} shares")
print(f"Average Volume: {avg_volume:,.0f} shares")
print(f"Overall Volatility: {total_volatility:.2f}%")