# -*- coding: utf-8 -*-
from pandas import DataFrame, DatetimeIndex, concat, qcut
from QuantFin.HandleError import InputError


def _cal_breakpoints(peak: float or int, bottom: float or int, decile: int)->list:
    return [x/100*(peak-bottom)-bottom for x in range(int(100/decile), 100, int(100/decile))]

def _assign_port_num(x, decile, edges):
    if x < edges[0]:
        return 1
    elif x >= edges[-1]:
        return decile
    else:
        for i, edge in enumerate(edges):
            if i > 0:
                if edges[i-1] <= x < edge:
                    return i+1

def _periodic_sorting(df, decile, ranking, ranking_method):
    if ranking:
        df = df.rank(method=ranking_method)
    peak = df.max()
    bottom = df.min()
    edges = _cal_breakpoints(peak, bottom, decile)
    edges.sort()
    df = df.apply(lambda x: _assign_port_num(x, decile, edges))
    return df

def _smart_periodic_sorting(df, decile, ranking=True, ranking_method='dense'):
    try:
        df = qcut(df, q=decile, labels=range(1, decile+1))
    except:
        df = _periodic_sorting(df, decile, ranking, ranking_method)
    return df

def univariate_sorting(
                    df: DataFrame,
                    on: str,
                    decile: int = 10,
                    label: str = 'port',
                    jdate: str = 'jdate',
                    entity: str = 'permno',
                    method: str = 'ranking',
                    ranking_method = 'dense',
                    ) -> DataFrame:
    """_summary_

    Args:
        df (DataFrame): _description_
        on (str): _description_
        decile (int, optional): _description_. Defaults to 10.
        label (str, optional): _description_. Defaults to 'port'.
        jdate (str, optional): _description_. Defaults to 'jdate'.
        entity (str, optional): _description_. Defaults to 'permno'.
        method (str, optional): _description_. Defaults to 'ranking'.
        ranking_method (str, optional): _description_. Defaults to 'dense'.

    Raises:
        InputError: _description_

    Returns:
        DataFrame: _description_
    """

    _d = df[[entity, jdate, on]].dropna()
    if method == 'qcut':
        _d.loc[:, label] = _d.groupby(jdate)[on].transform(
            lambda x: qcut(x, q=decile, labels=range(1, 1+decile))
            )
        _d.loc[:, label] = _d.loc[:, label].astype(int)
    elif method == 'ranking':
        _d.loc[:, label] = _d.groupby(jdate)[on].transform(
            lambda x: _periodic_sorting(x, decile, ranking=True, ranking_method=ranking_method)
            )
    elif method == 'value':
        _d.loc[:, label] = _d.groupby(jdate)[on].transform(
            lambda x: _periodic_sorting(x, decile, ranking=False, ranking_method=ranking_method)
            )
    elif method == 'smart':
        _d.loc[:, label] = _d.groupby(jdate)[on].transform(
            lambda x: _smart_periodic_sorting(x, decile)
            )
    else:
        raise InputError(
            "The arg of method should be 'smart', 'qcut', 'ranking' or 'value', see documentation for details."
        )
    _d = _d[[entity, jdate, label]]
    df = df.merge(_d, on=[entity, jdate], how='left')
    return df