from requests_html import HTMLSession

# define a function to get the search results given a url
def get_search_results(url):
    session = HTMLSession()
    response = session.get(url)
    response.html.render()
    return response.html.find(".g")

# define a function to extract the title and link from a search result
def extract_result_data(result):
    return {
        "title": result.find("h3", first=True).text,
        "link": list(result.absolute_links)[0]
    }

# define a function to get the search results given a query
def search(query):
    url = f"https://news.google.com/rss/search?q={query}"
    results = get_search_results(url)
    return [extract_result_data(result) for result in results]