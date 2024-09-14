import feedparser
import json
from newspaper import Article
import requests
import re
import time

import urllib.request


def fetch_rss_feed(query):
    """Fetch the RSS feed from Google News based on the search query."""
    rss_url = f'https://news.google.com/rss/search?q={query}'
    feed = feedparser.parse(rss_url)
    return feed


def fetch_redirect_url(url):
    """Fetch the final URL after initial content redirection using request history."""
    response = requests.get(url)
    redirects = [url]
    for resp in response.history:
        redirects.append(resp.headers['Location'])
    return response.url


def parse_article_content(url):
    """Parse the article content from the given link using newspaper3k."""
    try:
        # Follow redirects to get the final URL
        final_url = fetch_redirect_url(url)

        # Print the final URL for debugging
        # print(f"Final URL: {final_url}")

        # Use Newspaper3k to extract the article content from the final URL
        article = Article(final_url)
        article.download()
        article.parse()

        # Return the extracted article content
        return article.text
    except Exception as e:
        return f"Error parsing article: {str(e)}"


def extract_feed_entry_data(entry):
    """Extract relevant data from a feed entry and parse the article content."""
    link = entry.link
    article_content = parse_article_content(
        'https://towardsdatascience.com/creating-project-environments-in-python-with-vscode-b95b530cd627')

    # Extract all relevant fields and return them as a dictionary
    return {
        "title": entry.title,
        "link": link,
        "description": entry.description,
        "published": entry.published,
        "source": entry.get('source', {}).get('title', 'Unknown Source'),
        "content": article_content
    }


def scrape_google_news_feed(query, max_results=5):
    """Fetch news articles from Google News, extract data, and return as JSON."""
    feed = fetch_rss_feed(query)

    if feed.entries:
        # Limit the number of entries processed to max_results
        limited_entries = feed.entries[:max_results]

        # List to store all the extracted news data
        news_data = [extract_feed_entry_data(
            entry) for entry in limited_entries]

        # Return the data as a formatted JSON string
        return json.dumps(news_data, indent=4)
    else:
        return json.dumps({"message": "Nothing Found!"}, indent=4)


def search(query):  
    result = scrape_google_news_feed('Python', max_results=1)
    print(result)
    return result