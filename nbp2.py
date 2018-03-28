import urllib.request, urllib.parse
from bs4 import BeautifulSoup
from hashlib import md5
import sys, json
import requests

# TODO 
# 2017: w niektorych brak contentu, dodajace sie skrypty jquery do contentu, niezamkniety tag w 'moneta roku 2017'
# 2016: pusty content w 2 komunikatach
# 2015: pusty content w 2 komunikatach
# 2014: pusty content w 3 komunikatach, z czego 2 prawidłowe
# 2013: dużo problemu z contentholderem, hilines
# 2012: pusty content w 8 komunikatach - na wlasne zyczenie (pomijanie tagu a)


simple_json = {}
l = []
#year = sys.argv[1]
year = 2014

index = urllib.request.urlopen('http://www.nbp.pl/home.aspx?f=/aktualnosci/wiadomosci_{0}.htm'.format(year))
index_soup = BeautifulSoup(index, 'lxml')
anchors = index_soup.find_all('a', class_='news_head')
dates = index_soup.find_all('span', class_='date')
titles = index_soup.find_all('a', class_='news_head')

for a in range(0, len(anchors)):
    content = ''
    
    if anchors[a].get('href').startswith('/home.aspx'):
        # ignoring non-ascii characters in link
        href = anchors[a].get('href').encode('utf-8').decode('ascii', 'ignore')
        url = 'http://www.nbp.pl{0}'.format(href)
        request = requests.get(url)
        if not request.status_code == 200: # if site doesn't exist go to another one
            continue

        # print(url)
        statement = urllib.request.urlopen(url)
        statement_soup = BeautifulSoup(statement, 'lxml')

        iid = int(md5(url.encode('utf-8')).hexdigest(), 16)
        simple_json["iid"] = iid
        simple_json["id"] = '{}-1'.format(iid)
        simple_json["url"] = url
        simple_json["lname"] = "nbp.pl"

        # there are two different types of date sep: 2018-2004 is '-', older years is '.'
        time = dates[a].text[1:-1]
        if time[-5] == '.':
            time = dates[a].text[1:-1].split('.')
        elif time[-5] == '-':
            time = dates[a].text[1:-1].split('-')

        simple_json["title"] = titles[a].text
        simple_json["duration_start"] = "{}-{}-{}T00:00:00Z".format(time[2], time[1], time[0])
        simple_json["duration_end"] = "{}-{}-{}T23:59:59Z".format(time[2], time[1], time[0])

        # there are different types of building pages across the years
        if statement_soup.find('div', id='contentholder'):
            contentholder = statement_soup.find('div', id='contentholder')
            paragraphs = contentholder.find_all('p', class_=None)

            # not all statements have class 'srodtytul'
            if contentholder.find('p', class_='srodtytul'):
                content += contentholder.find('p', class_='srodtytul').text.strip()
                content += '\n'
            
            if contentholder.find_all('li'):
                for c in contentholder.find_all('li'):
                    content += c.text
                content += 'n'
            
            for p in paragraphs:
                content += p.text.strip()
                content += '\n'
        
        else:
            if len(statement_soup.find('div', id='article').find_all('td')) != 1:
                td = statement_soup.find('div', id='article').find_all('td')[1]
            else:
                td = statement_soup.find('div', id='article').find('td')
            if td.find('p'):
                if td.find_all('li'): # if there are lists
                    for i in td.find_all('p'):
                        l.append(i)
                    for i in td.find_all('li'):
                        l.append(i)
                else:
                    for i in td.find_all('p'):
                        l.append(i)
                for i in l:
                    content += i.text
                    content += '\n'
            elif td.find_all('div', class_='justify'):
                for i in td.find_all('div', class_='justify'):
                    content += i.text.strip()
                    content += '\n'

        simple_json['content'] = content

    print(simple_json)
