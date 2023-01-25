# -*- coding: utf-8 -*-
import pandas_datareader.data as web
from pandas.tseries.offsets import BMonthEnd
from datetime import datetime
from zipfile import ZipFile
from bs4 import BeautifulSoup as bs
import requests
import io
import os

class KenFrenchLib:
    def __init__(self):
        self.domain = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/'

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
                ls = ls + link['href'].split('/')[1] + '\n'
        print(ls)

    def _download_file(self, url):
        print('Downloading file... ...')
        res = requests.get(url, stream=True)
        return res

    def _download_zipfile(self, fpath, url):
        res = self._download_file(url)
        z = ZipFile(io.BytesIO(res.content))
        print('Got the zip file.')
        return z
    
    def _download_and_unzip_file(self, fpath, url):
        z = self._download_zipfile(fpath, url)
        print('Unzip the zip file... ...')
        z.extractall(fpath)
        print('Unzip done.')
    
    def _get_sic_codes_txt_file(self, fpath, ffind):
        try:
            fs = os.listdir(fpath)
            f = None
            for _f in fs:
                if _f.endswith('txt') and str(ffind) in _f:
                    f = _f
                    break
            if not f:
                print(f'Found no Fama-French {ffind} industries definition txt file')
                url = self.domain + f'Siccodes{ffind}.zip'
                self._download_and_unzip_file(fpath, url)
                fs = os.listdir(fpath)
                for _f in fs:
                    if _f.endswith('txt') and str(ffind) in _f:
                        f = _f
                        break
            else:
                pass
            
            if f:
                with open(fpath+f, 'r') as file:
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
    
    def industry_ports(self, fpath: str, ffind: int=17) -> dict or None:
        """
        Fama-French Industry Portfolios Classified on SIC codes (merged from 
        CRSP and Compustat)

        Parameters
        ----------
        fpath : str
            The path to store and read the industry-portfolio-classification 
            definition.
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
            siccodes = self._get_sic_codes_txt_file(fpath, ffind)
            sic_dict = self._get_sic_dict(siccodes)
            sic_dict.update({9999: ffind}) # dummy for manually adjusting some industry codes as others
            print(f'Fama-French {ffind} industries SIC Codes Got.') 
        except Exception as e:
            print(f'Exception Error: {e}')
            sic_dict = None
        return sic_dict

    """
    Coding........
    def factors(self, fpath, filename):
        url = self.domain + filename
        f = self._download_and_unzip_file(fpath, url)
        fs = os.listdir(fpath)
        for f in fs:
            if '.csv' in f.lower():
                df = read_csv(fpath+f)
        return df
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