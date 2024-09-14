import feedparser
import json
import requests
from newspaper import Article
from chromadb import Client, Collection
import chromadb
from googlesearch import search

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
        redirects.append(resp.headers.get('Location'))
    return response.url


def fetch_url(query: str):
    for j in search(query, tld="com", num=1, stop=1, pause=2):
        return j


def parse_article_content(entry: feedparser.FeedParserDict):
    """Parse the article content from the given link using Newspaper3k."""
    try:
        # Follow redirects to get the final URL
        final_url = fetch_url(entry.title)

        # Use Newspaper3k to extract the article content from the final URL
        article = Article(final_url)
        article.download()
        article.parse()

        return article.text
    except Exception as e:
        return f"Error parsing article: {str(e)}"


def extract_feed_entry_data(entry):
    """Extract relevant data from a feed entry."""
    article_content = parse_article_content(entry)

    return {
        "title": entry.title,
        "link": entry.link,
        "description": entry.description,
        "published": entry.published,
        "source": entry.get('source', {}).get('title', 'Unknown Source'),
        "content": article_content
    }


def save_to_chromadb(entries):
    """Save the extracted data to ChromaDB."""
    client = chromadb.HttpClient(host='localhost', port=8000)
    collection = client.get_or_create_collection(
        name="news_articles")  # Get or create a collection

    documents = []
    metadatas = []
    ids = []

    for index, entry in enumerate(entries):
        metadata = {
            "title": entry['title'],
            "link": entry['link'],
            "description": entry['description'],
            "published": entry['published'],
            "source": entry['source'],
        }
        documents.append(entry['content'])
        metadatas.append(metadata)
        ids.append(str(index))

    # Upsert the extracted data into the collection
    collection.upsert(documents=documents, metadatas=metadatas, ids=ids)


def scrape_and_push_to_db(query):
    """Fetch news articles from Google News, extract data, and save to ChromaDB."""
    feed = fetch_rss_feed(query)

    if feed.entries:
        # Limit the number of entries processed to max_results
        limited_entries = [extract_feed_entry_data(
            entry) for entry in feed.entries[:10]]
        save_to_chromadb(limited_entries)
    else:
        return json.dumps({"message": "Nothing Found!"}, indent=4)


def retrieve_from_chromadb(query: str):
    client = chromadb.HttpClient(host='localhost', port=8000)
    collection = client.get_collection(name="news_articles")
    print(collection.count())

    if collection:
        results = collection.query(
            # Query for documents containing the word "Python"
            query_texts=[query],
            # Retrieve the content, document and metadata fields
            include=['distances', 'metadatas', 'documents'],
            n_results=5
        )
        return results
    else:
        return json.dumps({"message": "Collection not found!"}, indent=4)


def search(search_queries: list):
    for query in search_queries:
        scrape_and_push_to_db(query)
