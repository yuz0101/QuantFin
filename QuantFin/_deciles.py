# -*- coding: utf-8 -*-
from pandas import DataFrame, DatetimeIndex, concat, qcut
from QuantFin.HandleError import InputError
from numpy import nan


def _cal_breakpoints(peak: float or int, bottom: float or int, decile: int) -> list:
    return [x/100*(peak-bottom)-bottom for x in range(int(100/decile), 100, int(100/decile))]


def _assign_port_num(_x, decile, edges):
    if _x < edges[0]:
        return 1
    elif _x >= edges[-1]:
        return decile
    else:
        for i, edge in enumerate(edges):
            if i > 0:
                if edges[i-1] <= _x < edge:
                    return i+1

def _periodic_sorting(panel_data, decile, ranking, ranking_method):
    if ranking:
        panel_data = panel_data.rank(method=ranking_method)
    peak = panel_data.max()
    bottom = panel_data.min()
    edges = _cal_breakpoints(peak, bottom, decile)
    edges.sort()
    panel_data = panel_data.apply(lambda x: _assign_port_num(x, decile, edges))
    return panel_data


def _smart_periodic_sorting(panel_data, decile, ranking=True, ranking_method='dense'):
    try:
        panel_data = qcut(panel_data, q=decile, labels=range(1, decile+1))
    except: # pylint: disable=bare-except
        panel_data = _periodic_sorting(panel_data, decile, ranking, ranking_method)
    return panel_data


def univariate_sorting(panel_data: DataFrame, sort_on: str, decile: int = 10, port_label: str = 'port', time_label: str = 'jdate', entity_label: str = 'permno', method: str = 'ranking', ranking_method='dense') -> DataFrame:
    '''This function performs univariate sorting on panel data based on a specified variable and method.

    Parameters
    ----------
    panel_data : DataFrame
        a pandas DataFrame containing panel data with columns for entity identifier, time identifier, and
    the variable to be sorted on
    sort_on : str
        The variable/column name on which the sorting needs to be performed.
    decile : int, optional
        The number of equal-sized groups to divide the data into (e.g. decile=10 would divide the data into
    10 groups).
    port_label : str, optional
        The label for the column that will contain the sorted portfolio numbers.
    time_label : str, optional
        The label for the time variable in the panel data.
    entity_label : str, optional
        The label for the entity identifier column in the panel data.
    method : str, optional
        The method parameter specifies the method to be used for sorting the data. It can take one of the
    following values: 'smart', 'qcut', 'ranking', or 'value'.
    ranking_method, optional
        The ranking_method parameter specifies the method used for assigning ranks to the data. It can take
    values such as 'dense', 'min', 'max', 'average', 'first', 'random', etc. depending on the method
    used for ranking.

    Returns
    -------
        a DataFrame.

    '''

    _d = panel_data[[entity_label, time_label, sort_on]].copy().dropna()
    if method == 'qcut':
        _d.loc[:, port_label] = _d.groupby(time_label)[sort_on].transform(
            lambda x: qcut(x, q=decile, labels=range(1, 1+decile))
        )
        _d.loc[:, port_label] = _d.loc[:, port_label].astype(int)
    elif method == 'ranking':
        _d.loc[:, port_label] = _d.groupby(time_label)[sort_on].transform(
            lambda x: _periodic_sorting(
                x, decile, ranking=True, ranking_method=ranking_method)
        )
    elif method == 'value':
        _d.loc[:, port_label] = _d.groupby(time_label)[sort_on].transform(
            lambda x: _periodic_sorting(
                x, decile, ranking=False, ranking_method=ranking_method)
        )
    elif method == 'smart':
        _d.loc[:, port_label] = _d.groupby(time_label)[sort_on].transform(
            lambda x: _smart_periodic_sorting(x, decile)
        )
    else:
        raise InputError(
            "The arg of method should be 'smart', 'qcut', 'ranking' or 'value', \
                see documentation for details."
        )
    _d = _d[[entity_label, time_label, port_label]]
    panel_data = panel_data.merge(
        _d, on=[entity_label, time_label], how='left')
    return panel_data
