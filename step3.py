import csv
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import re

# chrome driver
# return soup <class 'bs4.BeautifulSoup'>
def chrome_driver(url):
    
    driver = webdriver.Chrome(executable_path='/Applications/chromedriver')
    driver.get(url)
    sleep(1)
    text = driver.page_source
    sleep(1)
    soup = BeautifulSoup(text, 'lxml')
    driver.close()
    
    return soup

# extract authors' name and generate their orcid.org's url
# return urls list
def author_url(file_path):
    author_first = []
    author_last = []
    urls = []
    
    with open(file_path, encoding = "utf-8") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        for row in reader:
            author_first.append(row[2])
            author_last.append(row[1])
    
    if len(author_first) == len(author_first):
        for i in range(len(author_first)):
            u = (author_first[i] + '&lastName=' +author_last[i])
            urls.append('https://orcid.org/orcid-search/search?firstName=' + u)
    
    return urls

# extract authors' orcid
# return orcid list
def extract_orcid(urls):
    orcids = []
    
    for url in urls:
        soup = chrome_driver(url)
        
        try: 
            orcid_column = soup.find('td', {"class":"orcid-id-column"})
            a = orcid_column.find('a')
            
            pattern = re.compile(r'\d\d\d\d-\d\d\d\d-\d\d\d\d-\d\d\d\d|\d\d\d\d-\d\d\d\d-\d\d\d\d-\d\d\d\w')
            fliter = re.findall(pattern, str(a))
            orcids.append(fliter[0])
        except:
            orcids.append("NO orcid yet")
    return orcids

# extract authors' scopus url
# return scopus url list
def extract_scopus(orcids):
    scopus = []
  
    for orcids in orcids:
        url = 'https://orcid.org/' + orc
        #e.g. https://orcid.org/0000-0003-0807-463X
        
        soup = chrome_driver(url)
        
        keyword = 'scopus.com'
        hrefs = soup.find_all('a', {"target":"externalIdentifier.value"})
        
        if len(hrefs) == 0:
            scopus.append('NO scopus website yet')
        else:
            for href in hrefs:
                links = href.get('href').split('\t')
                for link in links:
                    if keyword in link:
                        scopus.append(link)
    return scopus

# extract authors' h-index in scopus
# return h-index list
def extract_h(scopus):
    h = []
    
    for url in scopus:
        if url == 'NO scopus website yet':
                h.append('-1')
        else:
            soup = chrome_driver(url)
            
            try:
                author_details = soup.find('section', {"id":"authorDetailsHindex"})
                hindex = author_details.find('span', {"class":"fontLarge"})
                h.append(hindex.text)
            except:   
                h.append('-1')
    return h


#############################main#############################

file_path = '/Users/zhangqihao/Desktop/BIA660/FINNAL/Dataset/SCORE_csv.csv' 
#get authors' url
urls = author_url(file_path)
#get authors' webpage
scopus = extract_scopus(extract_orcid(urls))
#get and writer author's h-index
extract_h(scopus)

with open('/Users/zhangqihao/Desktop/BIA660/FINNAL/result.csv', 'w', encoding="utf-8") as file:
        writer = csv.writer(file)
        
        writer.writerow(['NO.', 'H-index'])
        for result in enumerate(extract_h(scopus)):
                writer.writerow(result)