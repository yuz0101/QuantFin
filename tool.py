# -*- coding: utf-8 -*-
from numpy import nan, log, exp
from pandas import DataFrame


class Volatility:

    def hist(self, df: DataFrame, window: int, minw: int) -> DataFrame:
        return df.rolling(window, min_periods=minw).std()

    def ewma(self, ret: DataFrame, burnin: int, lambda_: float=0.94):
        ret2 = ret**2
        ret2_burn = ret2[:burnin]
        ret2_samp = ret2[burnin:]
        time_line = list(ret2_samp.index)
        sigma2_samp = ret2_burn.var().rename(time_line[0]).to_frame().T
        for i,t in enumerate(time_line[1:]):
            t_1 = time_line[i-1]
            sigma2 = (1 - lambda_)*ret2_samp.loc[t_1, :] + lambda_*sigma2_samp.loc[t_1, :]
            sigma2_samp.loc[t, :] = sigma2
        return sigma2_samp
    
    def garch(self):
        pass

class CumulativeReturn:

    def geometric(self, df: DataFrame, pre: int, post: int) -> DataFrame:
        df = df.fillna(0) + 1
        window = abs(post - pre) + 1
        for i in range(1, window):
            cr = cr * df.shift(i)
        cr = cr.shift(-post)
        cr = cr - 1
        cr = cr.replace(0, nan)
        return cr

    def logsum(self, df: DataFrame, pre: int, post: int) -> DataFrame:
        df = df.fillna(0) + 1
        window = abs(post - pre) + 1
        cr = log(df)
        cr = cr.rolling(window=window, min_periods=window).sum()
        cr = (exp(cr)-1).shift(-post)
        cr = cr.replace(0, nan)
        cr = cr.stack().rename(f'CR[{pre},{post}]').to_frame()
        cr[abs(cr[f'CR[{pre},{post}]']) < 0.0000001] = nan
        cr = cr.loc[:, f'CR_{pre}_{post}'].unstack()
        return cr

def rollingGeometricReturn(ret: DataFrame, window: int, decimals=4):
    """This is a function for calculating geometric returns wihin a rolling window in an efficient way.

    Args:
        ret (DataFrame): This is a dataframe of returns with columns of entities. E.g., A dataframe of monthly returns with a column index of tickers and an index of date.
        window (int): The window length for calculating the geometric returns.

    Returns:
        _df: Return a dataframe of geometric returns with input dataframe's columns and index.
    """
    ret = ret + 1 #ret.fillna(0) + 1
    _df = ret.copy()
    _df.iloc[:window-1, :] = nan
    prod = ret.iloc[:window, :].product()
    _df.iloc[window-1, :] = prod
    for i in range(window, len(_df)):
        prod = prod / ret.iloc[i-window, :].fillna(1) * ret.iloc[i, :].fillna(1)
        _df.iloc[i, :] = prod
    _df = _df - 1
    _df = _df.round(decimals)
    _df = _df.replace(0, nan)
    return _df