import os

from dates import extract_dates_from_topic

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = " "

from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

def process_gemini(topic:str, language:str='en'):
    data = extract_dates_from_topic(topic, language)
    messages = [
        (
            "system",
            "You are a precise historical event analyzer. "
            "Given dated sentences from Wikipedia, you must create a comprehensive timeline:\n"
            "Rules:\n"
            "1. Process EVERY date mentioned - do not skip any dates\n"
            "2. Keep dates in their original format exactly as they appear\n"
            "3. Merge related events on the same date\n"
            "4. Preserve ALL historical context and details\n"
            "5. Create clear, informative summaries that capture the full context\n"
            "6. NEVER add information not present in the source text\n"
            "7. IMPORTANT: Return ONLY a JSON array with this exact structure:\n"
            '[\n  {"date": "YYYY-MM-DD", "summary": "Detailed event summary with full context"},\n'
            '   {"date": "YYYY", "summary": "Another detailed event"}\n]\n'
            "8. Process dates in chronological order\n"
            "9. Include BCE/CE dates if present\n"
            "10. Include date ranges and approximate dates (c., circa)\n"
            "\n- Return ONLY the JSON array, no other text"
        ),
        (
            "human",
            f"Topic: {data['topic']}\n\nExtracted events:\n" +
            "\n".join(
                [f"- {date}: {context}" for date, context in list(data['dates'].items())[:30]]
            ),
        ),
    ]
    ai_msg = llm.invoke(messages)
    parsed_response=parse_gemini_response(ai_msg)
    return {
            'topic': topic,
            'wikipedia_page': data['wikipedia_page'],
            "text_length": data['text_length'],
            "dates_found": data['dates_found'],
            'dates': data['dates'],
            'parsed_data':parsed_response,
        }
    
def parse_gemini_response(response):
    """Parse and validate the Gemini response into a list of date-summary objects."""
    import json
    
    # Get the raw content from the response
    content = response.content.strip()
    
    # If no content, return empty list
    if not content:
        print("Warning: Empty response from Gemini")
        return []
    
    try:
        # Try to find JSON array in the response if there's surrounding text
        if content.find('[') != 0:  # Response doesn't start with [
            start = content.find('[')
            end = content.rfind(']')
            if start != -1 and end != -1:
                content = content[start:end+1]
            else:
                print(f"Warning: Could not find JSON array in response: {content[:100]}...")
                return []
        
        # Parse the JSON
        events = json.loads(content)
        print(events)
        # Validate the structure
        if not isinstance(events, list):
            print("Warning: Parsed JSON is not an array")
            return []
            
        # Validate and clean each event
        valid_events = []
        for event in events:
            if isinstance(event, dict) and 'date' in event and 'summary' in event:
                valid_events.append({
                    'date': str(event['date']).strip(),
                    'summary': str(event['summary']).strip()
                })
        print(valid_events)
        return valid_events
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse Gemini response: {str(e)}")
        print(f"Response content: {content[:100]}...")
        return []  # Return empty list instead of raising error
    except Exception as e:
        print(f"Warning: Unexpected error parsing Gemini response: {str(e)}")
        return []  # Return empty list instead of raising error