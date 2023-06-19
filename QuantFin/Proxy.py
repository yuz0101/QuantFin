# -*- coding: utf-8 -*-
from numpy import exp, log, nan
from pandas import (DataFrame, Series, concat, merge, qcut, read_csv,
                    to_datetime)
from pandas.tseries.offsets import BMonthEnd


class Lottery:

    def max_ret(self,
                data_set: DataFrame, 
                entity: str, 
                date: str, 
                on: str, 
                maxn: int) -> DataFrame:
        """
        A function for generating the MAX signals, which are the maximum daily returns 
        within a month.

        Parameters
        ----------
        data_set : DataFrame
            A panel data dataframe in a frequency of daily level. Columns 
            should have names of entity, date and daily return. The index of it
            should be a range index. Note that columns of date should be in 
            datetime index
        entity : str
            Name of entity. e.g. 'permno' in CRSP dataset.
        date : str
            Name of date. e.g. 'date' in CRSP dataset.
        on : str
            Name of return. e.g. 'ret' in CRSP dataset.
        maxn : int
            The amount of the largest values that would be encounted into
            maxmium signals. e.g. The function would return values of 
            max1 ~ max5 based on maxn of 5.

        Returns
        -------
        df : DataFrame
            A panel data dataframe in a monthly frequency. Column names would 
            be entity, date, jdate, maxn_date and maxn_ret. Noted that index 
            would be a range index rather than multi-index of entity and jdate.
        """
        try:
            _temp_set = data_set[[entity, date, on]]\
                .sort_values([entity, date])
            _temp_set.loc[:, 'jdate'] = _temp_set.loc[:, date]\
                .dt.to_period('M').dt.to_timestamp() + BMonthEnd()
            _max_set = _temp_set.groupby([entity, 'jdate'])[[date, on]]\
                .apply(lambda x:x.nlargest(maxn, columns=on)).reset_index()
            del _temp_set
            df = DataFrame()
            for i in range(maxn):
                _max_ = _max_set.groupby([entity, 'jdate'])[[date, on]].nth(i)\
                .rename(columns={date:f'max{i+1}_date', on:f'max{i+1}_ret'})
                df = concat([df, _max_], axis=1)
                del _max_
            return df.reset_index()
        except Exception as e:
            print(e)
    
    def skewexp(self):
        pass

    def ivol(self):
        pass

    def prc(self):
        pass

    def jackpotp(self):
        pass

class Momentum:
    def cross_sectional_mom(self):
        pass

    def time_series_mom(self):
        pass

class Illquidity:
    pass

class Turnover:
    pass

class BookToMarketRatio:
    pass

