import re
from typing import Dict, List
import requests
from dateutil import parser
from datetime import datetime

def extract_dates(text: str) -> List[Dict[str, str]]:
    """
    Extract dates from Wikipedia page text using comprehensive pattern matching.
    
    Args:
        text (str): Complete text from Wikipedia page
    
    Returns:
        List[Dict[str, str]]: List of dictionaries containing extracted dates and their context
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
    
    extracted_dates = []
    
    for pattern in date_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # Get some context around the date (50 characters before and after)
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].replace('\n', ' ').strip()
            
            extracted_dates.append({
                'date': match.group(),
                'pattern': pattern,
                'context': context,
                'position': match.start()
            })
    
    # Remove duplicates based on position
    unique_dates = {}
    for date_info in extracted_dates:
        pos = date_info['position']
        if pos not in unique_dates:
            unique_dates[pos] = date_info
    
    return sorted(unique_dates.values(), key=lambda x: x['position'])
