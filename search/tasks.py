from celery import shared_task
from search.utils import scrape_and_push_to_db


@shared_task
def hello_world():
    print("Hello, World!")


@shared_task
def search_task(query):
    search_queries = [
        "tech",
        "business",
        "health",
        "science",
        "politics",
        "entertainment",
        "sports",
        "travel",
        "lifestyle",
        "environment",
        "education",
        "crime",
        "automotive",
        "finance",
        "real estate",
        "startups",
        "energy",
        "social media",
        "culture",
        "agriculture",
        "artificial intelligence",
        "gadgets",
        "mental health",
        "food",
        "weather",
        "legal",
        "philanthropy",
        "space",
        "physics",
        "higher education",
        "k-12 education",
        "fitness"
    ]
    return scrape_and_push_to_db(search_queries)
