# -*- coding: utf-8 -*-

from numpy import nan
import statsmodels.api as sm
from pandas import concat, DataFrame

class OLS:
    """
    developing
    """

    def __init__(self, y, x, constant=True, **args):
        if constant:
            x = sm.add_constant(x)
        self.mod = sm.OLS(y, x).fit(**args)

    def stats(self, param):
        return self.mod.params[param], self.mod.tvalues[param], self.mod.pvalues[param]

    def r2(self):
        return self.mod.rsquared_adj

def add_(x):
    if x != '':
        return f"({x})"
    else:
        return ""

def ols_regs(formulas, data):
    stats = []
    rsquared_adjs = []
    nobss = []
    for colname in formulas.keys():
        formula = formulas[colname]
        if 'if' in formula:
            formula, condition = formula.replace(' ', '').split(',if')
            model = sm.OLS.from_formula(formula, data=data.query(condition)).fit(cov_type='HAC', cov_kwds={'maxlags':6})
        else:
            model = sm.OLS.from_formula(formula, data=data).fit(cov_type='HAC', cov_kwds={'maxlags':6})
        stat = concat([model.params, model.tvalues, model.pvalues], axis=1)
        stat.columns = ['coef', 'tvalue', 'pvalue']
        stat = stat.unstack().rename(colname)
        stats.append(stat)
        rsquared_adjs.append(model.rsquared_adj)
        nobss.append(model.nobs)
    stats = concat(stats, axis=1)
    stats = stats.sort_index()

    stats[stats.loc[['pvalue'], :]<=0.01] = 3
    stats[(stats.loc[['pvalue'], :]<=0.05)&(stats.loc[['pvalue'], :]>0.01)] = 2
    stats[(stats.loc[['pvalue'], :]<=0.10)&(stats.loc[['pvalue'], :]>0.05)] = 1
    stats[stats.loc[['pvalue'], :]<1] = nan
    stats.loc[['pvalue'], :] = stats.loc[['pvalue'], :].fillna(0)
    stats.loc[['pvalue'], :] = stats.loc[['pvalue'], :].applymap(lambda x:  int(x)*'*')
    stats.loc[['coef'], :] *= 100

    stats.loc[['coef', 'tvalue'], :] = stats.loc[['coef', 'tvalue'], :].applymap(lambda x: format(x, ".2f"))
    stats = stats.replace("nan", "")
    df = stats.loc['coef', :] + stats.loc['pvalue', :]
    df.index = stats.loc[['coef'], :].index
    stats.loc[['coef'], :] = df
    stats = stats.drop(index='pvalue')
    stats = stats.swaplevel().sort_index()
    stats = concat([stats, DataFrame({('Adj R2 (%)',''): rsquared_adjs, ('Obs',''):nobss}, index=stats.columns).T])

    stats.loc[['Adj R2 (%)'], :] = (stats.loc[['Adj R2 (%)'], :]*100).applymap(lambda x: format(x, ".2f"))
    stats.loc[['Obs'], :] = stats.loc[['Obs'], :].astype(int)
    stats.loc[(slice(None), 'tvalue'), :] = stats.loc[(slice(None), 'tvalue'), :].apply(lambda x: x.apply(lambda y: add_(y)))
    return stats