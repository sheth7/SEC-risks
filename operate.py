
from nltk import word_tokenize
import re
from nltk.corpus import stopwords

def clean_data(data):

    data = data.lower()
    
    
#    removing the \t and \n characters
    data = data.replace('\t',' ').replace('\n',' ')
#
##    removing the non-breaking space and special characters    
    data = data.replace('&#160;',' ').replace('&nbsp;',' ')
    data = data.replace('&#174',' ').replace('&#xA0;',' ')
    data = data.replace('&#32;',' ').replace('&#8220;',' ')
    data = data.replace('&#8221;',' ').replace('&#8217;', ' ')
    data = data.replace('&#149',' ').replace('&#146',' ')
                        
#    keeping the string between the two Item 1A. and Item 1B.   
    data_keep = re.findall(r"item 1a\.(.+?)item 1b\.",data) 
    
#    converting list of strings (output of re.findall into single string)    
    data = ". ".join(data_keep)
                                                
                        
##    removing the <HEAD></HEAD> from utf-8 encoded data       
#    clean = re.compile('<HEAD>.*?</HEAD>')
#    data = re.sub(clean,' ', data)                        
#
##    removing the <TABLE></TABLE> from utf-8 encoded data       
#    clean = re.compile('<CENTER>.*?</CENTER>')
#    data = re.sub(clean,' ', data)                        
#
##    removing the image utf-8 encoded data       
#    clean = re.compile('\.jpg(.|\s)*?</TEXT>')
#    data = re.sub(clean,' ', data)
#
##    removing the zip utf-8 encoded data
#    clean = re.compile('\.zip(.|\s)*?</TEXT>')
#    data = re.sub(clean,' ', data)    
#    
##    removing the xls utf-8 encoded data
#    clean = re.compile('\.xls(.|\s)*?</TEXT>')
#    data = re.sub(clean,' ', data)
#
##    removing the xsd utf-8 encoded data
#    clean = re.compile('\.xsd(.|\s)*?</TEXT>')
#    data = re.sub(clean,' ', data)    
#
#    
##    removing the png utf-8 encoded data
#    clean = re.compile('\.png.*|\s*<TEXT>.*?</TEXT>')
#    data = re.sub(clean,' ', data)   
#    
##    removing the pdf utf-8 encoded data
#    clean = re.compile('\.pdf(.|\s)*?</TEXT>')
#    data = re.sub(clean,' ', data)

##    removing the XBRL format utf-8 encoded data   
#    clean = re.compile('<XBRL>(.|\s)*?</XBRL>')
#    data = re.sub(clean,' ', data)
#
#
##    removing the .htm format utf-8 encoded data        
#    clean = re.compile('\.htm(.|\s)*?</TEXT>')
#    data = re.sub(clean,' ', data)
#
#
##    removing the xml utf-8 encoded data
#    clean = re.compile('\.xml(.|\s)*?</TEXT>')
#    data = re.sub(clean,' ', data)

#    removing the \t and \n characters
#    data = path.replace('\t',' ').replace('\n',' ')
#    data = path.replace('\t',' ')

#    removing the html tags from data
#
    clean = re.compile(r'<(.|\s)*?>')
    data = re.sub(clean,'', data)

#    clean4 = re.compile('<(.|\s)*?>')
#    data4 = re.sub(clean4,' ', data3)



#    removing all numbers from data   - this seems like a bad idea

#    clean4 = re.compile('\d+(?:\.\d+)?')
#    data4 = re.sub(clean4, ' ', data3)

    return (data)

#    return tokenize(data4)

def tokenize(data4):
#   Using NLTK library to tokenize remainder of the data 
    tokens = word_tokenize(data4)
#   Removes duplicate tokens by converting list into set object    
    set_tokens = set(tokens)
#   Removing stopwords like a, the, etc. from the tokenized data
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [w for w in set_tokens if not w in stop_words]        
    ordered_filtered = sorted(filtered_tokens)
    return ordered_filtered 