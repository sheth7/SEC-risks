import time
import crawler
import pandas as pd
#import operate

def get_filings(a,b,c,d):
    t1 = time.time()
    seccrawler = crawler.SecCrawler() # creating object crawler from class SecCrawler()
    
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

#    return path     
    
if __name__ == '__main__':
    
    companyCode = []
    cik = []
    
    with open('sp500.txt') as f:
        df = pd.read_csv(f,sep=',')
        df["CIK"] = df.CIK.map("{:010}".format)
        for index, row in df.iterrows():
            companyCode.append(row['Name'])
            cik.append(row['CIK'])
        
        
    
    
#    with open('cik_ticker_database.csv') as f:
#        df = pd.read_csv(f, sep='|')
#        df["CIK"] = df.CIK.map("{:010}".format)
#        for index, row in df.iterrows():
#            companyCode.append(row['Name'])
#            cik.append(row['CIK'])
    
        
    
#    companyCode = ['Norfolk Southern','Southwest Airlines','International Paper'
#                   ,'PG&E','Freeport-McMoRan','Bristol-Myers Squibb'
#                   ,'Texas Instruments','Las Vegas Sands','Las Vegas Sands b'
#                   ,'Abbott Laboratories','Marriott International','Biogen'
#                   ,'Monsanto','Andeavor','AmerisourceBergen','Applied Materials'
#                   ,'General Motors','Cisco Systems','TJX Cos'
#                   ,'American International Group']    #company code for Apple Inc
#    cik = ['0000702165','0000092380','0000051434','0001004980','0000831259'
#           ,'0000014272','0000097476','0001300514','0000850994' ,'0001441848'
#           ,'0001048286','0000875045','0001110783','0000050104','0001140859'
#           ,'0000006951','0000040730','0000858877','0000109198','0000005272']      #cik code for Apple Inc
    date = '20190512'       #date from which filings should be downloaded
    count = len(cik)            # number of filings to be downloaded, at minimum 10 entries by EDGAR
    
    for i in range(len(cik)):
#        path = get_filings(companyCode[i], cik[i], date, count)     #Fetching the data based on input details
        get_filings(companyCode[i], cik[i], date, count)     #Fetching the data based on input details
    
#    clean_text = operate.clean_data(path)
    
#    print()
#    print("The cleaned text for the data is as follows:\n")
#    print()
#    print ("Total number of unique tokens after clearning the text file are:\n")
#    print(len(clean_text))
#    print()
#    print(clean_text)       #Output
#    print()