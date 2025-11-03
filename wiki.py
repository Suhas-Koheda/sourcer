import wikipediaapi
import requests
import json
import re
from typing import List, Dict, Union

from dates import extract_dates
from wiki_name import extract_wikipedia_page_name, google_custom_search,get_wikipedia_page_name_from_topic


def get_complete_page_text(page_title: str, language: str = 'en', user_agent: str = 'MyProjectName (merlin@example.com)') -> str:
    """
    Get the complete text of a Wikipedia page including summary and all sections.
    
    Args:
        page_title (str): The title of the Wikipedia page
        language (str): Language code for Wikipedia (default: 'en')
        user_agent (str): User agent string for API identification
    
    Returns:
        str: Complete text of the Wikipedia page
    """
    # Initialize Wikipedia API
    wiki_wiki = wikipediaapi.Wikipedia(
        user_agent=user_agent,
        language=language,
        extract_format=wikipediaapi.ExtractFormat.WIKI
    )
    
    # Get the page
    page = wiki_wiki.page(page_title)
    
    if not page.exists():
        raise ValueError(f"Page '{page_title}' does not exist in {language} Wikipedia")
    
    # Return the complete text (includes summary + all sections)
    return page.text

def extract_dates_from_topic(topic: str, language: str = 'en', user_agent: str = 'MyProjectName (merlin@example.com)') -> Dict[str, Union[str, List[Dict]]]:
    """
    MAIN FUNCTION: Extract dates from a topic by first finding the Wikipedia page,
    then getting complete text, and finally extracting dates.
    
    Args:
        topic (str): The topic name (e.g., "python programming", "world war 2")
        language (str): Language code for Wikipedia (default: 'en')
        user_agent (str): User agent string for API identification
    
    Returns:
        Dict containing page info and extracted dates
    """
    try:
        print(f"Processing topic: {topic}")
        
        # Step 1: Get Wikipedia page name from topic using your existing functions
        print("  - Finding Wikipedia page...")
        page_name = get_wikipedia_page_name_from_topic(topic)
        print(f"  - Found page: {page_name}")
        
        # Step 2: Get complete page text
        print("  - Fetching page content...")
        page_text = get_complete_page_text(page_name, language, user_agent)
        print(f"  - Retrieved {len(page_text)} characters of text")
        
        # Step 3: Extract dates from the text
        print("  - Extracting dates...")
        dates = extract_dates(page_text)
        print(f"  - Found {len(dates)} dates")
        
        return {
            'topic': topic,
            'wikipedia_page': page_name,
            'text_length': len(page_text),
            'dates_found': len(dates),
            'dates': dates
        }
        
    except Exception as e:
        print(f"Error processing topic '{topic}': {e}")
        return {
            'topic': topic,
            'error': str(e),
            'dates': []
        }

def process_multiple_topics(topics: List[str], language: str = 'en', user_agent: str = 'MyProjectName (merlin@example.com)') -> List[Dict]:
    """
    Process multiple topics and extract dates from their Wikipedia pages.
    
    Args:
        topics (List[str]): List of topic names
        language (str): Language code for Wikipedia
        user_agent (str): User agent string for API identification
    
    Returns:
        List[Dict]: Results for each topic
    """
    results = []
    
    for topic in topics:
        result = extract_dates_from_topic(topic, language, user_agent)
        results.append(result)
        
        # Small delay to be respectful to APIs
        import time
        time.sleep(1)
    
    return results

# Example usage
if __name__ == "__main__":
    # Example topics to process
    topics = [
        "telangana separation"
    ]
    
    print("Starting date extraction from Wikipedia pages...")
    print("=" * 60)
    
    # Process all topics
    results = process_multiple_topics(topics)
    
    # Display results
    for result in results:
        print(f"\nTopic: {result['topic']}")
        print(f"Wikipedia Page: {result.get('wikipedia_page', 'N/A')}")
        
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Text Length: {result['text_length']} characters")
            print(f"Dates Found: {result['dates_found']}")
            
            # Show first 5 dates as example
            for i, date_info in enumerate(result['dates'][:5], 1):
                print(f"  {i}. {date_info['date']} - ...{date_info['context'][:60]}...")
        
        print("-" * 40)