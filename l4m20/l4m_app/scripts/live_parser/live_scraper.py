import urllib
import requests as req
from urllib.request import urlopen
import html.parser as hp
from html_parser import LiveHTMLParser
from bs4 import BeautifulSoup
from requests_html import HTMLSession


def div_has_class(div, classname):
    return (div.has_attr('class') and classname in div['class'])

#google-chrome --headless --dump-dom 'http://lega4mori.com/l4m/live/' > file.html

url = "https://www.fantacalcio.it/serie-a/calendario/1/2025-26/atalanta-pisa/16670/voti"

# resp = req.get(url)
# html_resp = resp.text
# html_content = resp.content

session = HTMLSession()
response = session.get(url)
response.html.render()
html_resp = response.html.html

# page = urlopen(url)
# html_base = page.read()
# html = html_base.decode('utf-8')

soup = BeautifulSoup(html_resp, 'html.parser')

grades_section = soup.find(id='playersListsTemplateTarget')
divs = grades_section.find_all('div')

for div in divs:
    if(div_has_class(div, 'home')):
        ul_section = div.find('ul')
        pass


# parser = LiveHTMLParser().feed(html)

