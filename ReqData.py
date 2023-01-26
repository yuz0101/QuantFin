# -*- coding: utf-8 -*-
#import pandas_datareader.data as web

import io
import os
import tempfile
from datetime import datetime
from zipfile import ZipFile

import requests
from _io import StringIO
from bs4 import BeautifulSoup as bs
from pandas import DataFrame, read_csv, to_datetime
from pandas.tseries.offsets import BMonthEnd, BYearEnd


class KenFrenchLib:
    def __init__(self, fpath='./dataKenFrench/'):
        self.domain = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/'
        self.fpath = fpath
        if not os.path.exists(fpath):
            os.mkdir(fpath)

    def show_all(self):
        """
        Show all availiable csv file names in Database
        """
        home = 'http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html'
        res = requests.get(home)
        soup = bs(res.content, 'html.parser')
        links = soup.find_all(href=True)
        ls = ''
        for link in links:
            if 'CSV.zip' in link['href']:
                ls = ls + link['href'].split('/')[1].replace('_CSV.zip', '') + '\n'
        print(ls)
        return ls

    def _download_file(self, url):
        print('Downloading file... ...')
        res = requests.get(url, stream=True)
        return res

    def _download_zipfile(self, url):
        res = self._download_file(url)
        z = ZipFile(io.BytesIO(res.content))
        print('Got the zip file.')
        return z
    
    def _download_and_unzip_file(self, url):
        z = self._download_zipfile(url)
        print('Unzip the zip file... ...')
        z.extractall(self.fpath)
        print('Unzip done.')

    def _get_sic_codes_txt_file(self, ffind):
        try:
            fs = os.listdir(self.fpath)
            f = None
            for _f in fs:
                if _f.endswith('txt') and str(ffind) in _f:
                    f = _f
                    break
            if not f:
                print(f'Found no Fama-French {ffind} industries definition txt file')
                url = self.domain + f'Siccodes{ffind}.zip'
                self._download_and_unzip_file(url)
                fs = os.listdir(self.fpath)
                for _f in fs:
                    if _f.endswith('txt') and str(ffind) in _f:
                        f = _f
                        break
            else:
                pass
            
            if f:
                with open(self.fpath+f, 'r') as file:
                    siccodes = file.read()        
                    print(f'Fama-French {ffind} industries definition txt file Got.')     
            else:
                print(f'Found no Fama-French {ffind} industries definition txt file')
        except Exception as e:
            print(f'Exception Error: {e}')
            siccodes = None
        return siccodes
    
    def _get_sic_dict(self, siccodes: str) -> dict:
        inds = siccodes.split('\n')
        sic = 0
        sic_dict = {}
        for ind in inds:
            if len(ind) > 0:
                if not ind.startswith('          '):
                    sic = int(ind[:2])
                else:
                    _min, _max = ind.replace('          ', '').split(' ')[0].split('-')
                    for i in range(int(_min), int(_max)+1):
                        sic_dict.update({i: sic})
        
        return sic_dict
    
    def industry_ports(self, ffind: int=17) -> dict or None:
        """
        Fama-French Industry Portfolios Classified on SIC codes (merged from 
        CRSP and Compustat)

        Parameters
        ----------
        ffind : int, optional
            Fama-French Industry Portfolios. The default is 17. Options are 5,
            10, 12, 17, 30, 38, 48 and 49.            

        Returns
        -------
        dict or None
            Output is the dictionary with keys of sic codes and values of portfolio
            numbers

        """
        try:
            siccodes = self._get_sic_codes_txt_file(ffind)
            sic_dict = self._get_sic_dict(siccodes)
            sic_dict.update({9999: ffind}) # dummy for manually adjusting some industry codes as others
            print(f'Fama-French {ffind} industries SIC Codes Got.') 
        except Exception as e:
            print(f'Exception Error: {e}')
            sic_dict = None
        return sic_dict
    
    def get_factors(self, factors: str, freq: str)->DataFrame:
        """_summary_

        Args:
            factors (str): The availiable factors are 'MOM', 'FF3', 'FF5' or dataset name
            freq (str): The frequency of data, e.g., 'D' for daily, 'M' for monthly, 'W' for weekly, 'Y' for yearly, default is 'M'.

        Returns:
            DataFrame: _description_
        """

        freq = freq.lower()
        factors = factors.lower()

        if freq in ['y', 'yearly', 'year', 'annual', 'a']:
            _freq = 'annual'
        elif freq in ['month', 'm', 'monthly']:
            _freq = 'monthly'
        elif freq in ['daily', 'd', 'day']:
            _freq = 'daily'
        elif freq in ['weekly', 'w', 'week']:
            _freq = 'weekly'

        if factors == 'ff3':
            factors = 'F-F_Research_Data_Factors'
        elif factors == 'ff5':
            factors = 'F-F_Research_Data_5_Factors_2x3'
        elif factors == 'mom':
            factors = 'F-F_Momentum_Factor'
        
        if _freq in ['annual', 'monthly']:
            url = self.domain + factors + '_CSV.zip'
        else:
            url = self.domain + factors + '_' + _freq + '_CSV.zip'

        res = requests.get(url).content
        if url[-4:] == '.csv':
            string = res.decode()
        elif url[-4:] == '.zip':
            with tempfile.TemporaryFile() as tmpf:
                tmpf.write(res)
                with ZipFile(tmpf, "r") as zf:
                    string = zf.open(zf.namelist()[0]).read().decode()

        ls = string.split('\r\n\r\n')
        ds = {}
        for l in ls:
            if len(l) >= 1000:
                if l[0] == ',':
                    ds.update({0: read_csv(StringIO('date'+l))})
                if 'annual' in l.lower() or 'year' in l.lower():
                    for i, s in enumerate(l):
                        if s == ',':
                            l = l[i:]
                            ds.update({1: read_csv(StringIO('date'+l))})
                            break
                            
        if _freq == 'annual':
            data = ds[1]
        else:
            data = ds[0]
        data.set_index('date', inplace=True)
        if _freq == 'monthly':
            data.index = to_datetime(data.index, format='%Y%m') + BMonthEnd()
        elif _freq == 'annual':
            data.index = to_datetime(data.index, format='%Y') + BYearEnd()
        else:
            data.index = to_datetime(data.index, format='%Y%m%d')
        return data/100

"""
class KenFrench:
    
    def __init__(
            self, factors, freq='M',
            start_date=datetime(year=1926, month=1, day=1), 
            end_date=datetime.today()):
        '''

        Parameters
        ----------
        factors : str
            The availiable factors are 'MOM', 'FF3' or dataset name
        freq: str
            The frequency of data, e.g., 'D' for daily, 'M' for monthly,
            'W' for weekly, 'Y' for yearly, default is 'M'.
        start_date : datetime
            The start date of a sample, eg., datetime(year=1962, month=1, day=1)
        end_date : datetime
            The end date of a sample, eg., datetime(year=2020, month=5, day=30),
            The default is today's date in datetime.
        Returns
        -------
        None.

        '''
        self.freq = freq.lower()
        
        if freq.lower() == 'w':
            _freq = '_weekly'
        elif freq.lower() == 'd':
            _freq = '_daily'
        else:
            _freq = ''
        
        if factors.lower() == 'mom':    
            self.topic = 'F-F_Momentum_Factor' + _freq
        elif factors.lower() == 'ff3':
            self.topic = 'F-F_Research_Data_Factors' + _freq
        elif factors.lower() == 'ff5':
            self.topic = 'F-F_Research_Data_5_Factors_2x3' + _freq
        else:
            self.topic = factors
        self.start_date = start_date
        self.end_date = end_date
        self.data_dict = self._retreive_data()
        self.data = self.get_data()
        self.des = self.get_data_des()

    def _retreive_data(self):
        data_dict = web.DataReader(
            self.topic, 'famafrench', self.start_date, self.end_date)    
        return data_dict
    
    def get_data(self):
        if self.freq == 'y':
            df = self.data_dict.get(1)/100
        else:
            df = self.data_dict.get(0)/100
        if self.freq != 'd' and self.freq != 'w':
            df.index = df.index.to_timestamp() + BMonthEnd()
        return df
    
    def get_data_des(self):
        data_descr = self.data_dict.get('DESCR')
        return data_descr
"""