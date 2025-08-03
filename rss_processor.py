import requests
import feedparser
import os
import time
from xml.etree import ElementTree as ET

# --- CONFIG ---
RSS_FEED_URLS = [
    'https://reader.websitemachine.nl/api/query.php?user=arpanchavdaeng&t=43c93b5336ffb7d07cc1b3971fde9970&f=rss',  # Add your feed URLs here
    'https://reader.websitemachine.nl/api/query.php?user=arpanchavdaeng&t=0047bbb69bd4add7ed9d72e8ed02361a&f=rss',
    'https://reader.websitemachine.nl/api/query.php?user=arpanchavdaeng&t=9d10ff528a331696b57f0bc86caa336f&f=rss',
]
gemini_api_key = os.getenv('GEMINI_API_KEY')  # Set your Gemini API key as env var
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent'
OUTPUT_DIR = 'public'

# --- STEP 1: Fetch RSS Feed ---
def fetch_rss(url):
    print(f"Fetching RSS feed from: {url}")
    resp = requests.get(url)
    resp.raise_for_status()
    print("RSS feed fetched successfully.")
    return resp.text

# --- STEP 2: Parse RSS Feed ---
def parse_rss(feed_xml):
    print("Parsing RSS feed XML...")
    parsed = feedparser.parse(feed_xml)
    print(f"Parsed feed with {len(parsed.entries)} entries.")
    return parsed

# --- STEP 3: Process with Gemini AI ---
def process_with_gemini(text):
    print("Processing entry with Gemini AI...")
    if not gemini_api_key:
        print('No Gemini API key set. Skipping AI processing.')
        return {'summary': '', 'html': ''}
    headers = {'Content-Type': 'application/json'}
    prompt = (
        "Summarize the following RSS feed item to cover everything of content in bullet points with emojis in gujarati language and with html formatting. Summary must start with \"સારાંશ\" H2 heading and output.\n"
        "Feed Content: " + text
    )
    payload = {
        'contents': [{'parts': [{'text': prompt}]}],
        'generationConfig': {
            'thinkingConfig': {
                'thinkingBudget': -1
            }
        }
    }
    params = {'key': gemini_api_key}
    try:
        r = requests.post(GEMINI_API_URL, headers=headers, params=params, json=payload)
        r.raise_for_status()
        data = r.json()
        import json as _json
        response_text = data['candidates'][0]['content']['parts'][0]['text']
        import re
        response_text = re.sub(r'```(?:html|xml)?\s*', '', response_text)
        response_text = re.sub(r'```\s*$', '', response_text, flags=re.MULTILINE)
        response_text = response_text.replace('`', '')
        response_text = response_text.strip()
        try:
            result = _json.loads(response_text)
            print("Gemini AI returned structured summary and HTML.")
            return {'summary': result.get('summary', ''), 'html': result.get('html', '')}
        except Exception:
            print("Gemini AI returned plain HTML.")
            return {'summary': '', 'html': response_text}
    except Exception as e:
        print(f'Gemini API error: {e}')
        return {'summary': '', 'html': ''}

# --- STEP 4: Add HTML to RSS Items ---
def add_html_to_rss(feed_xml, html_contents, recent_entries=None):
    print("Adding AI-generated HTML and summaries to RSS items...")
    tree = ET.ElementTree(ET.fromstring(feed_xml))
    channel = tree.find('channel')
    if channel is None:
        print("No <channel> found in RSS XML.")
        return b''
    items = channel.findall('item')
    if recent_entries is not None:
        recent_titles = set()
        for entry in recent_entries:
            if 'title' in entry:
                recent_titles.add(entry['title'])
        idx = 0
        for item in list(items):
            title = item.find('title')
            key = title.text if title is not None else None
            if key in recent_titles and idx < len(html_contents):
                content = html_contents[idx]
                idx += 1
                summary = content.get('summary', '')
                html = content.get('html', '')
                desc = item.find('description')
                combined = ''
                if summary:
                    combined += f'<b>Summary:</b> {summary}<br/>'
                if html:
                    combined += html
                if desc is not None:
                    desc.text = combined + '\n' + (desc.text or '')
                else:
                    ET.SubElement(item, 'description').text = combined
                print(f"Updated item: {key}")
            else:
                if channel is not None:
                    channel.remove(item)
                    print(f"Removed item: {key}")
    else:
        for item, content in zip(items, html_contents):
            summary = content.get('summary', '')
            html = content.get('html', '')
            desc = item.find('description')
            combined = ''
            if summary:
                combined += f'<b>Summary:</b> {summary}<br/>'
            if html:
                combined += html
            if desc is not None:
                desc.text = combined + '\n' + (desc.text or '')
            else:
                ET.SubElement(item, 'description').text = combined
            title = item.find('title')
            key = title.text if title is not None else None
            print(f"Updated item: {key}")
    root = tree.getroot()
    if root is None:
        print("No root found in RSS XML.")
        return b''
    print("All items updated.")
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)

# --- STEP 5: Save Processed RSS ---
def save_rss(xml_bytes, path):
    print(f"Saving processed RSS to: {path}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(xml_bytes)
    print(f'Processed RSS saved to {path}')

if __name__ == '__main__':
    print("Starting RSS processor script...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    from urllib.parse import urlparse
    import re
    import time as _time
    for feed_url in RSS_FEED_URLS:
        print(f'Processing feed: {feed_url}')
        # 1. Fetch
        feed_xml = fetch_rss(feed_url)
        # 2. Parse
        parsed = parse_rss(feed_xml)
        # 3. Filter entries newer than 24 hours
        now = _time.time()
        twenty_four_hours = 24 * 60 * 60
        recent_entries = []
        for entry in parsed.entries:
            entry_time = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                if isinstance(entry.published_parsed, _time.struct_time):
                    entry_time = _time.mktime(entry.published_parsed)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                if isinstance(entry.updated_parsed, _time.struct_time):
                    entry_time = _time.mktime(entry.updated_parsed)
            if entry_time and (now - entry_time <= twenty_four_hours):
                recent_entries.append(entry)
        print(f"Found {len(recent_entries)} entries newer than 24 hours.")
        # 4. Process each recent entry with Gemini (get summary and html)
        html_contents = []
        for idx, entry in enumerate(recent_entries):
            print(f"Processing entry {idx+1}/{len(recent_entries)}...")
            content = entry.get('summary', '') or entry.get('description', '')
            result = process_with_gemini(content)
            html_contents.append(result)
            if idx < len(recent_entries) - 1:
                print("Waiting 4 seconds for Gemini API rate limit...")
                time.sleep(4)
        # 5. Add summary and HTML to RSS (only for recent entries)
        processed_xml = add_html_to_rss(feed_xml, html_contents, recent_entries=recent_entries)
        # 6. Save, use a unique filename per feed (from feed title if available)
        feed_title = None
        if isinstance(parsed.feed, dict):
            feed_title = parsed.feed.get('title', None)
        if feed_title:
            feed_name = re.sub(r'[^A-Za-z0-9_]+', '', feed_title.replace(' ', '_'))
        else:
            feed_name = urlparse(feed_url).netloc.replace('.', '_')
        output_path = os.path.join(OUTPUT_DIR, f'processed-{feed_name}.xml')
        save_rss(processed_xml, output_path)
    print("All feeds processed.")
