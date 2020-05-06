import requests
import re
import pandas as pd

from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from urllib.parse import urlparse

def is_url(url):
    result = urlparse(url)
    if result.netloc == '':
        return False
    else:
        return True

def g_calculate(cites):
    cites.sort(reverse=True)
    count = 0
    flag = 0
    for g, cite in enumerate(cites):
        #print(g, ' ', cite)
        #print(g*g, ' ',count)
        #print()
        if count >= g*g:
            count += cite
            if count < (g+1) * (g+1):
                return (g)
                flag = 1
                break
            else:
                continue
        else:
            count += cite
    if flag==0:
        return(g)

def g_h_index(doi,file):
    
    url='https://dx.doi.org'

    driver = webdriver.Chrome()
    driver.get(url)
    #enter doi
    driver.find_element_by_css_selector("input[type='text']").send_keys(doi)
    driver.find_element_by_css_selector("input[type='submit']").submit()
    sleep(10)
    #If paper is on sciencedirect.com
    driver.find_element_by_id('author-group').find_element_by_tag_name('a').click()

    #try:
    #    driver.find_element_by_name('bau0005').click()
    #except NoSuchElementException:
    #    driver.find_element_by_name('baep-author-id4').click()
    try:   
        sleep(2)
        frame_element = driver.find_element_by_xpath('//*[@title="Mendeley Author Profile"]')
        driver.switch_to.frame(frame_element)
        sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        href = soup.find('a', {"class":"button-secondary see-more-link"})
        u=href["href"]
        if not is_url(u):
            x='https://www.mendeley.com'
            u=x+u
        print(u)
        driver.get(u)
        h_index = driver.find_element_by_xpath('//*[@class="stat-box with-tooltip stat-hindex"]')\
            .find_element_by_tag_name('data')
        #print("h_index:",h_index.text)
        file.write(h_index.text+',')
        sleep(5)
        
        #type 1:get from this page
        t = driver.find_element_by_xpath('//*[@class="TextHolder__TextAdjuster-s12ienp4-0 jVpJkf"]')
        if t.text=='View more':
            while(True):
                if_show_more = driver.find_element_by_xpath('//*[@class="publications-footer"]')\
                    .find_element_by_tag_name('div')
                if if_show_more.text!='':
                    driver.find_element_by_xpath('//*[@data-publications-card="view-more"]').click()
                    #print("show more")
                    sleep(5)
                else:
                    #print("0")
                    break

        #type 2:click View all publications
        else:
            if t.text=='View all publications':
                print("!!!")
                driver.find_element_by_xpath('//*[@data-publications-card="view-all-publications"]').click()
                sleep(5)
                while(True):
                    if_show_more = driver.find_element_by_xpath('//*[@class="publications-footer"]')\
                        .find_element_by_tag_name('div')
                    if if_show_more.text!='':
                        driver.find_element_by_xpath('//*[@data-publications-card="view-more"]').click()
                        #print("show more")
                        sleep(5)
                    else:
                        #print("0")
                        break
            else:
                file.write('-1,\n')
                driver.close()
                return
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.close()
        publications = soup.find('section', {"class":"publications-content"})
        pubs = publications.find_all('div', {"label":"Citations"})
        cites_ = []
        for pub in pubs:
            cites_.append(pub.find('data').text)
        cites = []
        #Transform citations str to int
        for cite in cites_:
            if cite == 'N/A':
                y = '0'
            else:
                temp = cite.split(',')
                y = ''
                for i in temp:
                    y+=i
            cites.append(int(y))
        g = g_calculate(cites)
        file.write(str(g)+'\n')
    
    #type 2: No publications
    except NoSuchElementException:
        file.write('-1\n')
    except Exception as e:
        print(e)
        url = driver.current_url 
        driver.close()
        #file.write('\n')
        file.write('-1\n')

###################################### main ######################################
Doi = pd.read_csv('SCORE_csv.csv',usecols=[1,2,4])
with open("my_result.txt","a") as file:
    count = 0
    for i, d in enumerate(Doi['DOI_CR']):
        count+=1
        print(count)
        file.write(Doi.loc[i,'author_first_CR'] + ' ' + Doi.loc[i,'author_last_CR']+ ',')
        g_h_index(d,file)
        #break

    #g_h_index('10.1016/j.jesp.2018.04.001',file)
