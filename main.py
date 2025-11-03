from typing import Union, List, Dict
from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import wikipediaapi
from dates import extract_dates_from_topic
from wiki_name import get_wikipedia_page_name_from_topic

app = FastAPI()

# Mount static files directory
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
    return {"Hello": "World"}

@app.get("/extract-dates/{topic}")
def get_dates_dict(topic: str, language: str = 'en'):
    """
    GET function to extract dates dictionary from Wikipedia page for a given topic
    Returns: Dictionary with dates as keys and context as values
    """
    try:
        result = extract_dates_from_topic(topic, language)
        
        if 'error' in result:
            raise HTTPException(status_code=404, detail=result['error'])
        
        return {
            "topic": result['topic'],
            "wikipedia_page": result['wikipedia_page'],
            "text_length": result['text_length'],
            "dates_found": result['dates_found'],
            "dates": result['dates']  # This is the dates dictionary (date -> context)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

from pydantic import BaseModel

class TopicsRequest(BaseModel):
    topics: List[str]
    language: str = 'en'

@app.post("/extract-dates-multiple/")
def extract_dates_multiple_topics(request: TopicsRequest):
    """
    POST function to extract dates from multiple topics
    Request body should contain:
    {
        "topics": ["topic1", "topic2", ...],
        "language": "en"  # optional, defaults to 'en'
    }
    """
    try:
        results = []
        
        for topic in request.topics:
            result = extract_dates_from_topic(topic, request.language)
            results.append(result)
            
            # Small delay to be respectful to APIs
            import time
            time.sleep(1)
        
        return {
            "total_topics": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/wiki-page/{topic}")
def get_wiki_page_name(topic: str):
    """
    GET function to get Wikipedia page name for a topic
    """
    try:
        page_name = get_wikipedia_page_name_from_topic(topic)
        return {
            "topic": topic,
            "wikipedia_page": page_name
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Wikipedia page not found: {str(e)}")

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