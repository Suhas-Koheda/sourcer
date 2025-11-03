import wikipediaapi
from typing import List, Dict, Union

from dates import extract_dates_from_topic

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

if __name__ == "__main__":
    # Example topics to process
    topics = [
        "Andhra pradesh"
    ]
    
    print("Starting date extraction from Wikipedia pages...")
    print("=" * 60)
    
    # Process all topics
    results = process_multiple_topics(topics)
    
    # Display results - CORRECTED VERSION
    for result in results:
        print(f"\nTopic: {result['topic']}")
        print(f"Wikipedia Page: {result.get('wikipedia_page', 'N/A')}")
        
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Text Length: {result['text_length']} characters")
            print(f"Dates Found: {result['dates_found']}")
            
            # FIX: Since 'dates' is now a dictionary, we need to handle it differently
            dates_dict = result['dates']
            
            # Show first 5 dates as example
            print("\nFirst 5 dates:")
            for i, (date_str, context) in enumerate(list(dates_dict.items()), 1):
                print(f"  {i}. {date_str} - ...{context[:60]}...")
        
        print("-" * 40)