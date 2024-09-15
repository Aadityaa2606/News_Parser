import feedparser
import json
import requests
from newspaper import Article
import chromadb
from googlesearch import search
from urllib.parse import quote_plus
from search.cache import cache_get, cache_set, cache_ttl
from time import sleep


def fetch_rss_feed(query):
    """Fetch the RSS feed from Google News based on the search query."""
    encoded_query = ''
    for words in query.split(' '):
        encoded_query += words + '+'
    encoded_query = encoded_query[:-1]
    rss_url = f'https://news.google.com/rss/search?q={encoded_query}'
    feed = feedparser.parse(rss_url)
    return feed


def fetch_url(query: str):
    for j in search(query, tld="com", num=1, stop=1, pause=2):
        return j


def parse_article_content(entry):
    """Parse the article content from the given link using Newspaper3k."""
    try:
        # Follow redirects to get the final URL
        final_url = fetch_url(entry.title)
        sleep(2)
        # final_url = fetch_final_url(entry.link)
        # Use Newspaper3k to extract the article content from the final URL
        article = Article(final_url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        final_url = fetch_url(entry.title)
        sleep(2)
        return f"Error parsing article: {str(e)}, {final_url}"


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


def retrieve_from_chromadb(query: str, top_k: int = 10, threshold: float = None):
    # Create cache key based on the query (exclude top_k and threshold)
    cache_key = f'chromadb:{query}'
    print(f"Cache Key: {cache_key}")

    # Check if the result is cached
    cached_result = cache_get(cache_key)

    if cached_result:
        cache_time_left = cache_ttl(cache_key)
        print(f"Using cached result. Cache expires in {cache_time_left} seconds.")
        results = json.loads(cached_result)
    else:
        # Perform actual retrieval from ChromaDB
        client = chromadb.HttpClient(host='localhost', port=8000)
        collection = client.get_collection(name="news_articles")

        if collection:
            results = collection.query(
                query_texts=[query],
                include=['distances', 'metadatas', 'documents'],
            )
            # Cache the full result with a 5-minute timeout (300 seconds)
            print("Caching results...")
            cache_set(cache_key, json.dumps(results), timeout=300)
        else:
            return json.dumps({"message": "Collection not found!"}, indent=4)

    # Filter results based on the threshold and then apply top_k
    filtered_results = {
        "ids": [],
        "distances": [],
        "metadatas": [],
        "documents": []
    }

    for i, distance in enumerate(results['distances'][0]):
        if threshold is None or distance <= threshold:  # Apply threshold if provided
            filtered_results['ids'].append(results['ids'][0][i])
            filtered_results['distances'].append(distance)
            filtered_results['metadatas'].append(results['metadatas'][0][i])
            filtered_results['documents'].append(results['documents'][0][i])

        # Stop after top_k valid results are collected
        if len(filtered_results['ids']) >= top_k:
            break

    return filtered_results


def scrapper(search_queries: list):
    for query in search_queries:
        scrape_and_push_to_db(query)
