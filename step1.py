import requests
from bs4 import BeautifulSoup
import csv
import os
import time
from selenium import webdriver

result_range =100

def extractAuthors(score_file):
    authors = []
    with open(score_file, encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        for row in reader:
            authors.append(row[2] + ' ' + row[1])
    return authors

def write_result(result_list):
    with open('g-index and h-index.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['author_name', 'find_or_not', 'H-index', 'G-index'])
        for result in result_list:
            if len(result) == 4:
                writer.writerow(result)
            else:
                writer.writerow([result[0], "Error Occure", -1, -1, "An error occured when finding the g-index"])


def get_urls(authors):
    prefix = 'https://scholar.google.com/citations?&view_op=search_authors&mauthors='
    url_list = []
    for author in authors:
        name = author.replace(' ', '+')
        url = prefix + name
        url_list.append(url)

    return url_list


def get_personal_url(url):
    re = requests.get(url)
    soup = BeautifulSoup(re.content, 'html.parser')

    sa_ccl = soup.find('div', id='gsc_sa_ccl')
    div = sa_ccl.find('div')
    if (div['class'][0] == 'gs_med'):
        raise RuntimeError('testError')
    else:
        href = div.find('a').get('href')
        return "https://scholar.google.com" + href


def get_h_index(soup):
    table = soup.find('table', id='gsc_rsb_st')
    tbody = table.find('tbody')
    trs = tbody.find_all('tr')
    for tr in trs:
        if (tr.find('td').text == 'h-index'):
            h_index = tr.find_all('td')[1].text
            return h_index


def get_g_index(driver):

    #click "Show More" button to show all articles
    for i in range(10):
        show_more_button = driver.find_element_by_id('gsc_art').find_element_by_id("gsc_bpf_more")
        show_more_button.click()

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table', id = 'gsc_a_t')
    tbody = table.find('tbody')
    trs = tbody.find_all('tr')
    total_cited = 0
    length = len(trs)
    for i, tr in enumerate(trs):
        square =(i+1)*(i+1)
        year = tr.find_all('td')[2].text
        if(year == ''):
            return i
        else:
            numCited = tr.find_all('td')[1].text.replace('*', '')
            if(numCited == ''):
                numCited = 0
            else:
                numCited = int(numCited)
        if(numCited>=0):
            total_cited += numCited
            if square > total_cited:
                return i
        if i == length-1:
            return i

# return_list has 4 parameters
# 1st is the authors name
# 2nd indicates whether we found the personal page in Google Scholar.(YES/NO/Error Occure))
# 3rd is the h_index, if the second is fault, it will be -1
# 4th is the g_index, if the second is fault, it will be -1
def step1(url_list, authors):
    visited_url = []

    result_list = []
    for i, url in enumerate(url_list):
        print(i)
        result = []
        result.append(authors[i])

        # deduplicate
        if (url in visited_url):
            result.append('duplicate')
            for r in result_list:
                if (r[0] == result[0]):
                    result.append(r[2])
                    result.append(r[3])
            result_list.append(result)
            continue

        visited_url.append(url)
        print("Visiting: " + url)

        try:
            personal_page_url = get_personal_url(url)

            driver = webdriver.Chrome()
            driver.get(personal_page_url)
            re = requests.get(personal_page_url)
            soup = BeautifulSoup(re.content, 'html.parser')

            result.append('YES')
            result.append(get_h_index(soup))
            result.append(get_g_index(driver))
            driver.quit()
            result_list.append(result)

        except:
            result.append('NO')
            result.append(-1)  # h-index = -1
            result.append(-1)  # g-index = -1
            result_list.append(result)
            continue
        print(result)

    return result_list



##################################### main ######################################

score_file = 'SCORE_csv.csv'

authors = extractAuthors(score_file)
#authors = ["Malia F. Mason", "Roland Imhoff", "Simone Tang", "Jordan R. Axt", "Jennifer Susan McClung"]

url_list = get_urls(authors)

result_list = step1(url_list, authors)

write_result(result_list)


