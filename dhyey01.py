from bs4 import BeautifulSoup
import grequests
import requests
import time
from feedgen.feed import FeedGenerator
from dateutil import parser
import pytz


def get_urls(link_main):
    urls = []
    main_page = requests.get(link_main)
    soup = BeautifulSoup(main_page.content, 'lxml')
    finding_lp = soup.find_all("td", {"class": "views-field-title"})
    for link in finding_lp:
        urls.append('https://www.dhyeyaias.com/' + link.find('a')['href'])
    return urls


def get_data(urls):
    reqs = [grequests.get(link) for link in urls]
    resp = grequests.map(reqs)
    return resp

def parse_data(resp,urls,feedas):
    feeds_list = []
    i = 0
    for r in resp:
        sp = BeautifulSoup(r.text, 'html5lib')
        article_title = sp.find("h1", {"id": "page-title"})
        dl_tag = sp.find("div", {"class": "boxdownload"})
        dl_tag.decompose()
        body = sp.find("div", {"class": "node-content"})
        final_html_op = str(article_title)+str(body)
        #print(final_html_op)
        temp_feed = {
            'title' : article_title.text.strip(),
            'link_url' : urls[i],
            'pubDate' : feedas[i],
            #'content' : final_html_op,
        }
        i = i + 1
        feeds_list.append(temp_feed)
    return feeds_list

def getdate_data(datelink):
    datedata = []
    main_page = requests.get(datelink)
    soup = BeautifulSoup(main_page.content, 'lxml')
    # get the dates from link
    tmp_var = soup.find_all("div", {"class": "viewdate"})
    #print(tmp_var)
    for datess in tmp_var:
        dt = datess.get_text()
        dt = parser.parse(dt)
        final_date = dt.replace(tzinfo=pytz.timezone('Asia/Kolkata'))
        #print(final_date)
        datedata.append(final_date)
    #     datedata.append('https://www.dhyeyaias.com/' + link.find('a')['href'])
    return datedata


def feedgen_main(feeds):
    title_feed = 'Dhyeya IAS RSS feeds'
    id_feed = 'https://monk-blade.github.io/scripts-rss/dhyeya-rss.xml'
    author_name_feed = 'Arpan'
    author_mail_feed = 'monk@blade.com'
    link_feed = 'https://monk-blade.github.io/scripts-rss/dhyeya-rss.xml'
    logo_feed = 'https://www.dhyeyaias.com/sites/default/files/Dhyeya-IAS-English-Logo-Small.png'
    lang_feed = 'en'
    subtitle_feed = 'UPSC Serving'

    fg.id(id_feed)
    fg.title(title_feed)
    fg.author({'name': author_name_feed, 'email': author_mail_feed})
    fg.logo(logo_feed)
    fg.subtitle(subtitle_feed)
    fg.link(href=link_feed, rel='self')
    fg.language(lang_feed)
    for add_feeds in feeds:
        entry = fg.add_entry()
        entry.title(add_feeds['title'])
        entry.id(add_feeds['link_url'])
        entry.link(href=add_feeds['link_url'], rel='alternate')
        entry.pubDate(add_feeds['pubDate'])
        #entry.content(add_feeds['content'],type="CDATA")

if __name__ == '__main__':
    start = time.perf_counter()
    main_link = 'https://www.dhyeyaias.com/hindi/current-affairs/articles'
    urls = get_urls(main_link)
    #print(urls)
    feedas = getdate_data(main_link)
    resp = get_data(urls)
    fds = parse_data(resp,urls,feedas)
    #print(fds)
    fg = FeedGenerator()
    feedgen_main(fds)
    fg.rss_file('dhyeya-rss.xml')
    fin = time.perf_counter() - start
    print(fin)