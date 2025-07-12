from bs4 import BeautifulSoup
import grequests
import requests
import time
from feedgen.feed import FeedGenerator
from dateutil import parser
import pytz


def get_urls(link_main):
    print(f"Fetching URLs from main page: {link_main}")
    urls = []
    main_page = requests.get(link_main)
    print("Main page fetched. Parsing for article links...")
    soup = BeautifulSoup(main_page.content, 'lxml')
    finding_lp = soup.find_all("td", {"class": "views-field-title"})
    from bs4.element import Tag
    for link in finding_lp:
        a_tag = None
        # Only process if link is a Tag
        if isinstance(link, Tag):
            a_tag = link.find('a')
        if a_tag and isinstance(a_tag, Tag):
            href = a_tag.attrs.get('href')
            if href:
                urls.append('https://www.dhyeyaias.com/' + str(href))
    print(f"Found {len(urls)} article URLs.")
    return urls


def get_data(urls):
    print(f"Fetching data for {len(urls)} URLs asynchronously...")
    reqs = [grequests.get(link) for link in urls]
    resp = grequests.map(reqs)
    print("All article pages fetched.")
    return resp

def parse_data(resp,urls,feedas):
    print("Parsing article data...")
    feeds_list = []
    i = 0
    for r in resp:
        sp = BeautifulSoup(r.text, 'html5lib')
        article_title = sp.find("h1", {"id": "page-title"})
        dl_tag = sp.find("div", {"class": "boxdownload"})
        if dl_tag:
            dl_tag.decompose()
        body = sp.find("div", {"class": "node-content"})
        final_html_op = "<html><head><title>" + str(article_title) + "</title></head><body>" + str(article_title) + str(body) + "</body></html>"
        temp_feed = {
            'title' : article_title.text.strip() if article_title else 'No Title',
            'link_url' : urls[i],
            'pubDate' : feedas[i],
            'content' : final_html_op,
        }
        print(f"Parsed article: {temp_feed['title']}")
        i = i + 1
        feeds_list.append(temp_feed)
    print(f"Parsed {len(feeds_list)} articles.")
    return feeds_list

def getdate_data(datelink):
    print(f"Fetching publication dates from: {datelink}")
    datedata = []
    main_page = requests.get(datelink)
    soup = BeautifulSoup(main_page.content, 'lxml')
    tmp_var = soup.find_all("div", {"class": "viewdate"})
    for datess in tmp_var:
        dt = datess.get_text()
        dt = parser.parse(dt)
        final_date = dt.replace(tzinfo=pytz.timezone('Asia/Kolkata'))
        datedata.append(final_date)
    print(f"Found {len(datedata)} publication dates.")
    return datedata


def feedgen_main(feeds):
    print("Generating RSS feed...")
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
        entry.published(add_feeds['pubDate'])
        entry.content(add_feeds['content'],type="CDATA")
        print(f"Added entry to feed: {add_feeds['title']}")
    print("RSS feed generation complete.")

if __name__ == '__main__':
    print("Starting Dhyeya IAS RSS feed script...")
    start = time.perf_counter()
    main_link = 'https://www.dhyeyaias.com/hindi/current-affairs/articles'
    urls = get_urls(main_link)
    feedas = getdate_data(main_link)
    resp = get_data(urls)
    fds = parse_data(resp,urls,feedas)
    fg = FeedGenerator()
    feedgen_main(fds)
    print("Saving RSS feed to dhyeya-rss.xml...")
    fg.rss_file('dhyeya-rss.xml')
    fin = time.perf_counter() - start
    print(f"Script completed in {fin:.2f} seconds.")