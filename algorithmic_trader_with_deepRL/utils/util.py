from technical_indicators import *
from get_data import load_data, get_path

def indicators_dict(symbol, prices, volume, window = 7):
  return {
    f'{symbol}': prices,
    f'{symbol}_norm': normalize(prices),
    'trend_rsi': relative_strength_index(prices, window),
    'mom_moms': momentum(prices, window),
    'trend_stok': stochastic_oscillator_k(prices, window),
    'trend_stod': stochastic_oscillator_d(prices, window),
    'volume_obv': on_balance_volume(prices, volume),
    'trend_sma': simple_moving_average(prices, window),
    'trend_p2sma': price_to_sma(prices, simple_moving_average(prices, window)),
    'trend_ema': exponential_moving_average(prices, window),
    'trend_p2ema': price_to_ema(prices, exponential_moving_average(prices)),
    'trend_macd': moving_average_convergence_divergence(prices),
    'vol_bbl': bollinger_bands(prices, simple_moving_average(prices))[0],
    'vol_bbh': bollinger_bands(prices, simple_moving_average(prices))[1],
    'vol_bbp': bollinger_band_pct(prices, simple_moving_average(prices))
  }

def create_df(data, index):
  df = pd.DataFrame(index = index)
  for key in data.keys(): df[key] = data[key]
  return df

def data_df(symbol, n_period = 7, fillna = True):
  data = load_data(symbol)
  inds = indicators_dict(symbol, data[symbol], data.volume, window = n_period)
  df = create_df(inds, data.index)

  high, low, close, volume = data.high, data.low, data.close, data.volume
  df = df.join(add_momentum_indicators(high, low, close, volume, n_period, fillna))
  df = df.join(add_trend_indicators(high, low, close, volume, n_period, fillna))
  df = df.join(add_volatility_indicators(high, low, close, n_period, fillna))
  df = df.join(add_volume_indicators(high, low, close, volume, n_period, fillna))
  return df

def holdings_df(trades, starting_balance):
  holdings = trades.copy()
  holdings['Cash'][0] += starting_balance
  return holdings.cumsum()


def stock_value_df(prices, holdings):
  holdings_ = holdings.drop('Cash', axis = 1)
  vals = prices[:, None] * holdings_
  vals['Cash'] = holdings[['Cash']]
  return vals.sum(axis = 1)

def portfolio_statistics(values, daily_rf = 0, samples_per_year = 252):
  cum_return = (values[-1] / values[0]) - 1

  daily_returns = (values /values.shift(1)) - 1
  daily_returns.iloc[0] = 0
  daily_returns = daily_returns[1:]

  avg_daily_returns = daily_returns.mean()
  std_daily_returns = daily_returns.std()

  K = np.sqrt(samples_per_year)
  sharpe_ratio = K * (avg_daily_returns - daily_rf) / std_daily_returns
  return cum_return, avg_daily_returns, std_daily_returns, sharpe_ratio
