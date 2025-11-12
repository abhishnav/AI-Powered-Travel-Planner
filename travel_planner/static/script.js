const chatMessages = document.getElementById("chatMessages");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const locationSelect = document.getElementById("location");
const weatherBadge = document.getElementById("weatherBadge");

let conversationHistory = [];
let currentWeather = null;

// Load locations on page load
window.addEventListener("load", loadLocations);

// Event listeners
sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

locationSelect.addEventListener("change", (e) => {
    if (e.target.value) {
        // Clear chat and start fresh for new location
        clearChat();
        loadWeather(e.target.value);

        // Show welcome message for the new location
        addMessage(`Great! I'm ready to help you plan your ${e.target.value} trip. What would you like to know?`, "bot");
    } else {
        hideWeatherBadge();
        clearChat();
    }
});

async function loadLocations() {
    try {
        const response = await fetch("/api/locations");
        const locations = await response.json();
        locations.forEach(location => {
            const option = document.createElement("option");
            option.value = location;
            option.textContent = location;
            locationSelect.appendChild(option);
        });
    } catch (error) {
        console.error("Error loading locations:", error);
    }
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    const location = locationSelect.value;

    // Disable send button while processing
    sendBtn.disabled = true;
    userInput.disabled = true;

    // Add user message to UI
    addMessage(message, "user");
    userInput.value = "";
    conversationHistory.push(message);

    // Show loading indicator
    showLoadingIndicator();

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: message,
                location: location,
                history: conversationHistory
            })
        });

        const data = await response.json();
        removeLoadingIndicator();

        if (data.response) {
            addMessage(data.response, "bot");
        } else {
            addMessage("Error: Unable to get response", "bot");
        }
    } catch (error) {
        removeLoadingIndicator();
        addMessage("Connection error. Please try again.", "bot");
        console.error("Error:", error);
    } finally {
        // Re-enable send button
        sendBtn.disabled = false;
        userInput.disabled = false;
        userInput.focus();
    }
}

function addMessage(text, sender) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}`;

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    // Use markdown rendering for bot messages
    if (sender === "bot") {
        contentDiv.innerHTML = formatMarkdown(text);

        // Add copy button for bot messages
        const copyBtn = document.createElement("button");
        copyBtn.className = "copy-btn";
        copyBtn.innerHTML = "📋";
        copyBtn.title = "Copy to clipboard";
        copyBtn.onclick = () => copyToClipboard(text, copyBtn);
        messageDiv.appendChild(copyBtn);
    } else {
        contentDiv.textContent = text;
    }

    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Copy message to clipboard
function copyToClipboard(text, button) {
    navigator.clipboard.writeText(text).then(() => {
        const originalHTML = button.innerHTML;
        button.innerHTML = "✓";
        button.style.background = "#4caf50";
        setTimeout(() => {
            button.innerHTML = originalHTML;
            button.style.background = "";
        }, 2000);
    }).catch(err => {
        console.error("Failed to copy:", err);
    });
}

// Simple markdown formatter for better text display
function formatMarkdown(text) {
    let html = text;

    // Escape HTML to prevent XSS
    html = html.replace(/&/g, '&amp;')
               .replace(/</g, '&lt;')
               .replace(/>/g, '&gt;');

    // Headers (Day 1:, Budget:, etc.)
    html = html.replace(/^([A-Za-z0-9\s]+:)$/gm, '<h3>$1</h3>');
    html = html.replace(/^(Day \d+:.*?)$/gm, '<h3>$1</h3>');

    // Bold text (**text** or __text__)
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/__(.+?)__/g, '<strong>$1</strong>');

    // Italic text (*text* or _text_)
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    html = html.replace(/_(.+?)_/g, '<em>$1</em>');

    // Convert bullet points (- item)
    const lines = html.split('\n');
    let inList = false;
    let result = [];

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trim();

        if (trimmed.startsWith('- ')) {
            if (!inList) {
                result.push('<ul>');
                inList = true;
            }
            result.push('<li>' + trimmed.substring(2) + '</li>');
        } else {
            if (inList) {
                result.push('</ul>');
                inList = false;
            }
            result.push(line);
        }
    }

    if (inList) {
        result.push('</ul>');
    }

    html = result.join('\n');

    // Convert line breaks to <br> (but not inside lists or headers)
    html = html.replace(/\n(?!<)/g, '<br>');

    // Highlight costs/prices ($XX-XX or $XX)
    html = html.replace(/(\$\d+(?:-\d+)?)/g, '<span class="cost-badge">$1</span>');

    return html;
}

function showLoadingIndicator() {
    const messageDiv = document.createElement("div");
    messageDiv.className = "message bot";
    messageDiv.id = "loadingIndicator";

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";
    contentDiv.innerHTML = '<span class="loading"></span><span class="loading"></span><span class="loading"></span>';

    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeLoadingIndicator() {
    const indicator = document.getElementById("loadingIndicator");
    if (indicator) indicator.remove();
}

// Weather badge functionality
async function loadWeather(location) {
    try {
        const response = await fetch(`/api/weather/${encodeURIComponent(location)}`);

        if (response.ok) {
            const weather = await response.json();
            currentWeather = weather;
            displayWeatherBadge(weather);
        } else {
            hideWeatherBadge();
        }
    } catch (error) {
        console.error("Error loading weather:", error);
        hideWeatherBadge();
    }
}

function displayWeatherBadge(weather) {
    if (!weatherBadge) return;

    const weatherIcon = getWeatherIcon(weather.weather_code, weather.is_day);
    const tempColor = getTempColor(weather.temperature);

    weatherBadge.innerHTML = `
        <div class="weather-info">
            <div class="weather-icon">${weatherIcon}</div>
            <div class="weather-details">
                <div class="weather-location">${weather.location}</div>
                <div class="weather-temp" style="color: ${tempColor}">
                    ${Math.round(weather.temperature)}${weather.temperature_unit}
                </div>
                <div class="weather-desc">${weather.weather_description}</div>
            </div>
            <div class="weather-extras">
                <div class="weather-extra-item">
                    <span class="extra-icon">💧</span>
                    <span>${weather.humidity}%</span>
                </div>
                <div class="weather-extra-item">
                    <span class="extra-icon">💨</span>
                    <span>${Math.round(weather.wind_speed)} ${weather.wind_unit}</span>
                </div>
            </div>
        </div>
    `;
    weatherBadge.style.display = 'block';
}

function hideWeatherBadge() {
    if (weatherBadge) {
        weatherBadge.style.display = 'none';
        currentWeather = null;
    }
}

function getWeatherIcon(weatherCode, isDay) {
    const icons = {
        0: isDay ? '☀️' : '🌙',      // Clear
        1: isDay ? '🌤️' : '🌙',      // Mainly clear
        2: '⛅',                       // Partly cloudy
        3: '☁️',                       // Overcast
        45: '🌫️',                      // Fog
        48: '🌫️',                      // Fog
        51: '🌦️',                      // Drizzle
        53: '🌦️',
        55: '🌧️',
        61: '🌧️',                      // Rain
        63: '🌧️',
        65: '⛈️',
        71: '🌨️',                      // Snow
        73: '🌨️',
        75: '❄️',
        77: '❄️',
        80: '🌦️',                      // Showers
        81: '🌧️',
        82: '⛈️',
        85: '🌨️',
        86: '❄️',
        95: '⛈️',                      // Thunderstorm
        96: '⛈️',
        99: '⛈️'
    };
    return icons[weatherCode] || '🌤️';
}

function getTempColor(temp) {
    if (temp >= 30) return '#ff5722';      // Hot - red
    if (temp >= 20) return '#ff9800';      // Warm - orange
    if (temp >= 10) return '#4caf50';      // Mild - green
    if (temp >= 0) return '#2196f3';       // Cool - blue
    return '#9c27b0';                       // Cold - purple
}

// Clear chat messages and conversation history
function clearChat() {
    chatMessages.innerHTML = '';
    conversationHistory = [];
}
