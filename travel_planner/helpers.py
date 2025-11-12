from groq import Groq
import os
from dotenv import load_dotenv
import re
import json
import requests
from datetime import datetime

load_dotenv()

# Load locations from JSON file
def load_locations_from_json():
    """Load all locations from locations.json file"""
    try:
        with open('locations.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("[-] locations.json not found!")
        return {}

locations_data = load_locations_from_json()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.2-90b-text-preview")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1024))
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.5))

# Weather code descriptions
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

def get_real_time_weather(location_name):
    """Fetch real-time weather for a specific location"""
    location = locations_data.get(location_name)
    if not location:
        return None
    
    # Get coordinates from location data
    coords = location.get("coordinates", {})
    if not coords.get("latitude") or not coords.get("longitude"):
        return None
    
    lat = coords["latitude"]
    lon = coords["longitude"]
    
    try:
        # Fetch current weather from Open-Meteo API (free, no API key needed)
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,weather_code,is_day"
        
        response = requests.get(weather_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        current = data.get("current", {})
        weather_code = current.get("weather_code", 0)
        
        weather_info = {
            "location": location_name,
            "temperature": current.get("temperature_2m", "N/A"),
            "temperature_unit": data.get("current_units", {}).get("temperature_2m", "°C"),
            "humidity": current.get("relative_humidity_2m", "N/A"),
            "weather_description": WEATHER_CODES.get(weather_code, "Unknown"),
            "weather_code": weather_code,
            "wind_speed": current.get("wind_speed_10m", "N/A"),
            "wind_unit": data.get("current_units", {}).get("wind_speed_10m", "km/h"),
            "is_day": current.get("is_day", True),
            "timezone": data.get("timezone", ""),
            "timestamp": datetime.now().isoformat(),
            "coordinates": {
                "latitude": lat,
                "longitude": lon
            }
        }
        
        return weather_info
    except Exception as e:
        print(f"[-] Weather API error for {location_name}: {str(e)}")
        return None


def get_location_context(location_name):
    """Fetch location data from JSON file"""
    # Search case-insensitively through locations
    for location_key, location_doc in locations_data.items():
        if location_key.lower() == location_name.lower():
            return location_doc
    return None


def analyze_query_type(user_message):
    """Analyze user message to determine query type"""
    message_lower = user_message.lower()
    
    # Itinerary patterns
    itinerary_keywords = ['plan', 'itinerary', 'day trip', 'days', 'schedule', 'agenda', 'what should i do', 'what to do']
    
    # Budget patterns
    budget_keywords = ['budget', 'cost', 'price', 'expensive', 'how much', 'afford', 'spend', 'money']
    
    # Attraction patterns
    attraction_keywords = ['attraction', 'visit', 'see', 'place', 'spot', 'museum', 'temple', 'church', 'monument', 'must-see', 'best places']
    
    # Time patterns
    time_keywords = ['when', 'best time', 'season', 'weather', 'climate', 'rain', 'hot', 'cold', 'month']
    
    # Practical patterns
    practical_keywords = ['transport', 'getting around', 'taxi', 'train', 'bus', 'flight', 'food', 'eat', 'restaurant', 'language', 'culture', 'tip']
    
    # Activity patterns
    activity_keywords = ['adventure', 'relax', 'family', 'couple', 'solo', 'nightlife', 'beach', 'hiking', 'shopping', 'dining']
    
    # Count matching keywords
    query_scores = {
        'itinerary': sum(1 for keyword in itinerary_keywords if keyword in message_lower),
        'budget': sum(1 for keyword in budget_keywords if keyword in message_lower),
        'attraction': sum(1 for keyword in attraction_keywords if keyword in message_lower),
        'time': sum(1 for keyword in time_keywords if keyword in message_lower),
        'practical': sum(1 for keyword in practical_keywords if keyword in message_lower),
        'activity': sum(1 for keyword in activity_keywords if keyword in message_lower)
    }
    
    # Return most likely query type
    if max(query_scores.values()) == 0:
        return 'general'
    
    return max(query_scores, key=query_scores.get)


def extract_duration(user_message):
    """Extract number of days from user message"""
    # Look for patterns like "3 days", "3-day", "3day", etc.
    match = re.search(r'(\d+)\s*-?\s*day', user_message.lower())
    if match:
        return int(match.group(1))
    return None


def is_travel_query(user_message):
    """Check if message is travel-related or casual/greeting"""
    message_lower = user_message.lower().strip()
    
    # If message is too short and casual, it's not a travel query
    if len(message_lower) < 5:
        return False
    
    # Casual/greeting phrases that should be redirected (exact matches or at start/end)
    casual_phrases = [
        'thank you', 'thanks', 'thx',
        'hello', 'hi', 'hey', 
        'bye', 'goodbye', 'see you', 
        'ok', 'okay', 'sure', 'cool', 'nice', 'great', 'awesome',
        'sorry', 'please',
        'how are you', 'what\'s up',
        'lol', 'haha'
    ]
    
    # Travel-related keywords that MUST be present
    travel_keywords = [
        'trip', 'visit', 'travel', 'plan', 'itinerary', 'day', 'days', 'budget', 'cost',
        'attraction', 'hotel', 'restaurant', 'food', 'eat', 'transport', 'train',
        'flight', 'taxi', 'bus', 'weather', 'season', 'when', 'where',
        'what to do', 'what to see', 'best', 'place', 'places', 'activity', 'adventure',
        'accommodation', 'stay', 'tour', 'guide', 'explore', 'discover',
        'temple', 'museum', 'beach', 'mountain', 'culture', 'language',
        'itinerary', 'schedule', 'agenda', 'things to do', 'must see', 'must-see'
    ]
    
    # Check if message matches casual phrases
    is_casual = any(message_lower == phrase or 
                   message_lower.startswith(phrase + ' ') or 
                   message_lower.endswith(' ' + phrase)
                   for phrase in casual_phrases)
    
    # Check if message contains travel keywords
    has_travel_keyword = any(keyword in message_lower for keyword in travel_keywords)
    
    # If it's a casual phrase without travel keywords, reject it
    if is_casual and not has_travel_keyword:
        return False
    
    # If it has travel keywords, accept it
    if has_travel_keyword:
        return True
    
    # If message is very short (casual greeting length), reject
    if len(message_lower) < 8 and not has_travel_keyword:
        return False
    
    # Otherwise, let LLM handle it
    return True


def get_redirect_message(location, user_message):
    """Get redirect message for non-travel queries"""
    message_lower = user_message.lower().strip()

    # Special handling for thank you messages - just acknowledge briefly
    thank_you_phrases = ['thank you', 'thanks', 'thx', 'appreciate']
    if any(phrase in message_lower for phrase in thank_you_phrases):
        if location:
            return f"You're welcome! Feel free to ask me anything else about your {location} trip."
        else:
            return "You're welcome! Select a destination and I'll help you plan your trip."

    # For other casual messages, give the full redirect
    if location:
        return f"I'm here to help you plan your {location} trip! What would you like to know?\n\nI can help with:\n- Creating day-by-day itineraries\n- Budget planning\n- Attraction recommendations\n- Best time to visit\n- Practical travel tips\n\nWhat aspect of your {location} trip would you like help with?"
    else:
        return "I'm your travel planning assistant! Please select a destination first, then ask me about:\n\n- Itineraries and what to do\n- Budget and costs\n- Attractions and places to visit\n- Best time to travel\n- Travel logistics and tips\n\nWhich destination would you like to explore?"


def build_system_prompt(location_context):
    """Build system prompt with location data and structured output format"""
    if location_context:
        attractions = "\n".join([f"- {a['name']}: {a['description']} (Rating: {a.get('rating', 'N/A')})" 
                                for a in location_context.get("attractions", [])])
        tips = "\n".join([f"- {tip}" for tip in location_context.get("tips", [])])
        budget_info = location_context.get("budget", {})
        
        budget_text = f"""
BUDGET REFERENCE FOR {location_context.get('location', '').upper()}:
- Budget Low: ${budget_info.get('daily_budget_low', 'N/A')}/day (hostels, street food, free attractions)
- Budget Mid: ${budget_info.get('daily_budget_mid', 'N/A')}/day (mid-range hotels, local restaurants, paid attractions)
- Budget High: ${budget_info.get('daily_budget_high', 'N/A')}/day (luxury hotels, fine dining, premium experiences)
- Notes: {budget_info.get('notes', 'N/A')}
"""
        
        return f"""You are a professional TRAVEL PLANNING ASSISTANT SPECIALIZED IN {location_context.get('location', '').upper()}.

IMPORTANT BEHAVIOR RULES:
1. NEVER respond to casual greetings like "thanks", "hi", "hello", "ok", "cool"
2. NEVER say things like "You're welcome!" or "Can I help with anything else?"
3. NEVER engage in chitchat or small talk
4. ALWAYS redirect non-travel messages back to travel planning
5. FOCUS EXCLUSIVELY on travel-related assistance for {location_context.get('location', '')}

IF USER SENDS CASUAL MESSAGE (thanks, hello, hi, ok, great, cool, etc.):
RESPOND WITH: "I'm here to help you plan your {location_context.get('location', '')} trip! What would you like to know? I can help with itineraries, budgets, attractions, and travel tips."

IF USER SENDS OFF-TOPIC MESSAGE:
RESPOND WITH: "Let's focus on your {location_context.get('location', '')} trip! What aspect would you like help with? Itinerary planning, budget, attractions, or practical travel tips?"

ONLY provide detailed responses to ACTUAL TRAVEL QUERIES.

{location_context.get('location', '').upper()} EXPERTISE:

Location: {location_context.get('location', '')}

ATTRACTIONS IN {location_context.get('location', '').upper()}:
{attractions}

TRAVEL TIPS FOR {location_context.get('location', '').upper()}:
{tips}

LOCATION FACTS:
- Best Time to Visit: {location_context.get('best_time_to_visit', 'N/A')}
- Currency: {location_context.get('currency', 'N/A')}
- Language: {location_context.get('language', 'N/A')}

{budget_text}

YOUR RESPONSIBILITIES:
1. ANALYZE the user's query carefully
2. IF NOT TRAVEL-RELATED: Redirect politely to travel planning
3. IF TRAVEL-RELATED: Provide detailed, structured information
4. PROVIDE specific details from the location database
5. FORMAT all responses using structured lists

QUERY TYPE HANDLING:

TYPE 1: ITINERARY REQUEST (keywords: plan, itinerary, days, schedule, what to do)
ACTION: Create day-by-day itinerary
FORMAT:
Day 1: [Title describing main theme/focus]
- Morning (8:00 AM): [Specific attraction/activity with brief description]
- Afternoon (1:00 PM): [Specific attraction/activity with brief description]
- Evening (6:00 PM): [Specific attraction/activity with brief description]
- Meals: [Suggested cuisine type or restaurant style]
- Day total cost: $XX-YY

TYPE 2: BUDGET QUESTION (keywords: budget, cost, price, how much, expensive)
ACTION: Provide detailed cost breakdown
FORMAT:
Budget Analysis for [number] Days in {location_context.get('location', '')}:
- Accommodation: $XX/night × [days] = $XXX total
- Food: $XX/day × [days] = $XXX total
- Transportation: $XX/day × [days] = $XXX total
- Activities: $XX/day × [days] = $XXX total
- TOTAL ESTIMATED COST: $XXX-XXX

Budget Tips:
- [Money-saving tip 1]
- [Money-saving tip 2]

TYPE 3: ATTRACTION QUESTION (keywords: attraction, visit, place, spot, must-see, best places)
ACTION: Describe attractions with practical details
FORMAT:
[Attraction Name]:
- What: Brief description of what it is
- Why Visit: Why it's worth going
- Best Time: When to visit (time of day/season)
- Duration: How long to spend (XX minutes/hours)
- Cost: Entry fee or price range ($XX)
- Accessibility: How to get there
- Insider Tip: One practical advice for visiting

TYPE 4: TIME/SEASON QUESTION (keywords: when, best time, season, weather, climate)
ACTION: Explain seasonal information
FORMAT:
Best Time to Visit {location_context.get('location', '')}:
- Ideal Season: [Season name and months]
  Weather: [Description]
  Crowds: [Crowd level]
  Price: [Relative cost]
  Why Visit: [Reasons]

- Alternative Season: [Season name and months]
  Weather: [Description]
  Avoid: [Why to avoid if applicable]

TYPE 5: PRACTICAL QUESTION (keywords: transport, food, language, culture, tips)
ACTION: Provide practical travel information
FORMAT:
[Topic - e.g., Transportation/Food/Language]:
- [Specific advice 1]: [Details]
- [Specific advice 2]: [Details]
- [Specific advice 3]: [Details]

Important Notes:
- [Key practical tip]
- [Safety or cultural consideration]

TYPE 6: ACTIVITY/INTEREST QUESTION (keywords: adventure, relax, family, couple, beach, hiking)
ACTION: Recommend activities matching interests
FORMAT:
[Interest Type] Activities in {location_context.get('location', '')}:
- [Activity 1]: [Description, duration, cost, location]
- [Activity 2]: [Description, duration, cost, location]
- [Activity 3]: [Description, duration, cost, location]

CRITICAL FORMATTING RULES:
1. ALWAYS use headers with colons (Day 1:, Accommodation:, Attraction Name:)
2. ALWAYS use bullet points with hyphens (-) for lists
3. ALWAYS include specific numbers (prices, times, ratings, distances)
4. KEEP bullet points short (1-2 lines maximum)
5. SEPARATE sections with blank lines
6. NEVER write long paragraphs - use structured lists only
7. REFERENCE attractions from the database provided above
8. INCLUDE costs in the specified currency ({location_context.get('currency', 'USD')})
9. PROVIDE estimated duration for each activity
10. ASK clarifying questions if details are missing (number of days, budget level, travel style)

WHEN TO ASK CLARIFYING QUESTIONS:
- If itinerary request doesn't specify number of days: "How many days will you be in {location_context.get('location', '')}?"
- If budget question doesn't specify duration: "How many days are you planning to stay?"
- If activity question doesn't specify interest type: "What type of activities interest you? (adventure, relaxation, culture, family-friendly, etc.)"
- If query is vague: Ask for 1-2 clarifying details, then provide response

RESPONSE QUALITY CHECKLIST:
✓ Matches user's query type exactly
✓ Uses only attractions from the database
✓ Includes specific numbers and costs
✓ Formatted with headers and bullet points
✓ Practical and actionable information
✓ Appropriate for {location_context.get('location', '')} specifically
✓ No generic travel advice - only {location_context.get('location', '')}-specific

Be professional, helpful, and SPECIFIC to {location_context.get('location', '')}. 
Never provide generic travel advice. Always reference the location database."""
    else:
        return """You are a professional TRAVEL PLANNING ASSISTANT.

ANALYZE USER QUERIES and respond with appropriate travel information.

QUERY TYPES:
- Itinerary: Create day-by-day plans
- Budget: Provide cost breakdowns
- Attractions: Describe places to visit
- Best Time: Explain seasonal info
- Practical: Give travel logistics advice
- Activities: Recommend based on interests

RESPONSE FORMAT:
[Header]:
- Item 1: Details
- Item 2: Details

RULES:
1. Use headers with colons
2. Use bullet points with hyphens
3. Include specific numbers
4. Keep items short (max 2 lines)
5. Never write paragraphs
6. Ask clarifying questions if needed

Be professional and helpful."""


def chat_with_groq(user_message, location_context, conversation_history):
    """Send message to Groq and get response"""

    # Check if it's a travel-related query
    if not is_travel_query(user_message):
        # Return redirect message instead of calling LLM
        location_name = location_context.get('location') if location_context else None
        return get_redirect_message(location_name, user_message)

    system_prompt = build_system_prompt(location_context)
    
    messages = [{"role": "user", "content": msg} for msg in conversation_history]
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "system", "content": system_prompt}] + messages,
            max_tokens=MAX_TOKENS,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


def get_all_locations():
    """Get all available locations from JSON file"""
    return list(locations_data.keys())
