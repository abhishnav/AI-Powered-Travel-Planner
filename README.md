# Travel Assistant Chatbot

An AI-powered travel planning chatbot that provides personalized itineraries, real-time information, and budget recommendations for travelers worldwide.

## Features

- **Responsive Chatbot UI** - Clean, modern interface that works on desktop and mobile
- **17+ Travel Destinations** - Paris, Tokyo, New York, Barcelona, Dubai, London, Rome, Bangkok, Sydney, Amsterdam, Singapore, Istanbul, Las Vegas, Vienna, Bali, Miami, Berlin
- **Real-Time Data** - Live weather, currency rates, and travel information
- **AI-Powered Responses** - Uses Groq's LLM for intelligent, conversational responses
- **Structured Formatting** - Easy-to-read itineraries, budgets, and recommendations
- **Budget Information** - Daily cost breakdowns for each destination

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **LLM**: Groq API (llama-3.2-90b-text-preview)
- **APIs**: 
  - Open-Meteo (Weather)
  - ExchangeRate-API (Currency)
  - Aladhan API (Location Info)

## Installation

### Prerequisites
- Python 3.8+
- Groq API key

### Setup Steps

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd travel
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Populate database with travel data**
```bash
python scraper.py
```

6. **Run the application**
```bash
python app.py
```

7. **Access the chatbot**
Open your browser and go to `http://localhost:5000`

## Environment Variables

Create a `.env` file with the following:

```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.2-90b-text-preview
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here
HOST=0.0.0.0
PORT=5000
MAX_TOKENS=1024
TEMPERATURE=0.5
```

## Project Structure

```
travel/
├── app.py                 # Main Flask application
├── helpers.py             # Helper functions
├── scraper.py             # Data scraping script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in repo)
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── templates/
│   └── index.html         # Chat UI template
└── static/
    ├── style.css          # Frontend styling
    └── script.js          # Frontend logic
```

## Usage

### Chat with the Assistant

1. Select a destination from the dropdown
2. Type your travel-related question
3. Receive structured, AI-powered recommendations
4. Continue the conversation for more details

### Example Queries

- "Create a 4-day itinerary for Bali"
- "What's the budget for Tokyo?"
- "Best time to visit Barcelona"
- "Tell me about attractions in Rome"
- "How much should I budget for New York?"

## API Endpoints

### GET `/api/locations`
Returns list of available travel destinations

**Response:**
```json
["Paris", "Tokyo", "New York", "Barcelona", ...]
```

### POST `/api/chat`
Send a message and get AI response

**Request:**
```json
{
  "message": "Create a 3-day itinerary for Paris",
  "location": "Paris",
  "history": ["Previous message 1", "Previous message 2"]
}
```

**Response:**
```json
{
  "response": "Day 1: Iconic Landmarks\n- Morning: Visit Eiffel Tower\n..."
}
```

## Response Format

Responses are structured for easy reading:

```
Day 1: [Title]
- Morning: [Activity] (Time)
- Afternoon: [Activity] (Time)
- Evening: [Activity] (Time)
- Estimated cost: $XX - $YY

[Section Name]:
- Item 1: Description
- Item 2: Description

Budget Information:
- Low: $XX/day
- Mid: $XX/day
- High: $XX/day
```

## Database Schema

### Location Document
```json
{
  "_id": ObjectId,
  "location": "Paris",
  "attractions": [
    {
      "name": "Eiffel Tower",
      "description": "Iconic iron lattice tower",
      "rating": 4.7
    }
  ],
  "description": "Complete travel guide for Paris",
  "best_time_to_visit": "April-June, September-October",
  "currency": "EUR (Euro)",
  "language": "French",
  "budget": {
    "daily_budget_low": 80,
    "daily_budget_mid": 150,
    "daily_budget_high": 250,
    "currency": "EUR",
    "notes": "Budget includes accommodation, food, and activities"
  },
  "real_time_data": {
    "weather": {...},
    "currency_rates": {...},
    "travel_info": {...},
    "last_updated": ISODate
  },
  "coordinates": {
    "latitude": 48.8566,
    "longitude": 2.3522
  },
  "tips": [...],
  "updated_at": ISODate
}
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

## Roadmap

- [ ] User authentication
- [ ] Save favorite trips
- [ ] Mobile app (iOS/Android)
- [ ] Interactive map integration
- [ ] Flight and hotel booking
- [ ] User reviews and photos
- [ ] Multi-language support
- [ ] 100+ destination coverage

## Authors

- Your Name - Initial work

## Acknowledgments

- Groq for LLM API
- Open-Meteo for weather data
- ExchangeRate-API for currency rates
- Flask for web framework
