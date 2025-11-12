from flask import Flask, render_template, request, jsonify
from helpers import (
    get_location_context,
    chat_with_groq,
    get_all_locations,
    get_real_time_weather
)
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev-secret-key")

@app.route("/")
def index():
    """Serve the chatbot page"""
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Handle chat messages"""
    data = request.json
    user_message = data.get("message", "")
    location = data.get("location", "")
    conversation_history = data.get("history", [])
    
    if not user_message:
        return jsonify({"error": "Empty message"}), 400
    
    location_context = get_location_context(location) if location else None
    bot_response = chat_with_groq(user_message, location_context, conversation_history)
    
    return jsonify({"response": bot_response})

@app.route("/api/locations", methods=["GET"])
def api_locations():
    """Get all available locations"""
    locations = get_all_locations()
    return jsonify(locations)

@app.route("/api/weather/<location>", methods=["GET"])
def api_weather(location):
    """Get real-time weather for a specific location"""
    weather_data = get_real_time_weather(location)
    if weather_data:
        return jsonify(weather_data)
    else:
        return jsonify({"error": f"Weather data not available for {location}"}), 404

if __name__ == "__main__":
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("FLASK_ENV") == "development"
    app.run(host=HOST, port=PORT, debug=DEBUG)
