import requests
import feedparser
import os
from xml.etree import ElementTree as ET

# --- CONFIG ---
RSS_FEED_URLS = [
    'https://reader.websitemachine.nl/api/query.php?user=arpanchavdaeng&t=43c93b5336ffb7d07cc1b3971fde9970&f=rss',  # Add your feed URLs here
    # 'https://another.com/feed.xml',
]
gemini_api_key = os.getenv('GEMINI_API_KEY')  # Set your Gemini API key as env var
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite-preview-06-17:generateContent'
OUTPUT_DIR = 'public'

# --- STEP 1: Fetch RSS Feed ---
def fetch_rss(url):
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text

# --- STEP 2: Parse RSS Feed ---
def parse_rss(feed_xml):
    return feedparser.parse(feed_xml)

# --- STEP 3: Process with Gemini AI ---
def process_with_gemini(text):
    if not gemini_api_key:
        print('No Gemini API key set. Skipping AI processing.')
        return {'summary': '', 'html': ''}
    headers = {'Content-Type': 'application/json'}
    # Ask Gemini to summarize and generate HTML content
    prompt = (
        "Summarize the following RSS feed item in 5 sentences, then generate improved HTML content for it. "
        "Respond in 'html'.\nContent: " + text
    )
    payload = {
        'contents': [{'parts': [{'text': prompt}]}]
    }
    params = {'key': gemini_api_key}
    try:
        r = requests.post(GEMINI_API_URL, headers=headers, params=params, json=payload)
        r.raise_for_status()
        data = r.json()
        # Try to parse JSON from Gemini's response
        import json as _json
        response_text = data['candidates'][0]['content']['parts'][0]['text']
        try:
            result = _json.loads(response_text)
            return {'summary': result.get('summary', ''), 'html': result.get('html', '')}
        except Exception:
            # Fallback: treat all as html, no summary
            return {'summary': '', 'html': response_text}
    except Exception as e:
        print(f'Gemini API error: {e}')
        return {'summary': '', 'html': ''}

# --- STEP 4: Add HTML to RSS Items ---
def add_html_to_rss(feed_xml, html_contents):
    tree = ET.ElementTree(ET.fromstring(feed_xml))
    channel = tree.find('channel')
    items = channel.findall('item')
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
            desc.text = (desc.text or '') + '\n' + combined
        else:
            ET.SubElement(item, 'description').text = combined
    return ET.tostring(tree.getroot(), encoding='utf-8', xml_declaration=True)

# --- STEP 5: Save Processed RSS ---
def save_rss(xml_bytes, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(xml_bytes)
    print(f'Processed RSS saved to {path}')

if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    from urllib.parse import urlparse
    import re
    for feed_url in RSS_FEED_URLS:
        print(f'Processing feed: {feed_url}')
        # 1. Fetch
        feed_xml = fetch_rss(feed_url)
        # 2. Parse
        parsed = parse_rss(feed_xml)
        # 3. Process each entry with Gemini (get summary and html)
        html_contents = []
        for entry in parsed.entries:
            content = entry.get('summary', '') or entry.get('description', '')
            result = process_with_gemini(content)
            html_contents.append(result)
        # 4. Add summary and HTML to RSS
        processed_xml = add_html_to_rss(feed_xml, html_contents)
        # 5. Save, use a unique filename per feed (from feed title if available)
        feed_title = parsed.feed.get('title', None)
        if feed_title:
            # Sanitize title to filename: remove non-alphanum, replace spaces with _
            feed_name = re.sub(r'[^A-Za-z0-9_]+', '', feed_title.replace(' ', '_'))
        else:
            feed_name = urlparse(feed_url).netloc.replace('.', '_')
        output_path = os.path.join(OUTPUT_DIR, f'processed-{feed_name}.xml')
        save_rss(processed_xml, output_path)
