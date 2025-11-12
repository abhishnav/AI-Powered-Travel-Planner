import requests
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DB_NAME", "travel_db")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
locations_collection = db["locations"]

# Real-time API sources with URLs
REAL_TIME_APIS = {
    "Paris": {
        "lat": 48.8566, "lon": 2.3522, "country": "FR",
        "weather_url": "https://api.open-meteo.com/v1/forecast?latitude=48.8566&longitude=2.3522&current=temperature_2m,weather_code,wind_speed_10m",
        "currency_url": "https://api.exchangerate-api.com/v4/latest/EUR",
        "advisory_url": "https://api.aladhan.com/v1/timings/today?latitude=48.8566&longitude=2.3522"
    },
    "Tokyo": {
        "lat": 35.6762, "lon": 139.6503, "country": "JP",
        "weather_url": "https://api.open-meteo.com/v1/forecast?latitude=35.6762&longitude=139.6503&current=temperature_2m,weather_code,wind_speed_10m",
        "currency_url": "https://api.exchangerate-api.com/v4/latest/JPY",
        "advisory_url": "https://api.aladhan.com/v1/timings/today?latitude=35.6762&longitude=139.6503"
    },
    "New York": {
        "lat": 40.7128, "lon": -74.0060, "country": "US",
        "weather_url": "https://api.open-meteo.com/v1/forecast?latitude=40.7128&longitude=-74.0060&current=temperature_2m,weather_code,wind_speed_10m",
        "currency_url": "https://api.exchangerate-api.com/v4/latest/USD",
        "advisory_url": "https://api.aladhan.com/v1/timings/today?latitude=40.7128&longitude=-74.0060"
    },
    "Barcelona": {
        "lat": 41.3851, "lon": 2.1734, "country": "ES",
        "weather_url": "https://api.open-meteo.com/v1/forecast?latitude=41.3851&longitude=2.1734&current=temperature_2m,weather_code,wind_speed_10m",
        "currency_url": "https://api.exchangerate-api.com/v4/latest/EUR",
        "advisory_url": "https://api.aladhan.com/v1/timings/today?latitude=41.3851&longitude=2.1734"
    },
    "Dubai": {
        "lat": 25.2048, "lon": 55.2708, "country": "AE",
        "weather_url": "https://api.open-meteo.com/v1/forecast?latitude=25.2048&longitude=55.2708&current=temperature_2m,weather_code,wind_speed_10m",
        "currency_url": "https://api.exchangerate-api.com/v4/latest/AED",
        "advisory_url": "https://api.aladhan.com/v1/timings/today?latitude=25.2048&longitude=55.2708"
    },
    "London": {
        "lat": 51.5074, "lon": -0.1278, "country": "GB",
        "weather_url": "https://api.open-meteo.com/v1/forecast?latitude=51.5074&longitude=-0.1278&current=temperature_2m,weather_code,wind_speed_10m",
        "currency_url": "https://api.exchangerate-api.com/v4/latest/GBP",
        "advisory_url": "https://api.aladhan.com/v1/timings/today?latitude=51.5074&longitude=-0.1278"
    },
    "Rome": {
        "lat": 41.9028, "lon": 12.4964, "country": "IT",
        "weather_url": "https://api.open-meteo.com/v1/forecast?latitude=41.9028&longitude=12.4964&current=temperature_2m,weather_code,wind_speed_10m",
        "currency_url": "https://api.exchangerate-api.com/v4/latest/EUR",
        "advisory_url": "https://api.aladhan.com/v1/timings/today?latitude=41.9028&longitude=12.4964"
    },
    "Bangkok": {
        "lat": 13.7563, "lon": 100.5018, "country": "TH",
        "weather_url": "https://api.open-meteo.com/v1/forecast?latitude=13.7563&longitude=100.5018&current=temperature_2m,weather_code,wind_speed_10m",
        "currency_url": "https://api.exchangerate-api.com/v4/latest/THB",
        "advisory_url": "https://api.aladhan.com/v1/timings/today?latitude=13.7563&longitude=100.5018"
    },
    "Sydney": {
        "lat": -33.8688, "lon": 151.2093, "country": "AU",
        "weather_url": "https://api.open-meteo.com/v1/forecast?latitude=-33.8688&longitude=151.2093&current=temperature_2m,weather_code,wind_speed_10m",
        "currency_url": "https://api.exchangerate-api.com/v4/latest/AUD",
        "advisory_url": "https://api.aladhan.com/v1/timings/today?latitude=-33.8688&longitude=151.2093"
    },
    "Amsterdam": {
        "lat": 52.3676, "lon": 4.9041, "country": "NL",
        "weather_url": "https://api.open-meteo.com/v1/forecast?latitude=52.3676&longitude=4.9041&current=temperature_2m,weather_code,wind_speed_10m",
        "currency_url": "https://api.exchangerate-api.com/v4/latest/EUR",
        "advisory_url": "https://api.aladhan.com/v1/timings/today?latitude=52.3676&longitude=4.9041"
    },
    "Singapore": {
        "lat": 1.3521, "lon": 103.8198, "country": "SG",
        "weather_url": "https://api.open-meteo.com/v1/forecast?latitude=1.3521&longitude=103.8198&current=temperature_2m,weather_code,wind_speed_10m",
        "currency_url": "https://api.exchangerate-api.com/v4/latest/SGD",
        "advisory_url": "https://api.aladhan.com/v1/timings/today?latitude=1.3521&longitude=103.8198"
    },
    "Istanbul": {
        "lat": 41.0082, "lon": 28.9784, "country": "TR",
        "weather_url": "https://api.open-meteo.com/v1/forecast?latitude=41.0082&longitude=28.9784&current=temperature_2m,weather_code,wind_speed_10m",
        "currency_url": "https://api.exchangerate-api.com/v4/latest/TRY",
        "advisory_url": "https://api.aladhan.com/v1/timings/today?latitude=41.0082&longitude=28.9784"
    },
    "Las Vegas": {
        "lat": 36.1699, "lon": -115.1398, "country": "US",
        "weather_url": "https://api.open-meteo.com/v1/forecast?latitude=36.1699&longitude=-115.1398&current=temperature_2m,weather_code,wind_speed_10m",
        "currency_url": "https://api.exchangerate-api.com/v4/latest/USD",
        "advisory_url": "https://api.aladhan.com/v1/timings/today?latitude=36.1699&longitude=-115.1398"
    },
    "Vienna": {
        "lat": 48.2082, "lon": 16.3738, "country": "AT",
        "weather_url": "https://api.open-meteo.com/v1/forecast?latitude=48.2082&longitude=16.3738&current=temperature_2m,weather_code,wind_speed_10m",
        "currency_url": "https://api.exchangerate-api.com/v4/latest/EUR",
        "advisory_url": "https://api.aladhan.com/v1/timings/today?latitude=48.2082&longitude=16.3738"
    },
    "Bali": {
        "lat": -8.6705, "lon": 115.2126, "country": "ID",
        "weather_url": "https://api.open-meteo.com/v1/forecast?latitude=-8.6705&longitude=115.2126&current=temperature_2m,weather_code,wind_speed_10m",
        "currency_url": "https://api.exchangerate-api.com/v4/latest/IDR",
        "advisory_url": "https://api.aladhan.com/v1/timings/today?latitude=-8.6705&longitude=115.2126"
    },
    "Miami": {
        "lat": 25.7617, "lon": -80.1918, "country": "US",
        "weather_url": "https://api.open-meteo.com/v1/forecast?latitude=25.7617&longitude=-80.1918&current=temperature_2m,weather_code,wind_speed_10m",
        "currency_url": "https://api.exchangerate-api.com/v4/latest/USD",
        "advisory_url": "https://api.aladhan.com/v1/timings/today?latitude=25.7617&longitude=-80.1918"
    },
    "Berlin": {
        "lat": 52.5200, "lon": 13.4050, "country": "DE",
        "weather_url": "https://api.open-meteo.com/v1/forecast?latitude=52.5200&longitude=13.4050&current=temperature_2m,weather_code,wind_speed_10m",
        "currency_url": "https://api.exchangerate-api.com/v4/latest/EUR",
        "advisory_url": "https://api.aladhan.com/v1/timings/today?latitude=52.5200&longitude=13.4050"
    }
}

# Extended locations with more details
SOURCES = {
    "Paris": {
        "attractions": [
            {"name": "Eiffel Tower", "description": "Iconic iron lattice tower with panoramic views", "rating": 4.7},
            {"name": "Louvre Museum", "description": "World's largest art museum housing Mona Lisa", "rating": 4.6},
            {"name": "Arc de Triomphe", "description": "Monumental arch honoring those who died in war", "rating": 4.5},
            {"name": "Notre-Dame Cathedral", "description": "Historic Gothic cathedral on Ile de la Cite", "rating": 4.6},
            {"name": "Sacre-Coeur", "description": "White-domed basilica with stunning city views", "rating": 4.5}
        ],
        "best_time_to_visit": "April-June, September-October",
        "currency": "EUR (Euro)",
        "language": "French",
        "budget": {
            "daily_budget_low": 80,
            "daily_budget_mid": 150,
            "daily_budget_high": 250,
            "currency": "EUR",
            "notes": "Budget includes accommodation, food, and activities"
        }
    },
    "Tokyo": {
        "attractions": [
            {"name": "Tokyo Tower", "description": "Red communication tower with observation decks", "rating": 4.6},
            {"name": "Senso-ji Temple", "description": "Ancient Buddhist temple in Asakusa district", "rating": 4.7},
            {"name": "Shibuya Crossing", "description": "World's busiest pedestrian crossing", "rating": 4.5},
            {"name": "Meiji Shrine", "description": "Shinto shrine dedicated to Emperor Meiji", "rating": 4.6},
            {"name": "teamLab Borderless", "description": "Digital art museum with immersive installations", "rating": 4.8}
        ],
        "best_time_to_visit": "March-May, September-November",
        "currency": "JPY (Japanese Yen)",
        "language": "Japanese",
        "budget": {
            "daily_budget_low": 70,
            "daily_budget_mid": 140,
            "daily_budget_high": 300,
            "currency": "USD",
            "notes": "Very efficient public transport reduces costs"
        }
    },
    "New York": {
        "attractions": [
            {"name": "Statue of Liberty", "description": "Iconic copper statue symbolizing freedom", "rating": 4.6},
            {"name": "Central Park", "description": "Large urban park with lakes, gardens, and wildlife", "rating": 4.5},
            {"name": "Times Square", "description": "Dazzling commercial and entertainment hub", "rating": 4.3},
            {"name": "Empire State Building", "description": "Historic Art Deco skyscraper with observation deck", "rating": 4.6},
            {"name": "Brooklyn Bridge", "description": "Historic cable-stayed bridge with pedestrian walkway", "rating": 4.7}
        ],
        "best_time_to_visit": "April-May, September-October",
        "currency": "USD (US Dollar)",
        "language": "English",
        "budget": {
            "daily_budget_low": 100,
            "daily_budget_mid": 200,
            "daily_budget_high": 400,
            "currency": "USD",
            "notes": "Expensive accommodation and dining"
        }
    },
    "Barcelona": {
        "attractions": [
            {"name": "Sagrada Familia", "description": "Stunning basilica designed by Antoni Gaudi", "rating": 4.7},
            {"name": "Park Guell", "description": "Colorful park with mosaic tiles and city views", "rating": 4.7},
            {"name": "Gothic Quarter", "description": "Medieval neighborhood with narrow streets", "rating": 4.5},
            {"name": "Casa Batllo", "description": "Modernist building with undulating stone facade", "rating": 4.6},
            {"name": "Las Ramblas", "description": "Famous tree-lined pedestrian street", "rating": 4.4}
        ],
        "best_time_to_visit": "April-May, September-October",
        "currency": "EUR (Euro)",
        "language": "Catalan, Spanish",
        "budget": {
            "daily_budget_low": 70,
            "daily_budget_mid": 130,
            "daily_budget_high": 220,
            "currency": "EUR",
            "notes": "Affordable compared to other European cities"
        }
    },
    "Dubai": {
        "attractions": [
            {"name": "Burj Khalifa", "description": "World's tallest building with observation deck", "rating": 4.6},
            {"name": "Dubai Mall", "description": "World's largest shopping mall", "rating": 4.4},
            {"name": "Palm Jumeirah", "description": "Artificial palm-shaped island with luxury resorts", "rating": 4.5},
            {"name": "Gold Souk", "description": "Traditional market famous for gold jewelry", "rating": 4.3},
            {"name": "Desert Safari", "description": "Adventure through golden sand dunes", "rating": 4.6}
        ],
        "best_time_to_visit": "November-March",
        "currency": "AED (UAE Dirham)",
        "language": "Arabic, English",
        "budget": {
            "daily_budget_low": 120,
            "daily_budget_mid": 200,
            "daily_budget_high": 400,
            "currency": "USD",
            "notes": "Luxury destination with high-end experiences"
        }
    },
    "London": {
        "attractions": [
            {"name": "Big Ben & Houses of Parliament", "description": "Iconic clock tower and government building", "rating": 4.6},
            {"name": "Tower of London", "description": "Historic fortress with Crown Jewels", "rating": 4.6},
            {"name": "Buckingham Palace", "description": "Official residence of the British monarch", "rating": 4.5},
            {"name": "British Museum", "description": "World history museum with Egyptian mummies", "rating": 4.6},
            {"name": "Tower Bridge", "description": "Gothic Revival bascule bridge over Thames", "rating": 4.7}
        ],
        "best_time_to_visit": "May-September",
        "currency": "GBP (British Pound)",
        "language": "English",
        "budget": {
            "daily_budget_low": 90,
            "daily_budget_mid": 170,
            "daily_budget_high": 300,
            "currency": "GBP",
            "notes": "One of Europe's most expensive cities"
        }
    },
    "Rome": {
        "attractions": [
            {"name": "Colosseum", "description": "Ancient Roman amphitheater", "rating": 4.7},
            {"name": "Vatican City", "description": "Independent city-state with St. Peter's Basilica", "rating": 4.7},
            {"name": "Roman Forum", "description": "Archaeological site of ancient ruins", "rating": 4.6},
            {"name": "Trevi Fountain", "description": "Baroque masterpiece where visitors throw coins", "rating": 4.6},
            {"name": "Pantheon", "description": "Ancient Roman temple with oculus dome", "rating": 4.7}
        ],
        "best_time_to_visit": "April-May, September-October",
        "currency": "EUR (Euro)",
        "language": "Italian",
        "budget": {
            "daily_budget_low": 75,
            "daily_budget_mid": 140,
            "daily_budget_high": 250,
            "currency": "EUR",
            "notes": "Good value for accommodation and food"
        }
    },
    "Bangkok": {
        "attractions": [
            {"name": "Grand Palace", "description": "Former royal residence with golden spires", "rating": 4.6},
            {"name": "Wat Pho", "description": "Temple with giant reclining Buddha statue", "rating": 4.7},
            {"name": "Floating Markets", "description": "Traditional markets on canals", "rating": 4.5},
            {"name": "Wat Arun", "description": "Temple of Dawn with ornate towers", "rating": 4.6},
            {"name": "Chatuchak Weekend Market", "description": "World's largest weekend market", "rating": 4.5}
        ],
        "best_time_to_visit": "November-February",
        "currency": "THB (Thai Baht)",
        "language": "Thai",
        "budget": {
            "daily_budget_low": 40,
            "daily_budget_mid": 80,
            "daily_budget_high": 150,
            "currency": "USD",
            "notes": "Very affordable destination with cheap eats and transport"
        }
    },
    "Sydney": {
        "attractions": [
            {"name": "Sydney Opera House", "description": "Iconic performing arts venue with shell design", "rating": 4.7},
            {"name": "Bondi Beach", "description": "Famous beach known for swimming and surfing", "rating": 4.6},
            {"name": "Sydney Harbour Bridge", "description": "Steel arch bridge with scenic walks", "rating": 4.6},
            {"name": "Royal Botanic Gardens", "description": "Beautiful gardens overlooking the harbour", "rating": 4.5},
            {"name": "Blue Mountains", "description": "Mountain range with hiking trails and lookouts", "rating": 4.6}
        ],
        "best_time_to_visit": "September-November, February-April",
        "currency": "AUD (Australian Dollar)",
        "language": "English",
        "budget": {
            "daily_budget_low": 100,
            "daily_budget_mid": 180,
            "daily_budget_high": 300,
            "currency": "AUD",
            "notes": "Moderate to expensive, good value on beaches"
        }
    },
    "Amsterdam": {
        "attractions": [
            {"name": "Anne Frank House", "description": "Historic house where Anne Frank hid during WWII", "rating": 4.7},
            {"name": "Van Gogh Museum", "description": "Museum with world's largest Van Gogh collection", "rating": 4.7},
            {"name": "Canal Cruises", "description": "Boat tours through picturesque canals", "rating": 4.5},
            {"name": "Rijksmuseum", "description": "Dutch art and history museum", "rating": 4.6},
            {"name": "Windmills of Kinderdijk", "description": "Historic windmill village", "rating": 4.6}
        ],
        "best_time_to_visit": "April-May, September",
        "currency": "EUR (Euro)",
        "language": "Dutch, English",
        "budget": {
            "daily_budget_low": 85,
            "daily_budget_mid": 160,
            "daily_budget_high": 280,
            "currency": "EUR",
            "notes": "Bikes reduce transportation costs significantly"
        }
    },
    "Singapore": {
        "attractions": [
            {"name": "Marina Bay Sands", "description": "Iconic hotel with rooftop infinity pool", "rating": 4.7},
            {"name": "Gardens by the Bay", "description": "Futuristic garden with supertree structures", "rating": 4.6},
            {"name": "Sentosa Island", "description": "Resort island with beaches and attractions", "rating": 4.5},
            {"name": "Chinatown Heritage Centre", "description": "Museum preserving Chinese culture", "rating": 4.4},
            {"name": "National Museum of Singapore", "description": "Interactive museum with Singapore's history", "rating": 4.5}
        ],
        "best_time_to_visit": "February-April, July-August",
        "currency": "SGD (Singapore Dollar)",
        "language": "English, Mandarin, Malay, Tamil",
        "budget": {
            "daily_budget_low": 80,
            "daily_budget_mid": 150,
            "daily_budget_high": 280,
            "currency": "USD",
            "notes": "Expensive but efficient and clean"
        }
    },
    "Istanbul": {
        "attractions": [
            {"name": "Blue Mosque", "description": "Ottoman mosque with blue tile decorations", "rating": 4.7},
            {"name": "Hagia Sophia", "description": "Historic Byzantine cathedral turned mosque", "rating": 4.7},
            {"name": "Topkapi Palace", "description": "Former Ottoman sultans' residence", "rating": 4.6},
            {"name": "Grand Bazaar", "description": "One of world's oldest covered markets", "rating": 4.4},
            {"name": "Bosphorus Cruise", "description": "Boat tour between Europe and Asia", "rating": 4.6}
        ],
        "best_time_to_visit": "April-May, September-October",
        "currency": "TRY (Turkish Lira)",
        "language": "Turkish, English",
        "budget": {
            "daily_budget_low": 50,
            "daily_budget_mid": 100,
            "daily_budget_high": 200,
            "currency": "USD",
            "notes": "Great value for food and bazaar shopping"
        }
    },
    "Las Vegas": {
        "attractions": [
            {"name": "The Strip", "description": "Famous boulevard with casinos and hotels", "rating": 4.5},
            {"name": "Bellagio Fountains", "description": "Spectacular water fountain show", "rating": 4.6},
            {"name": "Grand Canyon Tour", "description": "Helicopter tours of natural wonder", "rating": 4.7},
            {"name": "Fremont Street", "description": "Historic downtown with vintage casinos", "rating": 4.3},
            {"name": "Seven Magic Mountains", "description": "Colorful rock formations in desert", "rating": 4.4}
        ],
        "best_time_to_visit": "October-April",
        "currency": "USD (US Dollar)",
        "language": "English",
        "budget": {
            "daily_budget_low": 90,
            "daily_budget_mid": 180,
            "daily_budget_high": 400,
            "currency": "USD",
            "notes": "Gambling and entertainment can inflate costs"
        }
    },
    "Vienna": {
        "attractions": [
            {"name": "Schonbrunn Palace", "description": "Former summer residence of emperors", "rating": 4.7},
            {"name": "St. Stephen's Cathedral", "description": "Gothic cathedral in city center", "rating": 4.6},
            {"name": "Hofburg Palace", "description": "Former winter residence with museums", "rating": 4.5},
            {"name": "Vienna State Opera House", "description": "Historic opera venue with grand architecture", "rating": 4.6},
            {"name": "Belvedere Palace", "description": "Baroque palace with art museum", "rating": 4.6}
        ],
        "best_time_to_visit": "April-May, September-October",
        "currency": "EUR (Euro)",
        "language": "German, English",
        "budget": {
            "daily_budget_low": 80,
            "daily_budget_mid": 150,
            "daily_budget_high": 280,
            "currency": "EUR",
            "notes": "Affordable culture and classical music venues"
        }
    },
    "Bali": {
        "attractions": [
            {"name": "Tanah Lot Temple", "description": "Dramatic coastal temple on rock formation", "rating": 4.7},
            {"name": "Ubud Monkey Forest", "description": "Sacred sanctuary with playful monkeys", "rating": 4.6},
            {"name": "Mount Batur", "description": "Active volcano with sunrise hikes", "rating": 4.7},
            {"name": "Tegallalang Rice Terraces", "description": "Picturesque green rice paddies", "rating": 4.6},
            {"name": "Seminyak Beach", "description": "Popular beach with water sports", "rating": 4.5}
        ],
        "best_time_to_visit": "April-October",
        "currency": "IDR (Indonesian Rupiah)",
        "language": "Indonesian, English",
        "budget": {
            "daily_budget_low": 35,
            "daily_budget_mid": 70,
            "daily_budget_high": 150,
            "currency": "USD",
            "notes": "Extremely affordable with great value temples and beaches"
        }
    },
    "Miami": {
        "attractions": [
            {"name": "Miami Beach", "description": "Iconic beach with Art Deco architecture", "rating": 4.6},
            {"name": "Art Deco Historic District", "description": "Colorful historic buildings from 1923-1943", "rating": 4.5},
            {"name": "Everglades National Park", "description": "Unique wetland ecosystem with wildlife", "rating": 4.6},
            {"name": "Wynwood Walls", "description": "Vibrant street art and murals district", "rating": 4.5},
            {"name": "Vizcaya Museum", "description": "Italian Renaissance-style villa with gardens", "rating": 4.4}
        ],
        "best_time_to_visit": "November-April",
        "currency": "USD (US Dollar)",
        "language": "English, Spanish",
        "budget": {
            "daily_budget_low": 100,
            "daily_budget_mid": 180,
            "daily_budget_high": 350,
            "currency": "USD",
            "notes": "Moderate to expensive with pricey beachfront dining"
        }
    },
    "Berlin": {
        "attractions": [
            {"name": "Brandenburg Gate", "description": "Iconic monument symbolizing German unity", "rating": 4.7},
            {"name": "Berlin Wall Memorial", "description": "Historic Cold War landmark", "rating": 4.6},
            {"name": "Reichstag Building", "description": "Government building with glass dome", "rating": 4.6},
            {"name": "Museum Island", "description": "UNESCO World Heritage site with five museums", "rating": 4.6},
            {"name": "East Side Gallery", "description": "Street art gallery on remaining wall section", "rating": 4.5}
        ],
        "best_time_to_visit": "May-September",
        "currency": "EUR (Euro)",
        "language": "German, English",
        "budget": {
            "daily_budget_low": 70,
            "daily_budget_mid": 130,
            "daily_budget_high": 240,
            "currency": "EUR",
            "notes": "Good value for culture and museums"
        }
    }
}

def get_weather_data(location, weather_url):
    """Fetch real-time weather data from Open-Meteo API"""
    try:
        response = requests.get(weather_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})
        
        return {
            "temperature": current.get("temperature_2m", "N/A"),
            "weather": current.get("weather_code", "N/A"),
            "wind_speed": current.get("wind_speed_10m", "N/A"),
            "timezone": data.get("timezone", ""),
            "source_url": weather_url
        }
    except Exception as e:
        print(f"[-] Weather API error for {location}: {str(e)}")
        return {}

def get_currency_data(currency_url):
    """Fetch real-time currency exchange rates"""
    try:
        response = requests.get(currency_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "rates": data.get("rates", {}),
            "source_url": currency_url
        }
    except Exception as e:
        print(f"[-] Currency API error: {str(e)}")
        return {}

def get_travel_advisories(advisory_url):
    """Fetch travel information using Aladhan API (reliable alternative)"""
    try:
        response = requests.get(advisory_url, timeout=10, verify=False)
        response.raise_for_status()
        data = response.json()
        
        return {
            "data": data.get("data", {}),
            "source_url": advisory_url,
            "status": "Information available"
        }
    except Exception as e:
        print(f"[-] Advisory API error: {str(e)}")
        return {"status": "Unable to fetch", "source_url": advisory_url}

def scrape_and_store_data():
    """Scrape real-time travel data from APIs and store in MongoDB"""
    for location, data in SOURCES.items():
        api_data = REAL_TIME_APIS.get(location, {})
        
        # Get real-time data using URLs
        weather = get_weather_data(location, api_data.get("weather_url", ""))
        currency = get_currency_data(api_data.get("currency_url", ""))
        advisory = get_travel_advisories(api_data.get("advisory_url", ""))
        
        location_doc = {
            "location": location,
            "attractions": data["attractions"],
            "description": f"Complete travel guide for {location}",
            "best_time_to_visit": data.get("best_time_to_visit", "Year-round"),
            "currency": data.get("currency", "Local currency"),
            "language": data.get("language", "Local language"),
            "budget": data.get("budget", {}),
            "real_time_data": {
                "weather": weather,
                "currency_rates": currency,
                "travel_info": advisory,
                "last_updated": datetime.now()
            },
            "coordinates": {
                "latitude": api_data.get("lat"),
                "longitude": api_data.get("lon")
            },
            "updated_at": datetime.now(),
            "tips": [
                f"Book accommodations in advance during peak season in {location}",
                f"Use local public transportation to explore {location}",
                f"Try authentic local cuisine and restaurants in {location}",
                f"Learn basic phrases in the local language before visiting {location}",
                f"Check visa requirements before traveling to {location}"
            ]
        }
        
        locations_collection.update_one(
            {"location": location},
            {"$set": location_doc},
            upsert=True
        )
        print(f"[+] Stored real-time data for {location}")

if __name__ == "__main__":
    scrape_and_store_data()
    print("[+] Real-time data scraping completed!")
    print(f"[+] Total locations stored: {locations_collection.count_documents({})}")
