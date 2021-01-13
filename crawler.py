# This script will download all the 10-K, 10-Q and 8-K
# provided that the company symbol and its cik code are correctly input. 
# Else it will raise exceptions as defined in the module execptions.py 

#from __future__ import print_function

import requests
import os
import errno
from bs4 import BeautifulSoup
import datetime
from exceptions import EDGARQueryError, CIKError
import operate
#from lxml import html
#import xml.etree.ElementTree as ET


DEFAULT_DATA_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'SEC-Edgar-Data'))


class SecCrawler(object):    #Main class for data search, retreival and storage 

    def __init__(self, data_path=DEFAULT_DATA_PATH):
        self.data_path = data_path
        print("Path of the directory where data will be saved: " + self.data_path)

    def __repr__(self):
        return "SecCrawler(data_path={0})".format(self.data_path)

    def _make_directory(self, company_code, cik, priorto, filing_type):
        # Making the directory to save company filings
        path = os.path.join(self.data_path, company_code, cik, filing_type)

        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise

    def _save_in_directory(self, company_code, cik, priorto, filing_type, docs):
        # Save every text document into its respective folder
        for (url, doc_name) in docs:
            r = requests.get(url)
            data = r.text      #(data = string type) 
#            data = data.encode('utf8','ignore')
             
#            tree = ET.fromstring(r.content)
#            print()
##            print(tree)
#            for line in r.text.splitlines():
#                print (line)
            
            data1 = operate.clean_data(data)
                        
            path = os.path.join(self.data_path, company_code, cik,
                                filing_type, doc_name)

            with open(path, "ab") as f:
                f.write(data1.encode('ascii', 'ignore'))
#            with open(path, "w") as f:
#                for item in data1:
#                    f.write("%s\n" % item)
#                f.write(data1.encode('ascii', 'ignore'))
#                                f.write(data1)
        
                
#    def _one_file(self, name):
#        new_path = DEFAULT_DATA_PATH + "/AAPL/0000320193/10-k/"
#        c_path = os.path.join(self.data_path, name)
#        
#        str1 = os.listdir(new_path)
#                
#        for i in str1:
#            f = open(new_path + i)
#            f2 = open(c_path, "a")
#            for line in f.readlines():
#                f2.write(line)
#        return (c_path)
                
    def _one_file(self, name):
        new_path = DEFAULT_DATA_PATH + "/AAPL/0000320193/10-k/"
        c_path = os.path.join(self.data_path, name)
        
        str1 = os.listdir(new_path)
                
        for i in str1:
            f = open(new_path + i)
            f2 = open(c_path, "a")
            for line in f.readlines():
                f2.write(line)
        return (c_path)            

    @staticmethod
    def _create_document_list(data):
        # parse fetched data using beautifulsoup
        # Explicit parser needed
        soup = BeautifulSoup(data, features='html.parser')
        # store the link in the list
        link_list = [link.string for link in soup.find_all('filinghref')]

        print("Number of files to download: {0}".format(len(link_list)))
        print("Starting download...")

        # List of url to the text documents
        txt_urls = [link[:link.rfind("-")] + ".txt" for link in link_list]
        # List of document doc_names
        doc_names = [url.split("/")[-1] for url in txt_urls]

        return list(zip(txt_urls, doc_names))

    @staticmethod
    def _sanitize_date(date):
        if isinstance(date, datetime.datetime):
            return date.strftime("%Y%m%d")
        elif isinstance(date, str):
            if len(date) != 8:
                raise TypeError('Date must be of the form YYYYMMDD')
        elif isinstance(date, int):
            if date < 10**7 or date > 10**8:
                raise TypeError('Date must be of the form YYYYMMDD')

    @staticmethod
    def _check_cik(cik):
        invalid_str = isinstance(cik, str) and len(cik) != 10
        invalid_int = isinstance(cik, int) and not (999999999 < cik < 10**10)
        invalid_type = not isinstance(cik, (int, str))
        if invalid_str or invalid_int or invalid_type:
            raise CIKError(cik)
        else:
            return cik

    def _fetch_report(self, company_code, cik, priorto, count, filing_type):
        priorto = self._sanitize_date(priorto)
        cik = self._check_cik(cik)
        self._make_directory(company_code, cik, priorto, filing_type)

        # generate the url to crawl
        base_url = "http://www.sec.gov/cgi-bin/browse-edgar"
        params = {'action': 'getcompany', 'owner': 'exclude', 'output': 'xml',
                  'CIK': cik, 'type': filing_type, 'dateb': priorto, 'count': count}
        print("started {filing_type} {company_code}".format(
            filing_type=filing_type, company_code=company_code))
        r = requests.get(base_url, params=params)
        if r.status_code == 200:
            data = r.text
#            tree = html.fromstring(r.content)
            # get doc list data
            docs = self._create_document_list(data)

            try:
                self._save_in_directory(
                    company_code, cik, priorto, filing_type, docs)
            except Exception as e:
                print(str(e))
        else:
            raise EDGARQueryError(r.status_code)
        
#        combined_file = 'combined.txt'
#        path_to_consolidated_file = self._one_file(combined_file)
#        return path_to_consolidated_file

            
        
    def filing_10Q(self, company_code, cik, priorto, count):
        path = self._fetch_report(company_code, cik, priorto, count, '10-Q')
        return path

    def filing_10K(self, company_code, cik, priorto, count):
#        path = self._fetch_report(company_code, cik, priorto, count, '10-K')
#        return path
        self._fetch_report(company_code, cik, priorto, count, '10-K')

    def filing_8K(self, company_code, cik, priorto, count):
        path = self._fetch_report(company_code, cik, priorto, count, '8-K')
        return path

    def filing_13F(self, company_code, cik, priorto, count):
        path = self._fetch_report(company_code, cik, priorto, count, '13-F')
        return path

    def filing_SD(self, company_code, cik, priorto, count):
        path = self._fetch_report(company_code, cik, priorto, count, 'SD')
        return path

    def filing_4(self, company_code, cik, priorto, count):
        path = self._fetch_report(company_code, cik, priorto, count, '4')
        return path
