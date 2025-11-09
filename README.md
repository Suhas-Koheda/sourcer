# Wikipedia Date Extractor

A powerful web application that extracts, analyzes, and visualizes chronological information from Wikipedia articles using FastAPI, Gemini AI, and modern web technologies.

## Features

- 🔍 Extract dates from any Wikipedia article
- 📊 Smart date summarization using Google's Gemini AI
- 📑 Support for single and multiple topic searches
- 🌍 Multi-language support (English, Spanish, French, German)
- 📋 Detailed and summarized timeline views
- 📈 Coverage statistics and visualization
- ⚡ Fast and efficient date extraction algorithm
- 🎯 Handles various date formats (BCE/CE, circa dates, ranges)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/suhas-koheda/sourcer.git
cd sourcer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
export GOOGLE_API_KEY="your_google_api_key"  # Required for Gemini AI integration
```

## Usage

1. Start the server:
```bash
uvicorn main:app --reload
```

2. Open your browser and navigate to `http://localhost:8000`

3. Use the application in two ways:
   - **Single Topic Search**: Enter a single Wikipedia topic
   - **Multiple Topics Search**: Enter multiple topics, one per line

## Features in Detail

### Date Extraction
- Supports various date formats:
  - Full dates (e.g., "January 15, 2023")
  - Years (e.g., "1999")
  - BCE/CE dates
  - Circa dates (e.g., "c. 1500")
  - Date ranges (e.g., "1939-1945")
  - Decades (e.g., "1990s")

### Timeline Views
- **Summarized View**: AI-generated concise timeline using Gemini
- **Detailed View**: Complete chronological listing of all extracted dates
- Toggle between views for each topic

### Statistics
- Number of dates found
- Text length analysis
- Coverage metrics
- Visual indicators for data quality

## API Endpoints

### Single Topic
```http
GET /extract-dates/{topic}?language={language}
```

### Multiple Topics
```http
POST /extract-dates-multiple/
Content-Type: application/json

{
    "topics": ["topic1", "topic2"],
    "language": "en"
}
```

### Wikipedia Page Name
```http
GET /wiki-page/{topic}
```

## Project Structure

```
sourcer/
├── main.py              # FastAPI application and routes
├── dates.py            # Date extraction core functionality
├── wiki.py             # Wikipedia API interaction
├── wiki_name.py        # Wikipedia page name resolution
├── llm.py             # Gemini AI integration
├── templates/         
│   └── index.html     # Web interface
└── requirements.txt    # Project dependencies
```

## Dependencies

- FastAPI: Web framework
- Wikipedia-API: Wikipedia content access
- Langchain: AI model integration
- Google Gemini: AI text processing
- Bootstrap 5: Frontend styling
- See `requirements.txt` for complete list

## Development

### Setting up for Development

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Enable development mode:
```bash
uvicorn main:app --reload --debug
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Include docstrings for functions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

- **Author**: Suhas Koheda
- **Email**: sharmasuhas450@gmail.com

## Acknowledgments

- Wikipedia for providing the content API
- Google for the Gemini AI model
- FastAPI for the excellent web framework