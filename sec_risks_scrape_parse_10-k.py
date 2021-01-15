import requests
import os
from bs4 import BeautifulSoup
import errno
import datetime
import argparse
import time
import re
from tqdm import trange
import pandas as pd
from nltk import word_tokenize
from nltk.corpus import stopwords


class EDGARQueryError(Exception):
    """
    This error is thrown when a query receives a response that is not a 200 response.
    """

    def __init__(self, response):
        self.response = response

    def __str__(self):
        return "An error occured while making the query. Received {response} response".format(
            response=self.response
        )


class EDGARFieldError(Exception):
    """
    This error is thrown when an invalid field is given to an endpoint.
    """

    def __init__(self, endpoint, field):
        self.endpoint = endpoint
        self.field = field

    def __str__(self):
        return "Field {field} not found in endpoint {endpoint}".format(
            field=self.field, endpoint=self.endpoint
        )


class CIKError(Exception):
    """
    This error is thrown when an invalid CIK is given.
    """

    def __init__(self, cik):
        self.cik = cik

    def __str__(self):
        return "CIK {cik} is not valid. Must be str or int with 10 digits.".format(cik=self.cik)


default_data_path = os.path.abspath("~/SEC/SEC-company-data")

def clean_data(data):
    data = data.lower()  

#    removing the html tags from data
    clean = re.compile(r'<(.|\s)*?>')
    new_data = re.sub(clean,' ', data)

    new_data = new_data.replace('&#8217;',"'").replace('&#39;', "'")

#    removing the &#; from data
    clean = re.compile(r'&#.*?;')
    new_data = re.sub(clean,' ', new_data)

#    removing the &nbsp; from data
    clean = re.compile(r'&nbsp;')
    new_data = re.sub(clean,' ', new_data)

#    keeping the string between the two Item 1A. and Item 1B.   
    data1 = re.findall(r"item 1a\.(.+?)item 1b\.",new_data, re.S)
    new_data1 = " ".join(data1)

#    keeping the string between the two Item 7. and Item 8.   
    data2 = re.findall(r"item 7a\.(.+?)item 8\.",new_data, re.S)
    new_data2 = " ".join(data2)

    new_data = new_data1 + new_data2

#    removing the \ss\s from data
    clean = re.compile(r'\ss\s')
    new_data = re.sub(clean,' ', new_data)

    new_data = " ".join(new_data.strip().split())
    
    return (new_data)


class SecCrawler(object):

    def __init__(self, data_path=default_data_path):
        self.data_path = data_path
        print("Directory where reports are stored:  " + self.data_path)

    def __repr__(self):
        return "SecCrawler(data_path{0})".format(self.data_path)

    def __str__(self):
        return "SecCrawler(data_path{0})".format(self.data_path)


    def _make_directory(self, company_code, cik, priorto, filing_type):
        # path = os.path.join(self.data_path, company_code, cik, filing_type)
        path = os.path.join(self.data_path, company_code)

        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as Exception:
                if Exception.errno != errno.EEXIST:
                    raise


    def _save_in_directory(self, company_code, cik, priorto, filing_type, docs):
        # Save every text document into its respective folder
        for (url, doc_name) in docs:
            r = requests.get(url)
            data = r.text
            data1 = clean_data(data)
            # data1 = data 

            # path = os.path.join(self.data_path, company_code, cik,
            #                     filing_type, doc_name)
            path = os.path.join(self.data_path, company_code, doc_name)

            with open(path, "ab") as f:
                f.write(data1.encode('ascii', 'ignore'))


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
        

def get_filings(a,b,c,d):
    t1 = time.time()
    seccrawler = SecCrawler() # creating object crawler from class SecCrawler()
    
    companyCode = a    #company code for Apple Inc
    cik = b      #cik code for Apple Inc
    date = c       #date from which filings should be downloaded
    count = d            # number of filings to be downloaded, at minimum 10 entries by EDGAR
    
#   Crawling, creating consolidated file, returning path to consolidated file
#    path = seccrawler.filing_10K(companyCode, cik, date, count)
    seccrawler.filing_10K(companyCode, cik, date, count)

    print("Successfully downloaded all the files")
    
#   Clocking out 
    t2 = time.time()
    print("Total time taken: {0}".format(t2-t1))


if __name__ == '__main__':
    
    # companyCode = ['AMD']
    # cik = ['0000002488']
    companyCode = []
    cik = []    
    with open('sp500.txt') as f:
        df = pd.read_csv(f,sep=',')
        df["CIK"] = df.CIK.map("{:010}".format)
        for index, row in df.iterrows():
            companyCode.append(row['Name'])
            cik.append(row['CIK'])
    
    date = '20201231'       #date from which filings should be downloaded
    count = 25            # number of filings to be downloaded, at minimum 10 entries by EDGAR
    
    for i in range(len(cik)):
#        path = get_filings(companyCode[i], cik[i], date, count)     #Fetching the data based on input details
        get_filings(companyCode[i], cik[i], date, count)     #Fetching the data based on input details
