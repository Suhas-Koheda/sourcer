import wikipediaapi
import requests
import json

def google_custom_search(query):
    """
    Search using Google Custom Search API for Wikipedia pages
    """
    with open('client_secrets.json', 'r') as f:
        secrets = json.load(f)
    
    API_KEY = secrets['installed']['client_secret']
    SEARCH_ENGINE_ID = secrets['installed']['client_id']
    
    url = "https://www.googleapis.com/customsearch/v1"
    
    params = {
        'key': API_KEY,
        'cx': SEARCH_ENGINE_ID,
        'q': query + " wikipedia",
        'num': 5  # Get top 5 results
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def extract_wikipedia_page_name(search_results):
    """
    Extract Wikipedia page name from Google search results
    """
    if not search_results or 'items' not in search_results:
        return None
    
    for item in search_results['items']:
        title = item.get('title', '')
        link = item.get('link', '')
        
        # Check if it's a Wikipedia page
        if 'en.wikipedia.org/wiki/' in link:
            # Extract page name from URL
            page_name = link.split('/wiki/')[-1]
            # Clean up URL encoding
            page_name = page_name.replace('_', ' ')
            # Remove fragment identifiers
            page_name = page_name.split('#')[0]
            return page_name
    
    return None

def get_wikipedia_page_name_from_topic(topic: str) -> str:
    """
    Convert a topic name to a valid Wikipedia page title using Google Custom Search.
    
    Args:
        topic (str): The topic name (e.g., "python programming", "world war 2")
    
    Returns:
        str: Valid Wikipedia page title
    """
    # Use your existing Google Custom Search function
    search_results = google_custom_search(topic)
    
    if not search_results:
        raise ValueError(f"No search results found for topic: {topic}")
    
    # Use your existing function to extract Wikipedia page name
    page_name = extract_wikipedia_page_name(search_results)
    
    if not page_name:
        raise ValueError(f"No Wikipedia page found for topic: {topic}")
    
    return page_name
