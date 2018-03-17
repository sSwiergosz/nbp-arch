import urllib.request, urllib.parse
from bs4 import BeautifulSoup
from hashlib import md5
import sys, json

# 2018-2012: przyjazna budowa, article, contentholder, head2
# 2011: tytuł - klasa hdr

simple_json = {}
year = sys.argv[1]

page = urllib.request.urlopen('http://www.nbp.pl/home.aspx?f=/aktualnosci/wiadomosci_{0}.htm'.format(year))
soup = BeautifulSoup(page, 'html.parser')
anchors = soup.find_all('a', class_='news_head')
dates = soup.find_all('span', class_='date')

for i in range(0, len(anchors)):
    content = ''
    
    article = urllib.request.urlopen('http://www.nbp.pl{0}'.format(anchors[i].get('href')))
    soup = BeautifulSoup(article, 'html.parser')

    iid = int(md5('http://www.nbp.pl{0}'.format(anchors[i].get('href')).encode('utf-8')).hexdigest(), 16)
    simple_json['iid'] = iid
    simple_json['id'] = '{}-1'.format(iid)

    simple_json['url'] = 'http://www.nbp.pl{0}'.format(anchors[i].get('href'))
    simple_json['lname'] = 'nbp.pl'
    time = dates[i].text[1:-1]
    if time[-5] == '.':
        time = dates[i].text[1:-1].split('.')
    elif time[-5] == '-':
        time = dates[i].text[1:-1].split('-')
    simple_json['duration_start'] = '{}-{}-{}T00:00:00Z'.format(time[2], time[1], time[0])
    simple_json['duration_end'] = '{}-{}-{}T23:59:59Z'.format(time[2], time[1], time[0])

    if soup.find('span', class_='hdr'): # strona w starszej wersji
        simple_json['title'] = soup.find('span', class_='hdr').text
        for i in soup.find_all('p', class_=None):
            content += i.text
            content += '\n'
        simple_json['content'] = content.replace('\n', ' ').replace('\r', '').replace('\t', '')

    else:
        if soup.find('p', class_='head2'):
            simple_json['title'] = soup.find('p', class_='head2').text # wyszukanie tytułu
            if soup.find('div', id='contentholder'):
                for i in soup.find('div', id='contentholder').find_all('p', class_=None):
                    content += i.text
                    content += '\n'
            else:
                tab = soup.find('div', id='article')
                paragraphs = tab.find_all('p')
                for i in paragraphs:
                    content += i.text
                    content += '\n'
                print(content)
        elif soup.find('span', class_='tyt'):
            simple_json['title'] = soup.find('span', class_='tyt').text # wyszukanie tytułu
            for i in soup.find('div', class_='justify'):
                content += i
                content += '\n'
        
        simple_json['content'] = content.replace('\n', ' ').replace('\r', '').replace('\t', '')
    # print(simple_json)



# server = '150.254.78.133'
# core = 'isi'
# url = 'http://{}:8983/solr/{}/update/json/docs?commit=true'.format(server, core)

# f = urllib.parse.urlencode(simple_json)
# f = f.encode('utf-8')

# req = urllib.request.Request(url, f)
# req.add_header('Content-type', 'application/json')
# response = urllib.request.urlopen(req)
# page = response.read()
# print(page)