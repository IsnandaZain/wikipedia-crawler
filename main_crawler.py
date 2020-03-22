import sys
import mysql.connector
import requests
import re
import bs4 as bs


"""
    Crawl Wikipedia Webpage
    Properties :
    - r {requests object}
    - data_raw {string} -> teks html dari webpage
    - soup {BeautifulSoup object}
    - no_text {list} -> untuk mengecek apakah halaman masih kosong
    - title {string} -> judul dari artikel webpage
    - get_snippet {BeautifulSoup object} -> berisi teks yang terdapat pada div dengan class=mw-parser-output
    - snippet {list} -> snippet artikel webpage
    - res_data {dictionaries} -> object return yang berisi 'title' , 'snippet' , 'panjang snippet'
"""
def wikipedia_crawler(url):        
    r = requests.get(url)
    data_raw = r.text
    soup = bs.BeautifulSoup(data_raw, 'html.parser')
    
    no_text = soup.find_all('div', class_='noarticletext mw-content-ltr')
    if len(no_text) == 1:
        return "Halaman Masih Kosong!"
    else:
        title = soup.find('h1', class_='firstHeading').text
        get_snippet = soup.find_all('div', class_='mw-parser-output')
        for i in get_snippet:
            get_snippet = i.find_all('p')
    
        snippet = ''
        for i in get_snippet:
            if title in i.text:
                snippet = snippet + ''.join(i.text)
    
        snippet = snippet[:500]
        res_data = {}
        res_data['title'] = title
        res_data['snippet'] = snippet
        res_data['panjang_snippet'] = len(snippet)
        return res_data
    
"""
    Processing Data through Database Operations (Get and Input Data)
    Properties :
    - mydb {mysql object}
    - res_data {dictionaries} -> object return yang berisi 'title' , 'snippet' , 'panjang snippet'
"""
def data_checker(url):
    mydb = mysql.connector.connect(
        host = "localhost",
        user = "root",
        passwd = "",
        database = "db_sebangsa",
    )
    
    cursor = mydb.cursor()
    sql_get_data = "SELECT * FROM wikipedia_data WHERE url='{}'".format(url)
    cursor.execute(sql_get_data)
    
    result = cursor.fetchall()
    if len(result) != 0:
        result = result[0]
        print("Data Diambil dari Database!!")
        res_data = {}
        res_data['title'] = str(result[2])
        res_data['snippet'] = str(result[3])
        res_data['panjang_snippet'] = len(str(result[3]))
        return res_data
    else:
        print("Data Diambil dari Crawling!!")
        res_data = wikipedia_crawler(url)
        
        if res_data == "Halaman Masih Kosong!":
            return res_data
        else:
            sql_input_data = 'INSERT INTO wikipedia_data VALUES(NULL, "{}", "{}", "{}")'.format(url, res_data['title'], res_data['snippet'])
            cursor.execute(sql_input_data)
            mydb.commit()
            return res_data
            
"""
    Checking suitability url request
    Properties :
    - url {string} -> url request
    - pattern {regex} -> pattern untuk mendapatkan url 'http://*.wikipedia.org'
    - res_url {string} -> domain utama dari url request 
"""
def url_checker(url):
    pattern = re.finditer(r'^(?:http(s)?:\/\/)?[\w.-]+', url)
    res_url = ''
    for res in pattern:
        res_url = ''.join(res.group(0))
    
    if 'wikipedia.org' in res_url:
        return data_checker(url)
    else:
        return "Url Tidak Valid!"
    
"""
    Get url request
    Properties:
    url {string} -> url berupa input dari user
"""
url = input("Input URL : ")
print(url_checker(url))