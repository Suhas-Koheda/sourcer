import wikipediaapi
import requests

def wikipedia_search(topic: str,user_agent: str = 'haas (sharmasuhas450@gmail.com)'):
    """
    Search using Wikipedia API directly
    """
    url = "https://en.wikipedia.org/w/api.php"
    
    headers = {
        'User-Agent': user_agent
    }
     
    params = {
        'action': 'query',
        'list': 'search',
        'srsearch': topic,
        'format': 'json'
    }
    
    response = requests.get(url, params=params,headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def extract_wikipedia_page_name(search_results):
    """
    Extract Wikipedia page name from Wikipedia search results
    """
    if not search_results or 'query' not in search_results or 'search' not in search_results['query']:
        return None
    
    # Get the first search result
    search = search_results['query']['search']
    if search:
        return search[0]['title']
    
    return None

def get_wikipedia_page_name_from_topic(topic: str) -> str:
    """
    Convert a topic name to a valid Wikipedia page title using Wikipedia search API.
    
    Args:
        topic (str): The topic name (e.g., "python programming", "world war 2")
    
    Returns:
        str: Valid Wikipedia page title
    """
    search_results = wikipedia_search(topic)
    
    if not search_results:
        raise ValueError(f"No search results found for topic: {topic}")
    
    page_name = extract_wikipedia_page_name(search_results)
    
    if not page_name:
        raise ValueError(f"No Wikipedia page found for topic: {topic}")
    
    return page_name
