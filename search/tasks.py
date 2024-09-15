from celery import shared_task
from search.utils import scrapper

@shared_task
def search_task():
    search_queries = [
        "tech",
        "business",
        "health",
        "science",
        "politics",
        "entertainment",
        "sports",
        "travel",
        # "lifestyle",
        # "environment",
        # "education",
        # "crime",
        # "automotive",
        # "finance",
        # "real estate",
        # "startups",
        # "energy",
        # "social media",
        # "culture",
        # "agriculture",
        # "artificial intelligence",
        # "gadgets",
        # "mental health",
        # "food",
        # "weather",
        # "legal",
        # "philanthropy",
        # "space",
        # "physics",
        # "higher education",
        # "k-12 education",
        # "fitness"
    ]
    return scrapper(search_queries)
