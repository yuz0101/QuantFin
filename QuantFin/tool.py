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

def winsorize(data: DataFrame, var: str, interval: str, by: list = None, new_label: str = None, cutoff: bool = False):
    '''The function `winsorize` takes a DataFrame, a variable name, an interval, optional grouping
    variables, and optional parameters to winsorize the variable values within the specified interval.
    
    Parameters
    ----------
    data : DataFrame
        The `data` parameter is expected to be a DataFrame containing the dataset on which you want to
    perform winsorization. It should include the variable specified in the `var` parameter that you want
    to winsorize.
    var : str
        The `var` parameter in the `winsorize` function refers to the column name in the DataFrame `data`
    that you want to winsorize. It is the variable for which you want to apply the winsorization
    procedure.
    interval : str
        The `interval` parameter in the `winsorize` function specifies the range of percentiles to be used
    for winsorization. It is a string that represents the lower and upper bounds of the interval. For
    example, if `interval = '[.01, .99)'`, it means that 1% <= data < 99%.
    by : list
        The `by` parameter in the `winsorize` function is used to specify a list of columns to group the
    data by before applying the winsorization process. This parameter allows you to perform
    winsorization within groups defined by the columns specified in the `by` list. If you do
    new_label : str
        The `new_label` parameter in the `winsorize` function is used to specify a new label for the
    winsorized variable in the output DataFrame. If provided, the winsorized variable will be renamed
    with the value of `new_label`. If not provided, the winsorized variable
    cutoff : bool, optional
        The `cutoff` parameter in the `winsorize` function determines whether the values outside the
    specified interval should be replaced with NaN (missing values) or clipped to the nearest value
    within the interval.
    
    Returns
    -------
        The function `winsorize` returns a pandas Series containing the winsorized values of the specified
    variable in the input DataFrame. If a new_label is provided, the Series is renamed accordingly
    before being returned.
    
    '''
    interval = interval.replace(' ', '')
    dc = interval[0]
    uc = interval[-1]
    d, u = interval[1:-1].split(',')
    d, u = float(d), float(u)
    if not ((dc=='[' or dc=='(') and (uc==']'or uc==')')):
        print("Interval should be started from '(' or '[' and ended with ')' or ']'")
    if not (0<=d<=1 and 0<=u<=1):
        print("Percentiles should be between 0 and 1")
    
    if by:
        df = data.loc[:, by+[var]].set_index(by).copy()
        df.loc[:, 'u'] = df.groupby(by)[var].quantile(u)
        df.loc[:, 'd'] = df.groupby(by)[var].quantile(d)
    else:
        df = data.loc[:, [var]].copy()
        df.loc[:, 'u'] = df.loc[:, var].quantile(u)
        df.loc[:, 'd'] = df.loc[:, var].quantile(d)
    
    if cutoff:
        if '(' == dc:
            df.loc[df[var]<df['d'], var] = nan
        if ')' == uc:
            df.loc[df[var]>df['u'], var] = nan
        if '[' == dc:
            df.loc[df[var]<=df['d'], var] = nan
        if ']' == uc:
            df.loc[df[var]>=df['u'], var] = nan
    else:
        df.loc[df[var]<df['d'], var] = df.loc[df[var]<df['d'], 'd']
        df.loc[df[var]>df['u'], var] = df.loc[df[var]>df['u'], 'u']
            
    df.index = data.index
    df = df[var]
    if new_label:
        df = df.rename(new_label)
    return df

class Volatility:
    """
    developing... ... 
    """
    def vol_hist_rolling(self, data: DataFrame, window: int, minw: int=12) -> DataFrame:

        '''The function `vol_hist_rolling` calculates the rolling standard deviation of a DataFrame with a
        specified window size and minimum number of periods.
        
        Parameters
        ----------
        data : DataFrame
            DataFrame - the input data frame containing the volume data for which rolling standard deviation
        needs to be calculated.
        window : int
            The `window` parameter specifies the size of the moving window. It represents the number of
        observations used for calculating the statistic at each step.
        minw : int, optional
            The `minw` parameter in the `vol_hist_rolling` function represents the minimum number of
        observations required to have a non-null result at the beginning. In this case, it is set to a
        default value of 12, meaning that the rolling standard deviation calculation will only start
        producing results once
        
        Returns
        -------
            The function `vol_hist_rolling` is returning a DataFrame that contains the rolling standard
        deviation of the input DataFrame `df` using a specified window size and minimum number of periods.
        
        '''
        return data.rolling(window, min_periods=minw).std()

    def vol_ewma(self, data: DataFrame, burnin: int, lambda_: float=0.94):
        '''The function calculates the exponentially weighted moving average of squared returns using a
        specified lambda value after a burn-in period.
        
        Parameters
        ----------
        data : DataFrame
            The `data` parameter is expected to be a DataFrame containing the returns data.
        burnin : int
            The `burnin` parameter in the `vol_ewma` function is used to specify the number of initial
        observations to be excluded from the calculation of the EWMA (Exponentially Weighted Moving Average)
        volatility. These initial observations are typically considered as a "burn-in" period where the
        lambda_ : float
            The `lambda_` parameter in the `vol_ewma` function represents the decay factor used in the
        Exponentially Weighted Moving Average (EWMA) calculation for volatility. It determines the weight
        given to past observations in the calculation of the current volatility estimate.
        
        Returns
        -------
            The function `vol_ewma` returns a DataFrame `sigma2_samp` containing the exponentially weighted
        moving average (EWMA) of squared returns calculated using the input DataFrame `ret`, a specified
        burn-in period `burnin`, and a decay parameter `lambda_`.
        
        '''
        data2 = data**2
        data2_burn = data2[:burnin]
        data2_samp = data2[burnin:]
        time_line = list(data2_samp.index)
        sigma2_samp = data2_burn.var().rename(time_line[0]).to_frame().T
        for i,t in enumerate(time_line[1:]):
            t_1 = time_line[i-1]
            sigma2 = (1 - lambda_)*data2_samp.loc[t_1, :] + lambda_*sigma2_samp.loc[t_1, :]
            sigma2_samp.loc[t, :] = sigma2
        return sigma2_samp
    
    def vol_garch(self):
        
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