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
    soup = BeautifulSoup(main_page.content, 'html5lib')
    finding_lp = soup.select(".box-hide a")
    for link in finding_lp:
        urls.append(link['href'])
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
        soup = BeautifulSoup(r.text, 'html5lib')
        article_title = soup.find("h1")
        dl_tag = soup.find_all("div", {"class": "next-post"})
        for rml in dl_tag:
            rml.decompose()
        body = soup.find_all("div", {"class": "article-detail"})
        final_html_op = '<br/>'.join([str(tag) for tag in body])
        final_html_op = str(article_title) + str(final_html_op)
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
    tmp_var = soup.select(".box-hide a")
    for datess in tmp_var:
        span = datess.find('span')
        if span:
            dt = span.get_text()
            try:
                parsed_dt = parser.parse(dt)
                final_date = parsed_dt.replace(tzinfo=pytz.timezone('Asia/Kolkata'))
                datedata.append(final_date)
            except Exception as e:
                print(f"Could not parse date '{dt}': {e}")
    print(f"Found {len(datedata)} publication dates.")
    return datedata


def feedgen_main(feeds):
    print("Generating RSS feed...")
    title_feed = 'Drishti IAS RSS feeds'
    id_feed = 'https://monk-blade.github.io/scripts-rss/drishti-rss.xml'
    author_name_feed = 'Arpan'
    author_mail_feed = 'monk@blade.com'
    link_feed = 'https://monk-blade.github.io/scripts-rss/drishti-rss.xml'
    logo_feed = 'https://www.drishtiias.com/frontend/img/drishti_logo_new.png'
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
    print("Starting Drishti IAS RSS feed script...")
    start = time.perf_counter()
    main_link = 'https://www.drishtiias.com/hindi/current-affairs-news-analysis-editorials'
    urls = get_urls(main_link)
    feed_dates = getdate_data(main_link)
    resp = get_data(urls)
    fds = parse_data(resp,urls,feed_dates)
    fg = FeedGenerator()
    feedgen_main(fds)
    print("Saving RSS feed to drishti-rss.xml...")
    fg.rss_file('drishti-rss.xml')
    fin = time.perf_counter() - start
    print(f"Script completed in {fin:.2f} seconds.")