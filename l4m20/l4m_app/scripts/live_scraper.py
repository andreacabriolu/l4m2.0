import urllib
from urllib.request import urlopen
import html.parser as hp
from l4m_app.scripts.html_parser import LiveHTMLParser

#google-chrome --headless --dump-dom 'http://lega4mori.com/l4m/live/' > file.html

url = "https://www.fantacalcio.it/serie-a/calendario/1/2025-26/atalanta-pisa/16670/voti"
page = urlopen(url)
html_base = page.read()
html = html_base.decode('utf-8')

parser = LiveHTMLParser()
parser.feed(html)