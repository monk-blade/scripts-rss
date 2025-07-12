# Copilot Instructions for AI Coding Agents

## Project Overview
This repository processes multiple RSS feeds, enriches them using Gemini AI, and outputs enhanced RSS XML files. The main workflow is orchestrated in `rss_processor.py`.

## Architecture & Data Flow
- **Input:** RSS feed URLs are defined in `RSS_FEED_URLS` (in `rss_processor.py`).
- **Processing Steps:**
  1. Fetch RSS XML from each URL.
  2. Parse feeds using `feedparser`.
  3. For each feed entry, send content to Gemini AI for summarization and HTML generation (Gujarati, with emojis, HTML formatting).
  4. Insert AI-generated content into the RSS `<description>` field.
  5. Save processed feeds to the `public/` directory.
- **Output:** Enhanced RSS XML files, named by sanitized feed title or domain.

## Key Files & Directories
- `rss_processor.py`: Main script, contains all logic for fetching, processing, and saving feeds.
- `public/`: Output directory for processed RSS files.
- `requirements.txt`: Python dependencies (`requests`, `feedparser`).

## Developer Workflows
- **Run the pipeline:**
  ```bash
  python rss_processor.py
  ```
- **Dependencies:** Install with:
  ```bash
  pip install -r requirements.txt
  ```
- **Gemini API:** Requires `GEMINI_API_KEY` set as an environment variable.
- **Rate Limiting:** Script enforces 1 Gemini request every 4 seconds (max 15/min).

## Patterns & Conventions
- **AI Integration:** All Gemini prompts must request Gujarati summaries with emojis and HTML, starting with "સારાંશ" as an H2 heading.
- **Output Naming:** Output files use sanitized feed titles or domain names for uniqueness.
- **Error Handling:** If Gemini API fails or key is missing, script skips AI processing and continues.
- **Extensibility:** Add new RSS URLs to `RSS_FEED_URLS`.

## External Dependencies
- **Gemini AI:** Used for content enrichment. API endpoint and key are configured in `rss_processor.py`.
- **feedparser:** Used for RSS parsing.
- **requests:** Used for HTTP requests.

## Example: Adding a New Feed
1. Add the feed URL to `RSS_FEED_URLS` in `rss_processor.py`.
2. Run the script. The new feed will be processed and output to `public/`.

---
For questions or unclear conventions, review `rss_processor.py` for implementation details. If workflow or integration points are missing, ask for clarification.
