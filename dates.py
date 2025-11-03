import re
from typing import Dict, List, Tuple, Union
import requests
from wiki_name import get_wikipedia_page_name_from_topic


def extract_dates_from_topic(topic: str, language: str = 'en', user_agent: str = 'MyProjectName (merlin@example.com)') -> Dict[str, Union[str, Dict[str, str]]]:
    """
    MAIN FUNCTION: Extract dates from a topic by first finding the Wikipedia page,
    then getting complete text, and finally extracting dates.
    
    Args:
        topic (str): The topic name (e.g., "python programming", "world war 2")
        language (str): Language code for Wikipedia (default: 'en')
        user_agent (str): User agent string for API identification
    
    Returns:
        Dict containing page info and dates dictionary (date -> context text)
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
        dates_dict = extract_dates_to_dict(page_text)
        print(f"  - Found {len(dates_dict)} unique dates")
        
        return {
            'topic': topic,
            'wikipedia_page': page_name,
            'text_length': len(page_text),
            'dates_found': len(dates_dict),
            'dates': dates_dict  # This is now a dictionary: date -> context
        }
        
    except Exception as e:
        print(f"Error processing topic '{topic}': {e}")
        return {
            'topic': topic,
            'error': str(e),
            'dates': {}
        }

def extract_dates_to_dict(text: str) -> Dict[str, str]:
    """
    Extract dates from Wikipedia page text and return as dictionary.
    Dates are normalized and sorted in chronological order.
    Returns complete sentences containing the dates.
    
    Args:
        text (str): Complete text from Wikipedia page
    
    Returns:
        Dict[str, str]: Dictionary with normalized dates as keys and complete sentences as values
    """
    # Comprehensive date patterns
    date_patterns = [
        # ISO format: YYYY-MM-DD
        r'\b\d{4}-\d{2}-\d{2}\b',
        # Full date: Month DD, YYYY or DD Month YYYY
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
        r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
        # Short date: MM/DD/YYYY or DD/MM/YYYY
        r'\b\d{1,2}/\d{1,2}/\d{4}\b',
        # Year only (4 digits, but not part of other numbers)
        r'\b(?:19|20)\d{2}\b(?!\d)',
        # Decades: 1990s, 1920s, etc.
        r'\b(?:19|20)\d{0}0s\b',
        # BC/AD dates
        r'\b\d+\s*(?:BC|BCE|AD|CE)\b',
        # Circa dates
        r'\bc\.\s*\d{4}\b',
    ]
    
    dates_dict = {}
    
    for pattern in date_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            original_date = match.group()
            
            # Normalize the date
            normalized_date = normalize_date(original_date)
            
            # Get the complete sentence containing the date
            sentence = extract_complete_sentence(text, match.start(), match.end())
            
            # Store with normalized date as key, keep the longest context
            if normalized_date not in dates_dict or len(sentence) > len(dates_dict[normalized_date]):
                dates_dict[normalized_date] = sentence
    
    # Sort dates chronologically and return as ordered dictionary
    return sort_dates_chronologically(dates_dict)

def extract_complete_sentence(text: str, start_pos: int, end_pos: int) -> str:
    """
    Extract the complete sentence containing the given position.
    
    Args:
        text (str): The complete text
        start_pos (int): Start position of the date
        end_pos (int): End position of the date
    
    Returns:
        str: Complete sentence containing the date
    """
    # Find the start of the sentence (previous period, exclamation, question mark or beginning of text)
    sentence_start = 0
    for i in range(start_pos, 0, -1):
        if text[i] in '.!?':
            sentence_start = i + 1
            break
        elif i == 0:
            sentence_start = 0
            break
    
    # Find the end of the sentence (next period, exclamation, question mark or end of text)
    sentence_end = len(text)
    for i in range(end_pos, len(text)):
        if text[i] in '.!?':
            sentence_end = i + 1
            break
        elif i == len(text) - 1:
            sentence_end = len(text)
            break
    
    # Extract the sentence and clean it up
    sentence = text[sentence_start:sentence_end].strip()
    
    # Remove extra whitespace and newlines
    sentence = re.sub(r'\s+', ' ', sentence)
    
    # If sentence is too short, try to get more context (the paragraph)
    if len(sentence) < 50:
        # Find the start of the paragraph (two newlines or beginning of text)
        para_start = 0
        for i in range(start_pos, 0, -1):
            if text[i:i+2] == '\n\n':
                para_start = i + 2
                break
            elif i == 0:
                para_start = 0
                break
        
        # Find the end of the paragraph (two newlines or end of text)
        para_end = len(text)
        for i in range(end_pos, len(text)):
            if text[i:i+2] == '\n\n':
                para_end = i
                break
            elif i == len(text) - 1:
                para_end = len(text)
                break
        
        paragraph = text[para_start:para_end].strip()
        paragraph = re.sub(r'\s+', ' ', paragraph)
        
        # Use paragraph if it provides better context
        if len(paragraph) > len(sentence):
            return paragraph
    
    return sentence

def normalize_date(date_str: str) -> str:
    """
    Normalize various date formats to a standard format.
    
    Args:
        date_str (str): Original date string
    
    Returns:
        str: Normalized date string
    """
    date_str = date_str.strip()
    
    # Handle circa dates
    if date_str.startswith('c.'):
        date_str = date_str[2:].strip()
        circa_prefix = 'c. '
    else:
        circa_prefix = ''
    
    # Handle BC/BCE dates (convert to negative years)
    if any(x in date_str.upper() for x in [' BC', ' BCE']):
        year_match = re.search(r'(\d+)', date_str)
        if year_match:
            year = int(year_match.group(1))
            return f"{circa_prefix}{-year} BCE"
    
    # Handle AD/CE dates
    if any(x in date_str.upper() for x in [' AD', ' CE']):
        year_match = re.search(r'(\d+)', date_str)
        if year_match:
            year = int(year_match.group(1))
            return f"{circa_prefix}{year} CE"
    
    # Handle decades (1990s -> 1990)
    if date_str.endswith('s') and re.match(r'(?:19|20)\d{2}s', date_str):
        return f"{circa_prefix}{date_str[:-1]}"
    
    # Handle full month names (January 15, 2023 -> 2023-01-15)
    month_map = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12'
    }
    
    # Pattern for "Month DD, YYYY" or "DD Month YYYY"
    month_pattern = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
    full_date_match = re.match(rf'({month_pattern})\s+(\d{{1,2}}),?\s+(\d{{4}})', date_str, re.IGNORECASE)
    if full_date_match:
        month_name, day, year = full_date_match.groups()
        month_num = month_map[month_name.lower()]
        return f"{circa_prefix}{year}-{month_num}-{day.zfill(2)}"
    
    # Pattern for "DD Month YYYY"
    full_date_match2 = re.match(rf'(\d{{1,2}})\s+({month_pattern})\s+(\d{{4}})', date_str, re.IGNORECASE)
    if full_date_match2:
        day, month_name, year = full_date_match2.groups()
        month_num = month_map[month_name.lower()]
        return f"{circa_prefix}{year}-{month_num}-{day.zfill(2)}"
    
    # Handle MM/DD/YYYY or DD/MM/YYYY (assuming MM/DD/YYYY for now)
    slash_date_match = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_str)
    if slash_date_match:
        month, day, year = slash_date_match.groups()
        return f"{circa_prefix}{year}-{month.zfill(2)}-{day.zfill(2)}"
    
    # Handle ISO format (already normalized)
    iso_match = re.match(r'\d{4}-\d{2}-\d{2}', date_str)
    if iso_match:
        return f"{circa_prefix}{date_str}"
    
    # Handle year only (1999 -> 1999)
    year_only_match = re.match(r'(?:19|20)\d{2}', date_str)
    if year_only_match:
        return f"{circa_prefix}{date_str}"
    
    # Return original if no pattern matches
    return date_str

def sort_dates_chronologically(dates_dict: Dict[str, str]) -> Dict[str, str]:
    """
    Sort dates in chronological order.
    
    Args:
        dates_dict (Dict[str, str]): Dictionary of dates to context
    
    Returns:
        Dict[str, str]: Chronologically sorted dictionary
    """
    def date_sort_key(date_str: str) -> Tuple[int, int, int]:
        """
        Convert date string to sortable tuple (year, month, day).
        Handles BCE dates as negative years.
        """
        # Handle circa dates
        if date_str.startswith('c. '):
            date_str = date_str[3:]
        
        # Handle BCE dates
        if ' BCE' in date_str:
            year = int(date_str.replace(' BCE', ''))
            return (-year, 0, 0)  # Negative years for BCE
        
        # Handle CE dates
        if ' CE' in date_str:
            year = int(date_str.replace(' CE', ''))
            return (year, 0, 0)
        
        # Handle full dates (YYYY-MM-DD)
        if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            year, month, day = map(int, date_str.split('-'))
            return (year, month, day)
        
        # Handle year only
        if re.match(r'\d{4}', date_str):
            year = int(date_str)
            return (year, 0, 0)
        
        # Default for unrecognized formats
        return (0, 0, 0)
    
    # Sort by chronological order
    sorted_items = sorted(dates_dict.items(), key=lambda x: date_sort_key(x[0]))
    
    # Return as ordered dictionary (Python 3.7+ preserves insertion order)
    return dict(sorted_items)

def extract_dates(text: str) -> List[Dict[str, str]]:
    """
    Original function that returns dates as list of dictionaries.
    Keeping this for backward compatibility.
    """
    dates_dict = extract_dates_to_dict(text)
    dates_list = []
    
    for date_str, context in dates_dict.items():
        dates_list.append({
            'date': date_str,
            'context': context
        })
    
    return dates_list

def get_complete_page_text(page_title: str, language: str = 'en', user_agent: str = 'haas (sharmasuhas450@gmail.com)') -> str:
    """
    Get the complete text of a Wikipedia page including summary and all sections using wikitext.
    
    Args:
        page_title (str): The title of the Wikipedia page
        language (str): Language code for Wikipedia (default: 'en')
        user_agent (str): User agent string for API identification
    
    Returns:
        str: Complete text of the Wikipedia page without headers/footers/references
    """
    headers = {
        'User-Agent': user_agent
    }
    
    # Get the page content in wikitext format
    url = f"https://{language}.wikipedia.org/w/api.php"
    
    params = {
        'action': 'query',
        'titles': page_title,
        'prop': 'revisions',
        'rvprop': 'content',
        'format': 'json'
    }
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code != 200:
        raise ValueError(f"Error fetching page: {response.status_code}")
    
    data = response.json()
    pages = data.get('query', {}).get('pages', {})
    
    # Get the first page
    page_id = next(iter(pages))
    page_data = pages[page_id]
    
    if page_id == '-1' or 'revisions' not in page_data:
        raise ValueError(f"Page '{page_title}' does not exist in {language} Wikipedia")
    
    # Get the wikitext content
    wikitext = page_data['revisions'][0]['*']
    
    # Clean the wikitext to remove markup and get clean text
    clean_text = clean_wikitext(wikitext)
    
    return clean_text

def clean_wikitext(wikitext: str) -> str:
    """
    Clean wikitext by removing markup and keeping clean text with proper sentence boundaries.
    """
    # Remove HTML comments
    text = re.sub(r'<!--.*?-->', '', wikitext, flags=re.DOTALL)
    
    # Remove references ({{cite ...}}, {{sfn ...}}, etc.)
    text = re.sub(r'{{[^}]*}}', '', text)
    
    # Remove templates like {{lang|...}}
    text = re.sub(r'{{[^}]*?}}', '', text)
    
    # Remove file/image links [[File:...]]
    text = re.sub(r'\[\[File:[^\]]*\]\]', '', text)
    text = re.sub(r'\[\[Image:[^\]]*\]\]', '', text)
    
    # Remove external links [http://...]
    text = re.sub(r'\[https?://[^\s\]]*\]', '', text)
    
    # Convert internal links [[link|display]] to just "display" or "link"
    text = re.sub(r'\[\[[^\]|]*\|([^\]]*)\]\]', r'\1', text)  # [[link|display]] -> display
    text = re.sub(r'\[\[([^\]|]*)\]\]', r'\1', text)  # [[link]] -> link
    
    # Remove bold/italic markup '''text''' -> text
    text = re.sub(r"'''''([^']*)'''''", r'\1', text)  # '''''bold italic'''''
    text = re.sub(r"'''([^']*)'''", r'\1', text)  # '''bold'''
    text = re.sub(r"''([^']*)''", r'\1', text)  # ''italic''
    
    # Remove section headers (== Header ==)
    text = re.sub(r'=+\s*(.*?)\s*=+', r'\1. ', text)  # Convert headers to text with period
    
    # Remove remaining markup characters
    text = re.sub(r'[{}]', '', text)
    
    # Clean up whitespace
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    
    # Remove unwanted sections
    lines = text.split('\n')
    filtered_lines = []
    skip_section = False
    
    unwanted_sections = [
        'references', 'external links', 'see also', 'notes', 
        'footnotes', 'bibliography', 'further reading', 'sources'
    ]
    
    for line in lines:
        line_lower = line.lower()
        
        # Check if this line starts an unwanted section
        if any(section in line_lower for section in unwanted_sections):
            skip_section = True
            continue
        
        # Reset skip_section when we reach a new major section (empty line or new context)
        if skip_section and (line.strip() == '' or re.match(r'^[A-Z]', line.strip())):
            skip_section = False
            continue
            
        if not skip_section and line.strip():
            filtered_lines.append(line.strip())
    
    return '\n'.join(filtered_lines)

def extract_context_paragraph(text: str, start_pos: int, end_pos: int) -> str:
    """
    Extract a contextual paragraph when sentence boundaries are not clear.
    """
    # Expand search window to get more context
    context_window = 300  # characters to look before and after
    
    # Calculate safe boundaries
    context_start = max(0, start_pos - context_window)
    context_end = min(len(text), end_pos + context_window)
    
    # Extract context
    context = text[context_start:context_end].strip()
    context = re.sub(r'\s+', ' ', context)
    
    return context


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
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    """
    Convert a topic name to a valid Wikipedia page title using Wikipedia search API.
    
    Args:
        topic (str): The topic name (e.g., "python programming", "world war 2")
        user_agent (str): User agent string for API identification
    
    Returns:
        str: Valid Wikipedia page title
    """
    search_results = wikipedia_search(topic, user_agent)
    
    if not search_results:
        raise ValueError(f"No search results found for topic: {topic}")
    
    page_name = extract_wikipedia_page_name(search_results)
    
    if not page_name:
        raise ValueError(f"No Wikipedia page found for topic: {topic}")
    
    return page_name