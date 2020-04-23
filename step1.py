import requests
from bs4 import BeautifulSoup
import csv
import os


def splice_url(authors):
    prefix = 'https://scholar.google.com/citations?&view_op=search_authors&mauthors='
    url_list = []
    for author in authors:
        name = author.replace(' ', '+')
        url = prefix + name
        url_list.append(url)

    return url_list


def parsing_response_scholor(re):
    # Parsing the response
    soup = BeautifulSoup(re.content, 'html.parser')

    sa_ccl = soup.find('div', id='gsc_sa_ccl')
    div = sa_ccl.find('div')
    if (div['class'][0] == 'gs_med'):
        raise RuntimeError('testError')
    else:
        href = div.find('a').get('href')
        return prefix + href


def request_scholer(url):
    re = requests.get(url)

    soup = BeautifulSoup(re.content, 'html.parser')

    table = soup.find('table', id='gsc_rsb_st')
    tbody = table.find('tbody')
    trs = tbody.find_all('tr')
    for tr in trs:
        if (tr.find('td').text == 'h-index'):
            result = tr.find_all('td')[1].text
            return result
        else:
            continue


# return_list has 3 parameters
# the first one is the authors name
# the second is the result. if it is true means the author has a result, vice versa.(duplicate)
# the third is the h_index, if the second is fault, it will be 0;
# return the result from scholor
def step1_visitScholor(url_list, authors):
    visit_url = []

    result_list = []
    count = 0
    for url in url_list:
        result = []
        result.append(authors[count])
        count += 1

        # deduplicate
        if (url in visit_url):
            result.append('duplicate')
            result_list.append(result)
            continue

        visit_url.append(url)
        print(url)

        try:
            re = requests.get(url)
            next_url = parsing_response_scholor(re)
            h_index = request_scholer(next_url)
            result.append('true')
            result.append(h_index)
            result_list.append(result)
        except:
            result.append('fault')
            result.append('0')
            result_list.append(result)
            continue

        print(result)

    return result_list


########### main #############
authors = []

score_file = os.getcwd() + '/SCORE_csv.csv'

with open(score_file) as csvfile:
    reader = csv.reader(csvfile)
    header = next(reader)
    for row in reader:
        authors.append(row[2] + ' ' + row[1])

# temp1 = []
# temp2 = []
# for author in authors:
#    if author not in temp1:
#        temp1.append(author)
#    else:
#        temp2.append(author)
# print(temp2)

url_list = splice_url(authors)
result_list = step1_visitScholor(url_list, authors)
print(result_list)



