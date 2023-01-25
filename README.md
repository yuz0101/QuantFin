# QuantFin
A toolkit for asset pricing.
Working........


### Get started

Momentum Effects

1) Calculating momentum effects (MOM)
2) Sorting stocks on MOM and divide samples into 10 deciles

```Python

import pandas as pd
from QuantFin import univariate_sorting, rollingGeometricReturn

# Read CRSP dataset, downloaded from WRDS
crsp = ''
crsp.columns = crsp.columns.str.lower()

"""
Sample Screens

1) The sample includes only stocks that are ordinary common share. E.g., shrcd == 10 or 11.
2) The sample includes only stocks listed on NYSE, AMEX or NASDAQ. E.g., exchcd is 1,2,3,31,32 or 33.
3) The sample includes only stocks with valid share price. E.g., prc > 0.

crsp = crsp.query("shrcd==10 or shrcd==11")
crsp = crsp.query("exchcd==1 or exchcd==31 or exchcd==2 or exchcd==32 or exchcd==3 or exchcd==33")
crsp = crsp.query('prc > 0')
"""

crsp = crsp.drop_duplicates(['date', 'permno'])
crsp = crsp.set_index(['date', 'permno'])
crsp = crsp['ret']

"""
# measure mom effects in an efficient way but ignore the requirement of minimum observations
mom = rollingGeometricReturn(mom, 11)
mom = 100*mom
"""

# measure mom effects
mom = mom + 1
mom = mom.rolling(window=11, min_periods=9).apply(pd.DataFrame.prod)
mom = 100*(mom-1)

# skip the most recent month, mom[-11, -1]
mom = mom.shift(1) 
mom = mom.unstack().rename('mom').reset_index()
mom = mom.merge(crsp, on=['permno', 'date'], how='left')

# sort stocks based on last period's mom, mom(t-1)
mom = mom.sort_values(['permno', 'date'])
mom.loc[:, 'mom(t-1)'] = mom.groupby(['permno'])['mom'].shift(1)
mom = univariate_sorting(mom, on='mom(t-1)', jdate='date', method='smart', label='port')

# mom sample data summary statistics
sample = mom.query("'1963-06-30' <= date <= '2021-12-31'")
sample.groupby(['date'])['mom'].describe().mean()
sample.groupby(['date'])['mom'].skew().mean()
sample.groupby(['date'])['mom'].apply(lambda x: x.kurt()).mean()
samp_ret = sample.groupby(['port', 'date'])['ret'].mean().unstack().T
np.log(samp_ret+1).cumsum().plot(figsize=(16,8))
```
![Momentum Portfolios Returns](momPortsRets.png)

Show the performance summary of portfolios, including mean returns and alphas(FF3 or FF5):
```python
from QuantFin import Performance
# Assume rets is a dataframe of your portfolio monthly returns with 
# column names of portfolio labels and an index of datetime (if model is specified).
samp_ret['10-1'] = samp_ret.loc[:, 10] - samp_ret.loc[:, 1]
print(Performance(samp_ret, model='FF5').summary())

                      Mean        Alpha(FF5)
Portfolio                                   
1            0.72*\n(1.77)      0.06\n(0.22)
2          0.85***\n(2.92)      0.13\n(0.88)
3          0.99***\n(3.97)     0.20*\n(1.91)
4          1.09***\n(4.88)   0.29***\n(3.66)
5          1.16***\n(5.67)   0.35***\n(6.07)
6          1.28***\n(6.46)   0.45***\n(9.80)
7          1.36***\n(6.90)  0.56***\n(12.39)
8          1.50***\n(7.38)  0.72***\n(12.84)
9          1.63***\n(7.29)  0.87***\n(11.85)
10         1.83***\n(6.57)   1.13***\n(9.88)
10-1       1.11***\n(3.69)   1.07***\n(3.45)
```
