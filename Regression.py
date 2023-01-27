# -*- coding: utf-8 -*-
import statsmodels.api as sm
from linearmodels import (BetweenOLS, FamaMacBeth, FirstDifferenceOLS,
                          PanelOLS, PooledOLS)
from linearmodels.panel import compare


class OLS:

    def __init__(self, y, x, constant=True, **args):
        if constant:
            x = sm.add_constant(x)
        self.mod = sm.OLS(y, x).fit(**args)
    
    def stats(self, param):
        return self.mod.params[param], self.mod.tvalues[param], self.mod.pvalues[param]

    def r2(self):
        return self.mod.rsquared_adj


class Panel:
    
    def __init__(self, df, entity, date, formula):
        '''
        
        Parameters
        ----------
        df : pd.DataFrame
            The panel data with columns of entity, date, dependent variable and 
            independent variables. 
        entity : str
            The column name of entity, eg., 'permno', which is the
            permanent number of a security in CRSP database.
        date : str
            The column name of date, eg., 'date'.
        formula : str
            The regression model, eg., 'return ~ 1 + mkt + mom + smb + hml'.

        '''
        if df.index.names != [entity, date]:
            self.df = df.set_index([entity, date])
        else:
            self.df = df
        self.entity = entity
        self.date = date
        self.formula = formula
    
    def _reg(self, estimator, **args):
        mod = estimator.from_formula(self.formula, self.df)
        reg = mod.fit(**args)
        return reg

    def fmb(self, **args):
        return self._reg(FamaMacBeth, **args)

    def fe(self, **args):
        return self._reg(PanelOLS, **args)

    def btw(self, **args):
        return self._reg(BetweenOLS, **args)

    def fd(self, **args):
        return self._reg(FirstDifferenceOLS, **args)

    def pool(self, **args):
        return self._reg(PooledOLS, **args)
