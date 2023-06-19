# -*- coding: utf-8 -*-

import io
import os
import tempfile
from zipfile import ZipFile

import requests
from _io import StringIO
from bs4 import BeautifulSoup as bs
from pandas import DataFrame, read_csv, read_excel, to_datetime
from pandas.tseries.offsets import BMonthEnd, BYearEnd

from QuantFin.HandleError import InputError


class Req:
    def __init__(self, fpath='./dataLib/'):
        self.fpath = fpath
        if not os.path.exists(fpath):
            os.mkdir(fpath)
    
    def _download_file(self, url, name=''):
        print(f'Downloading file {name}')
        res = requests.get(url, stream=True)
        return res

    def _download_zipfile(self, url):
        res = self._download_file(url)
        z = ZipFile(io.BytesIO(res.content))
        return z
    
    def _download_store_unzip_file(self, url):
        z = self._download_zipfile(url)
        z.extractall(self.fpath)
        print('File unzipped and stored in ./dataLib ')
    
    def _download_store_excel(self, url, name):
        res = self._download_file(url, name)
        with open(self.fpath+name, 'wb') as f:
            f.write(res.content)
        return res
    
    def _download_store_csv(self, url, name):
        res = self._download_file(url, name)
        res = requests.get(url)
        df = read_csv(StringIO(res.content.decode()))
        df.to_csv(self.fpath+name)
        return df
    
    def _download_store_txt(self, url, filename):
        string = self._download_file(url, filename).text
        with open(self.fpath+filename, 'w', encoding="utf-8") as f:
            f.write(string)
        return string
    

class KenFrenchLib(Req):
    """This a class for downloading factor data from Ken.French (http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)
    """
    def __init__(self):
        super().__init__()
        self.domain = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/'

    def show_all(self) -> list:
        """This is a function for showing all avaiable factor sets.

        Returns:
            list: this is a list of names for all factor sets listed on Ken.French data library. 
        """
        home = 'http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html'
        res = requests.get(home)
        soup = bs(res.content, 'html.parser')
        links = soup.find_all(href=True)
        ls = ''
        namelist = []
        for link in links:
            if 'CSV.zip' in link['href']:
                ls = ls + link['href'].split('/')[1].replace('_CSV.zip', '') + '\n'
                namelist.append(link['href'].split('/')[1].replace('_CSV.zip', ''))
        print(ls)
        return namelist

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
                self._download_store_unzip_file(url)
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
    
    def get_factors(self, factors: str, freq: str) -> DataFrame:
        """This is a fucntion for getting a factor data from Ken.French Lib. 

        Args:
            factors (str): Factor name. Options are 'MOM', 'FF3', 'FF5' or other dataset names.
                'MOM': Momentum factor data for USA market.
                'FF3': Factors of SIZE (SMB), VALUE(HML) and Market risk premium(Rm-Rf) for USA markets.
                'FF5': Factors of SMB, HML, Rm-Rf, RMW and CMA for USA markets.
                other dataset names can be found by using function of "show_all()".

            freq (str): Indicate the frequency of data, e.g., 'D' for daily, 'M' for monthly, 'W' for weekly, 'Y' or 'A' for annual, default is 'M'.

        Returns:
            DataFrame: A dataframe of factors data with column labels of factor names and an index of datetime in business day format.
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
        else:
            raise InputError(
                "Incorrect frequency level. Options are 'ANNUAL', 'WEEKLY', 'DAILY', 'MONTHLY'"
            )

        if factors == 'ff3':
            factors = 'F-F_Research_Data_Factors'
        elif factors == 'ff5':
            factors = 'F-F_Research_Data_5_Factors_2x3'
        elif factors == 'mom':
            factors = 'F-F_Momentum_Factor'
        else:
            raise InputError(
                "Incorrect factor name. Options are 'MOM', 'FF3', 'FF5' or other specific dataset names listed on site."
            )
        
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

class ZhiDaLib(Req):
    """This is a class for downloading data from Zhi Da's personal website.
    """
    def __init__(self):
        super().__init__()
        self.domain = 'https://www3.nd.edu/~zda/'

    def get_pear_index(self, update: bool=False, filename: str='PEAR.xlsx') -> DataFrame:
        """This is a function for getting PEAR index data. Please see the reference for details. Chen, Z., Da, Z., Huang, D. and Wang, L. (2023). Presidential economic approval rating and the cross-section of stock returns. Journal of Financial Economics, 147(1), pp.106-131.
        
        Args:
            update (bool, optional): Indicate if update the stored file. Defaults to False.
        
        Returns:
            DataFrame: This is a dataframe of pear index data with column label of 'PEAR' and a monthly datetime index in the business day format.
        """
        
        if update:
            self._download_store_excel(self.domain+filename, filename)
        if os.path.exists(self.fpath+filename):
            df = read_excel(self.fpath+filename, sheet_name='DATA')
        else:
            res = self._download_store_excel(self.domain+filename, filename)
            df = read_excel(res.content, sheet_name='DATA')
        df = df.set_index('yearmonth')
        df.index = to_datetime(df.index, format='%Y%m').rename('date') + BMonthEnd()
        return df
    
    def get_fear_index(self, update: bool=False, filename='fears_post_20140512.csv') -> DataFrame:
        """This is a function for getting PEAR index data. Please see the reference for details. Da, Z., Engelberg, J., & Gao, P. (2015). The sum of all FEARS investor sentiment and asset prices. The Review of Financial Studies, 28(1), 1-32.

        Args:
            update (bool, optional): Indicate if update the stored file. Defaults to False.
            filename (str, optional): Indicate the filename. Defaults to 'fears_post_20140512.csv'.

        Returns:
            DataFrame: DataFrame: This is a dataframe of pear index data with column label of 'FEAR' and a datetime index.
        """
        if update or not os.path.exists(self.fpath+filename):
            df = self._download_store_csv(self.domain+filename, filename)
        else:
            df = read_csv(self.fpath+filename)
        df.set_index('date', inplace=True)
        df.index = to_datetime(df.index, format='%m/%d/%Y')
        return df

    def get_nat_data(self, filename='nat.txt') -> DataFrame:
        """This is a function for getting NAT data. Please see the reference for details. Chen, Y., Da, Z., & Huang, D. (2019). Arbitrage trading: The long and the short of it. The Review of Financial Studies, 32(4), 1608-1646.

        Args:
            filename (str, optional): Indicate the filename. Defaults to 'nat.txt'.

        Returns:
            DataFrame: This is a dataframe of pear index data with column label of 'NAT' and a datetime index
        """
        string = self._download_store_txt(self.domain+filename, filename)
        string = string.split('\r\n\r\n')[4].replace('\t\t','\t')
        df = read_csv(StringIO(string), sep='\t')
        df.columns = df.columns.str.lower()
        df.date = to_datetime(df.date, format='%Y%m%d')
        return df
