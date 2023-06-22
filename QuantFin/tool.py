# -*- coding: utf-8 -*-
from numpy import nan, log, exp
from pandas import DataFrame

def geometric_ret(ret: DataFrame, window: int, decimals=4):
    '''This function calculates the geometric return of a DataFrame over a specified window.
    
    Parameters
    ----------
    ret : DataFrame
        A pandas DataFrame containing returns data.
    window : int
        The number of periods to use in the calculation of the geometric return.
    decimals, optional
        The number of decimal places to round the output to.
    
    Returns
    -------
        The function `geometric_ret` returns a DataFrame that contains the geometric returns calculated
    from the input DataFrame `ret` using a rolling window of size `window`. The calculated returns are
    rounded to `decimals` decimal places and any zero values are replaced with NaN.
    
    '''
    ret = ret + 1
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

def winsorize(data: DataFrame, var: str, interval: list, by: list = None, new_label: str = None, cutoff: bool = True):
    '''The function winsorize applies Winsorization to a specified variable in a DataFrame, either for the
    entire DataFrame or by a specified group, and can either replace values outside of a specified
    interval with the interval bounds or with NaN values.
    
    Parameters
    ----------
    data : DataFrame
        a pandas DataFrame containing the data to be winsorized
    var : str
        The name of the variable/column in the DataFrame that needs to be winsorized.
    interval : list
        The interval parameter is a list containing two values that represent the lower and upper quantiles
    to use for winsorizing the data. For example, if interval=[0.05, 0.95], the function will replace
    values below the 5th percentile with the 5th percentile value and
    by : list
        A list of column names to group the data by before applying the winsorization. If not provided, the
    function will apply the winsorization to the entire dataset.
    new_label : str
        The new label parameter is an optional parameter that allows the user to rename the column label of
    the resulting DataFrame. If this parameter is not specified, the resulting DataFrame will have the
    same label as the original DataFrame.
    cutoff : bool, optional
        A boolean parameter that determines whether values outside the specified interval should be
    replaced with the interval boundaries or set to NaN (default is True, meaning values will be
    replaced with the interval boundaries).
    
    Returns
    -------
        a pandas DataFrame with the winsorized values of the specified variable. The variable can be
    winsorized either for the entire dataset or by groups specified in the "by" parameter. The
    winsorization is done by replacing values above the upper quantile with the upper quantile value and
    values below the lower quantile with the lower quantile value. If the "cutoff"
    
    '''
    if by:
        df = data[by+[var]].set_index(by)
        df.loc[:, 'u'] = data.groupby(by)[var].quantile(interval[1])
        df.loc[:, 'd'] = data.groupby(by)[var].quantile(interval[0])
    else:
        df = data[[var]]
        df.loc[:, 'u'] = data[var].quantile(interval[1])
        df.loc[:, 'd'] = data[var].quantile(interval[0])
    if cutoff:
        df.loc[df[var]>df['u'], var] = df.loc[df[var]>df['u'], 'u']
        df.loc[df[var]<df['d'], var] = df.loc[df[var]<df['d'], 'd']
    else:
        df.loc[df[var]>df['u'], var] = nan
        df.loc[df[var]<df['d'], var] = nan
    df.index = data.index
    df = df[var]
    if new_label:
        df = df.rename(new_label)
    return df

class Volatility:
    """
    developing... ... 
    """
    def _hist(self, df: DataFrame, window: int, minw: int) -> DataFrame:
        return df.rolling(window, min_periods=minw).std()

    def _ewma(self, ret: DataFrame, burnin: int, lambda_: float=0.94):
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
    
    def _garch(self):
        pass

class CumulativeReturn:
    """
    developing... ... 
    """
    def _geometric(self, data: DataFrame, pre: int, post: int) -> DataFrame:
        data = data.fillna(0) + 1
        window = abs(post - pre) + 1
        for i in range(1, window):
            _cr = _cr * data.shift(i)
        _cr = _cr.shift(-post)
        _cr = _cr - 1
        _cr = _cr.replace(0, nan)
        return _cr

    def _logsum(self, data: DataFrame, pre: int, post: int) -> DataFrame:
        data = data.fillna(0) + 1
        window = abs(post - pre) + 1
        _cr = log(data)
        _cr = _cr.rolling(window=window, min_periods=window).sum()
        _cr = (exp(_cr)-1).shift(-post)
        _cr = _cr.replace(0, nan)
        _cr = _cr.stack().rename(f'CR[{pre},{post}]').to_frame()
        _cr[abs(_cr[f'CR[{pre},{post}]']) < 0.0000001] = nan
        _cr = _cr.loc[:, f'CR_{pre}_{post}'].unstack()
        return _cr