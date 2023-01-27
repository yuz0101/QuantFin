# -*- coding: utf-8 -*-
from numpy import ones
from pandas import DataFrame, DatetimeIndex, concat, qcut

from QuantFin._deciles import *
from QuantFin.HandleError import InputError
from QuantFin.Regression import OLS
from QuantFin.ReqData import KenFrenchLib

class Performance:

    def __init__(self, data: DataFrame, freq: str = 'M', model: str = 'FF3', capm: bool = True,
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
        if type(data.index) is not DatetimeIndex:
            if model != None:
                raise InputError(
                    "The Input dataset's index should be DatetimeIndex if model is indicated. Otherwise, please set model to None"
                    )
        self.df = data
        self.model = model
        if freq.lower() in ['d', 'day', 'daily']:
            self.freq = 'D'
            self.annFactor = 252
        elif freq.lower() in ['m', 'month', 'monthly']:
            self.freq = 'M'
            self.annFactor = 12
        elif freq.lower() in ['y', 'year', 'yearly']:
            self.freq = 'Y'
            self.annFactor = 1
        else:
            raise InputError(
                "The arg of 'freq' should be either 'D' for daily, 'M' for monthly or 'Y' for yearly"
            )
        self.datename = datename
        self.capm = capm

    def _get_factor_data(self):
        #_f = KenFrench(self.model, self.freq).get_data()
        _f = KenFrenchLib().get_factors(factors=self.model, freq=self.freq)
        _f.index = _f.index.rename(self.datename)
        try:
            _f = _f[_f.columns.drop('RF')]
        except:
            pass
        return _f

    def stats(self, ys, x, param, percentage, decimal, annualise, **args):
        _tp = ys.apply(lambda y: OLS(y, x, **args).stats(param))
        _m = _tp.iloc[0, :]
        if percentage:
            _m = _m*100
        if annualise:
            _m = _m*self.annFactor
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

    def summary(self, percentage: bool = True, decimal: int = 2, annualise: bool=False, **args) -> DataFrame:
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
        _t = self.stats(self.df, ones(len(self.df)), 'const', 
                        percentage, decimal, annualise, **args)
        _t = _t.rename(f'{label_ann}Mean{label_pct}').to_frame()

        if self.model:
            _f = self._get_factor_data()
            self.df = concat([self.df, _f], axis=1, join='inner')
            _ta = self.stats(
                self.df[_l], 
                self.df[_f.columns], 'const', percentage, decimal, annualise, **args)
            _ta = _ta.rename(f'{label_ann}Alpha({self.model}){label_pct}')
            _t = concat([_t, _ta], axis=1)
        
        if self.capm:
            _ta = self.stats(
                self.df.loc[:, _l], 
                self.df.loc[:, 'Mkt-RF'], 'const', percentage, decimal, annualise, **args)
            _ta = _ta.rename(f'{label_ann}Alpha(CAPM){label_pct}')
            _t = concat([_t, _ta], axis=1)          

        _t.index = _t.index.rename('Portfolio')
        return _t
