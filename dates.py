import re
from typing import Dict, List, Tuple, Union
import requests
from wiki_name import get_wikipedia_page_name_from_topic


def extract_dates_from_topic(topic: str, language: str = 'en', user_agent: str = 'Haas (sharmasuhas450@gmail.com)') -> Dict[str, Union[str, Dict[str, str]]]:
    """
    MAIN FUNCTION: Extract ALL dates from a Wikipedia page using raw content.
    """
    try:
        print(f"Processing topic: {topic}")
        
        # Step 1: Get Wikipedia page name from topic
        print("  - Finding Wikipedia page...")
        page_name = get_wikipedia_page_name_from_topic(topic)
        print(f"  - Found page: {page_name}")
        
        # Step 2: Get RAW page content (minimal cleaning)
        print("  - Fetching RAW page content...")
        raw_text = get_raw_page_content(page_name, language, user_agent)
        print(f"  - Retrieved {len(raw_text)} characters of raw text")
        
        # Step 3: Extract ALL dates aggressively
        print("  - Extracting dates aggressively...")
        dates_dict = extract_all_dates_aggressive(raw_text)
        print(f"  - Found {len(dates_dict)} unique dates with context")
        
        return {
            'topic': topic,
            'wikipedia_page': page_name,
            'text_length': len(raw_text),
            'dates_found': len(dates_dict),
            'dates': dates_dict
        }
        
    except Exception as e:
        print(f"Error processing topic '{topic}': {e}")
        return {
            'topic': topic,
            'error': str(e),
            'dates': {}
        }


def normalize_date_aggressive(date_str: str) -> str:
    """
    Normalize dates aggressively - keep more original information.
    """
    if not date_str:
        return date_str
        
    original = date_str
    date_str = date_str.strip()
    
    # Extract year from various patterns
    year_match = re.search(r'(1[0-9]{3}|2[0-9]{3})', date_str)
    if not year_match:
        # Try for BC/AD dates without specific year
        bc_match = re.search(r'(\d+)\s*(BC|BCE)', date_str, re.IGNORECASE)
        if bc_match:
            num, era = bc_match.groups()
            return f"{-int(num)} {era.upper()}"
        
        ad_match = re.search(r'(\d+)\s*(AD|CE)', date_str, re.IGNORECASE)
        if ad_match:
            num, era = ad_match.groups()
            return f"{num} {era.upper()}"
        
        return original
    
    year = year_match.group(1)
    
    # Handle circa
    circa = 'c. ' if re.search(r'\bc\.?\s*', date_str, re.IGNORECASE) else ''
    
    # Handle BC/BCE
    if re.search(r'\b(BC|BCE)\b', date_str, re.IGNORECASE):
        return f"{circa}{-int(year)} BCE"
    
    # Handle AD/CE  
    if re.search(r'\b(AD|CE)\b', date_str, re.IGNORECASE):
        return f"{circa}{year} CE"
    
    # Handle decades
    if date_str.endswith('s') and re.match(r'.*\d{4}s', date_str):
        return f"{circa}{year}s"
    
    # Handle full dates - try to extract month and day
    month_map = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12'
    }
    
    # Try to extract month and day
    for month_name, month_num in month_map.items():
        if month_name in date_str.lower():
            day_match = re.search(r'(\d{1,2})(?:\s|,|$)', date_str)
            day = day_match.group(1) if day_match else '01'
            return f"{circa}{year}-{month_num}-{day.zfill(2)}"
    
    # Handle ISO dates
    iso_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
    if iso_match:
        return f"{circa}{year}-{iso_match.group(2)}-{iso_match.group(3)}"
    
    # Handle slash dates (assume MM/DD/YYYY)
    slash_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_str)
    if slash_match:
        month, day, _ = slash_match.groups()
        return f"{circa}{year}-{month.zfill(2)}-{day.zfill(2)}"
    
    # Handle ranges
    range_match = re.search(r'(\d{4})[-–](\d{4}|present)', date_str)
    if range_match:
        start, end = range_match.groups()
        return f"{circa}{start}-{end}"
    
    # Default: just the year
    return f"{circa}{year}"

def extract_extensive_context(text: str, start_pos: int, end_pos: int, max_length: int = 600) -> str:
    """
    Extract context by capturing complete paragraphs around the date.
    """
    # Find paragraph start
    paragraph_start = start_pos
    for i in range(start_pos, max(0, start_pos - 800), -1):
        if i <= 2 or (i > 2 and text[i-2:i] == '\n\n'):
            paragraph_start = i
            break
        # Also look for bullet points or section markers
        if i > 1 and text[i-1] in ('•', '-', '*') and text[i] == ' ':
            paragraph_start = i - 1
            break
    
    # Find paragraph end
    paragraph_end = end_pos
    for i in range(end_pos, min(len(text), end_pos + 800)):
        if i >= len(text) - 2 or (i < len(text) - 2 and text[i:i+2] == '\n\n'):
            paragraph_end = i
            break
        # Stop at next bullet point or major section
        if i < len(text) - 1 and text[i] in ('\n', '.', '!', '?') and i > end_pos + 100:
            next_chars = text[i+1:i+3]
            if next_chars and next_chars[0] in ('•', '-', '*', '\n'):
                paragraph_end = i + 1
                break
    
    context = text[paragraph_start:paragraph_end].strip()
    
    # If we don't have enough content, expand to adjacent paragraphs
    if len(context) < 200:
        # Look for one more paragraph before
        extra_start = paragraph_start
        for i in range(paragraph_start, max(0, paragraph_start - 400), -1):
            if i > 2 and text[i-2:i] == '\n\n':
                extra_start = i
                break
        
        # Look for one more paragraph after
        extra_end = paragraph_end
        for i in range(paragraph_end, min(len(text), paragraph_end + 400)):
            if i < len(text) - 2 and text[i:i+2] == '\n\n':
                extra_end = i
                break
        
        context = text[extra_start:extra_end].strip()
    
    # Clean up
    context = re.sub(r'\s+', ' ', context)
    context = re.sub(r'\n+', ' \n', context)
    
    return context.strip()[:max_length]
def extract_all_dates_aggressive(text: str) -> Dict[str, str]:
    """
    Extract ALL possible dates using aggressive pattern matching on raw text.
    """
    if not text:
        return {}
    
    date_patterns = [
        # Years: 1999, 2000, 2023, etc. (any 4-digit number 1000-2999)
        r'\b(1[0-9]{3}|2[0-9]{3})\b',
        
        # Years in parentheses/brackets: (1999), [2000], (c. 1999)
        r'[\[(](c\.?\s*)?(1[0-9]{3}|2[0-9]{3})[\])]',
        
        # Full dates: January 15, 2023 or 15 January 2023
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*(?:1[0-9]{3}|2[0-9]{3})\b',
        r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+(?:1[0-9]{3}|2[0-9]{3})\b',
        
        # ISO dates: 2023-01-15
        r'\b(?:1[0-9]{3}|2[0-9]{3})-\d{2}-\d{2}\b',
        
        # Slash dates: 01/15/2023, 15/01/2023
        r'\b\d{1,2}/\d{1,2}/(?:1[0-9]{3}|2[0-9]{3})\b',
        
        # Decades: 1990s, 2000s
        r'\b(?:19|20)\d{2}s\b',
        
        # BC/AD dates: 1999 BC, 200 AD
        r'\b(?:1[0-9]{3}|2[0-9]{3})\s*(?:BC|BCE|AD|CE)\b',
        r'\b\d+\s*(?:BC|BCE|AD|CE)\b',
        
        # Circa dates: c. 1999, c.2000
        r'\bc\.?\s*(?:1[0-9]{3}|2[0-9]{3})\b',
        
        # Date ranges: 1999-2000, 1999–2000, 1999–present
        r'\b(?:1[0-9]{3}|2[0-9]{3})[-–](?:1[0-9]{3}|2[0-9]{3}|present)\b',
        
        # Years with punctuation: 1999., 2000;, 2023:
        r'\b(?:1[0-9]{3}|2[0-9]{3})[.,;:]\b',
    ]
    
    
    dates_dict = {}
    processed_regions = []  # Track processed regions to avoid overlaps
    
    # Collect ALL matches from all patterns
    all_matches = {}
    for pattern in date_patterns:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        for match in matches:
            if match.start() not in all_matches:
                all_matches[match.start()] = match
    
    print(f"  - Found {len(all_matches)} raw date matches")
    
    # Process matches in order
    for i, (pos, match) in enumerate(sorted(all_matches.items())):
        # Check if this position overlaps with already processed regions
        overlap = False
        for (start, end) in processed_regions:
            if pos >= start and pos <= end:
                overlap = True
                break
        
        if overlap:
            continue
            
        original_date = match.group()
        normalized_date = normalize_date_aggressive(original_date)
        
        # Use smarter context extraction
        context = extract_extensive_context(text, match.start(), match.end())
        
        if context and len(context.strip()) > 10:
            # Only add if we don't have this normalized date yet
            if normalized_date not in dates_dict:
                dates_dict[normalized_date] = context
                # Mark this region as processed
                processed_regions.append((match.start() - 100, match.end() + 100))
                
                if i < 10:
                    print(f"    - {normalized_date}: {context[:100]}...")
    
    return sort_dates_chronologically(dates_dict)

def get_raw_page_content(page_title: str, language: str = 'en', user_agent: str = 'haas (sharmasuhas450@gmail.com)') -> str:
    """
    Get RAW Wikipedia page content with minimal cleaning.
    """
    headers = {'User-Agent': user_agent}
    url = f"https://{language}.wikipedia.org/w/api.php"
    
    # Get raw wikitext - this contains ALL the content
    params = {
        'action': 'query',
        'titles': page_title,
        'prop': 'revisions',
        'rvprop': 'content',
        'rvslots': '*',
        'format': 'json'
    }
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code != 200:
        raise ValueError(f"Error fetching page: {response.status_code}")
    
    data = response.json()
    pages = data.get('query', {}).get('pages', {})
    
    page_id = next(iter(pages))
    page_data = pages[page_id]
    
    if page_id == '-1' or 'revisions' not in page_data:
        raise ValueError(f"Page '{page_title}' does not exist in {language} Wikipedia")
    
    revisions = page_data['revisions'][0]
    
    # Handle different API response structures
    raw_wikitext = ""
    
    # Method 1: Check for slots with content
    if 'slots' in revisions:
        slots = revisions['slots']
        if 'main' in slots:
            # The content might be in '*' key within the slot
            slot_content = slots['main']
            if '*' in slot_content:
                raw_wikitext = slot_content['*']
            elif 'content' in slot_content:
                raw_wikitext = slot_content['content']
    
    # Method 2: Direct content
    if not raw_wikitext and '*' in revisions:
        raw_wikitext = revisions['*']
    
    # Method 3: Try to extract from any possible location
    if not raw_wikitext:
        # Convert the entire revisions to string and look for content
        import json
        revisions_str = json.dumps(revisions)
        # Try to find wikitext patterns
        if '{{' in revisions_str and '}}' in revisions_str:
            # This is a fallback - might not be perfect but should get some content
            raw_wikitext = revisions_str
    
    if not raw_wikitext:
        raise ValueError("Could not extract page content from API response")
    
    print(f"  - Raw wikitext: {len(raw_wikitext)} characters")
    
    # MINIMAL cleaning - just remove the most disruptive markup
    return clean_wikitext_minimal(raw_wikitext)
def clean_wikitext_minimal(wikitext: str) -> str:
    """
    Minimal cleaning - preserve as much date-containing content as possible.
    """
    text = wikitext
    
    # Remove HTML comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    
    # Remove common Wikipedia templates that don't contain useful content
    text = re.sub(r'{{[Ss]hort description\|[^}]*}}', '', text)
    text = re.sub(r'{{[Ff]or\|[^}]*}}', '', text)
    text = re.sub(r'{{[Uu]se\s+\w+\s+dates\|[^}]*}}', '', text)
    text = re.sub(r'{{[^|{}]*}}', '', text)  # Remove simple templates without parameters
    
    # Remove REF tags but keep the content around them
    text = re.sub(r'<ref[^>]*>.*?</ref>', '', text, flags=re.DOTALL)
    text = re.sub(r'<ref[^>]*/>', '', text)
    
    # Remove specific templates that don't contain useful dates
    text = re.sub(r'{{cite[^}]*}}', ' ', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'{{sfn[^}]*}}', ' ', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'{{efn[^}]*}}', ' ', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove file/image links (they rarely contain useful date context)
    text = re.sub(r'\[\[(File|Image):[^\]]*\]\]', ' ', text, flags=re.IGNORECASE)
    
    # Convert links but KEEP the text content
    text = re.sub(r'\[\[[^\]|]*\|([^\]]*)\]\]', r'\1', text)  # [[link|display]] -> display
    text = re.sub(r'\[\[([^\]|]*)\]\]', r'\1', text)  # [[link]] -> link
    
    # Remove some formatting but keep text
    text = re.sub(r"'''''", ' ', text)
    text = re.sub(r"'''", ' ', text) 
    text = re.sub(r"''", ' ', text)
    
    # Clean up excessive whitespace but keep structure
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ ]{2,}', ' ', text)
    
    print(f"  - After minimal cleaning: {len(text)} characters")
    
    return text


def sort_dates_chronologically(dates_dict: Dict[str, str]) -> Dict[str, str]:
    """
    Sort dates in chronological order.
    """
    def date_sort_key(date_str: str) -> Tuple[int, int, int]:
        try:
            # Handle circa
            if date_str.startswith('c. '):
                date_str = date_str[3:]
            
            # Handle BCE dates
            if 'BCE' in date_str:
                year = int(date_str.replace(' BCE', ''))
                return (-year, 0, 0)
            
            # Handle year only
            year_match = re.search(r'(-?\d{4})', date_str)
            if year_match:
                year = int(year_match.group(1))
                return (year, 0, 0)
            
            return (0, 0, 0)
        except:
            return (0, 0, 0)
    
    sorted_items = sorted(dates_dict.items(), key=lambda x: date_sort_key(x[0]))
    return dict(sorted_items)


# Keep compatibility functions
def extract_dates(text: str) -> List[Dict[str, str]]:
    dates_dict = extract_all_dates_aggressive(text)
    return [{'date': date, 'context': context} for date, context in dates_dict.items()]


def get_complete_page_text(page_title: str, language: str = 'en', user_agent: str = 'haas (sharmasuhas450@gmail.com)') -> str:
    """Compatibility function"""
    return get_raw_page_content(page_title, language, user_agent)


def clean_wikitext(wikitext: str) -> str:
    """Compatibility function"""
    return clean_wikitext_minimal(wikitext)