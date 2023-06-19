# -*- coding: utf-8 -*-
from numpy import ones, nan
from pandas import DataFrame, DatetimeIndex, concat, qcut

from QuantFin._deciles import *
from QuantFin.HandleError import InputError
from QuantFin._regression import OLS
from QuantFin.ReqData import KenFrenchLib


class Performance:

    def __init__(self, data: DataFrame, freq: str = 'M', models: list = ['CAPM', 'FF3', 'FF4'],
                 datename: str = 'date'):
        """
        Parameters
        ----------
        df: DataFrame
            A DataFrame of portfolios returns with columns labels of portfolio 
            names and an index of datetime.

        freq: str
            The frequency of returns. Optional frequencies are monthly(M),
            daily(D) and yearly(Y). Default is 'M'.

        model: str
            Indicate the benchmark asset pricing models for estimating the 
            alpha. It regresses portfolios returns on factors. Optional 
            models are None (for not estimating alpha), Fama-French-3 factor (FF3), 
            Fama-French-5 factor (FF5), and FF3 + MOM (FF4). Default is FF3.

        datename: str
            Indicate the name of datetime index. Default is 'date'

        capm: bool
            Indicate if CAPM model applied

        """
        if not isinstance(data.index, DatetimeIndex):
            if models is not None:
                raise InputError(
                    "The Input dataset's index should be DatetimeIndex if model is indicated. Otherwise, please set model to None"
                )
        self.df = data
        self.models = models
        if freq.lower() in ['d', 'day', 'daily']:
            self.freq = 'D'
            self.ann_fac = 252
        elif freq.lower() in ['m', 'month', 'monthly']:
            self.freq = 'M'
            self.ann_fac = 12
        elif freq.lower() in ['y', 'year', 'yearly']:
            self.freq = 'Y'
            self.ann_fac = 1
        else:
            raise InputError(
                "The arg of 'freq' should be either 'D' for daily, 'M' for monthly or 'Y' for yearly"
            )
        self.datename = datename

    def _get_factor_data(self, model):
        if model.lower() == 'ff4':
            _f = KenFrenchLib().get_factors(factors='FF3', freq=self.freq)
            _mom = KenFrenchLib().get_factors(factors='MOM', freq=self.freq)
            _f = _f.merge(_mom, right_index=True, left_index=True, how='inner')
        else:
            _f = KenFrenchLib().get_factors(factors=model, freq=self.freq)
        _f.index = _f.index.rename(self.datename)
        try:
            _f = _f[_f.columns.drop('RF')]
        except:  # pylint: disable=bare-except
            pass
        return _f

    def _stats(self, ys, x, param, percentage, decimal, annualise, **args):
        _tp = ys.apply(lambda y: OLS(y, x, **args).stats(param))
        _m = _tp.iloc[0, :]
        if percentage:
            _m = _m*100
        if annualise:
            _m = _m*self.ann_fac
        _m = _m.apply(lambda x: format(x, '.2f'))
        _t = _tp.iloc[1, :].apply(
            lambda x: '\n('+format(x, f'.{decimal}f')+')')
        _pv = _tp.iloc[2, :]
        _pv = _pv.mask(_pv <= .01, 3)
        _pv = _pv.mask(_pv <= .05, 2)
        _pv = _pv.mask(_pv <= .10, 1)
        _pv = _pv.mask((_pv > .10) & (_pv < 1), 0)
        _pv = _pv.apply(lambda x: int(x)*'*')
        _tp = _m + _pv + _t
        return _tp

    def summary(self, percentage: bool = True, decimal: int = 2, annualise: bool = False, **args) -> DataFrame:
        """
        It reports the summary statistics of portfolios performance, including 
        mean returns and t-values, standard factor models'alpha and relative
        t-values. 

        Parameters
        ----------
        percentage: bool
        It indicates if returns in the summary table is in percentage, 
        including alphas. Default is True

        decimal: int
        It indicates the decimals in this summary table would be kept.
        Default is 2.

        annualise: bool
        It indicates if annulise coefficients. Default is False.

        args:
        All arguments related to the statsmodel.api.OLS.fit are applied
        here. e.g., cov_type='HAC', cov_kwds={'maxlags':6} for 
        Newey-West adjust t-statistics.

        Returns
        -------
        summary: DataFrame
        """
        if percentage:
            label_pct = ' (%)'
        else:
            label_pct = ''
        if annualise:
            label_ann = 'Annualised '
        else:
            label_ann = ''

        _l = self.df.columns  # get all portfolio-label names
        _t = self._stats(self.df, ones(len(self.df)), 'const',
                         percentage, decimal, annualise, **args)
        _t = _t.rename(f'{label_ann}Mean{label_pct}').to_frame()

        if self.models:
            for model in self.models:
                if model.lower() == 'capm':
                    _ta = self._stats(
                        self.df.loc[:, _l], self.df.loc[:, 'Mkt-RF'], 'const', percentage, decimal, annualise, **args)
                    _ta = _ta.rename(f'{label_ann}Alpha(CAPM){label_pct}')
                    _t = concat([_t, _ta], axis=1)
                else:
                    _f = self._get_factor_data(model)
                    self.df = concat([self.df, _f], axis=1, join='inner')
                    _ta = self._stats(
                        self.df[_l], self.df[_f.columns], 'const', percentage, decimal, annualise, **args)
                    _ta = _ta.rename(f'{label_ann}Alpha({model}){label_pct}')
                    _t = concat([_t, _ta], axis=1)

        _t.index = _t.index.rename('Portfolio')
        return _t


def cal_portfolio_returns(panel_data: DataFrame, ret_label: str, time_label: str, port_label: str = None, weight_on: str = None) -> DataFrame:
    '''This function calculates portfolio returns based on input data and specified parameters.
    
    Parameters
    ----------
    panel_data : DataFrame
        a pandas DataFrame containing the data for the portfolio
    ret_label : str
        The label of the column in the panel_data DataFrame that contains the returns data.
    time_label : str
        The name of the column in the panel_data DataFrame that represents the time period of each
    observation.
    port_label : str
        The label for the portfolio column in the output DataFrame. If not provided, the function will
    return a Series instead of a DataFrame.
    weight_on : str
        The column name of the weights to be used for calculating value-weighted returns.
    
    Returns
    -------
        a DataFrame that calculates portfolio returns based on the input parameters. The returned DataFrame
    contains the portfolio returns grouped by the specified time and portfolio labels. If a weight label
    is specified, the portfolio returns are calculated using value-weighted returns.
    
    '''
    _l = [time_label]
    if port_label:
        _l = [port_label] + _l
    if weight_on:
        panel_data = panel_data[[ret_label, weight_on] + _l]
        panel_data[weight_on] = panel_data[ret_label] / \
            panel_data[ret_label] * panel_data[weight_on]
        value_weight = panel_data.groupby(_l)[weight_on]\
            .sum().rename('vw').reset_index()
        panel_data = panel_data.merge(value_weight, on=_l, how='left')
        panel_data['vw'] = panel_data[weight_on] / \
            panel_data['vw'] * panel_data[ret_label]
        if port_label:
            return panel_data.groupby(_l)['vw'].sum().unstack().T.replace(0, nan)
        else:
            return panel_data.groupby(_l)['vw'].sum().replace(0, nan)
    else:
        panel_data = panel_data[[ret_label] + _l]
        if port_label:
            return panel_data.groupby(_l)[ret_label].mean().unstack().T
        else:
            return panel_data.groupby(_l)[ret_label].mean()
