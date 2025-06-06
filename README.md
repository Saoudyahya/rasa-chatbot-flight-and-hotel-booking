# 🌍 Arabic Travel Agency Chatbot

[![Rasa Version](https://img.shields.io/badge/Rasa-3.6-blue.svg)](https://rasa.com/)
[![Python Version](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Demo](https://img.shields.io/badge/Demo-Live-red.svg)](https://arabic-travel-chatbot.herokuapp.com)

> An intelligent Arabic travel booking chatbot with interactive web interface and real-time map integration

![Main Interface](docs/images/main-interface.png)

## 🚀 Features

### 🤖 **Intelligent Conversational AI**
- **Arabic Language Support** - Native RTL interface and NLU
- **Context-Aware Booking** - Distinguishes between hotel and flight bookings
- **Natural Language Understanding** - Powered by Rasa framework
- **Persistent Conversations** - Chat history maintained across sessions

### 🗺️ **Interactive Maps**
- **Flight Route Visualization** - Dynamic flight paths with departure/arrival markers
- **Hotel Location Mapping** - Multiple hotel properties with detailed information
- **Real-time Interaction** - Click-to-book functionality from map popups
- **Leaflet.js Integration** - Smooth, responsive mapping experience

### 💻 **Modern Web Interface**
- **Responsive Design** - Works seamlessly on desktop, tablet, and mobile
- **Glassmorphism UI** - Modern design with backdrop filters and gradients
- **Real-time Chat** - Instant messaging with typing indicators
- **Quick Actions** - Pre-defined buttons for common queries

### 🔧 **Advanced Features**
- **Error Handling** - Graceful degradation with automatic retry mechanisms
- **Loading States** - Visual feedback during processing
- **Connection Status** - Real-time connection monitoring
- **Session Management** - Automatic session restoration

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 14+ (for web interface)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/username/arabic-travel-chatbot.git
cd arabic-travel-chatbot
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install Rasa and dependencies
pip install -r requirements.txt

# Install Rasa
pip install rasa
```

### 4. Train the Model

```bash
# Train the Rasa model
rasa train

# Test the NLU
rasa shell nlu
```

## 🚀 Quick Start

### 1. Start Rasa Server

```bash
# Terminal 1: Start Rasa server
rasa run --enable-api --cors "*" --debug

# Terminal 2: Start action server (if using custom actions)
rasa run actions
```

### 2. Launch Web Interface

```bash
# Terminal 3: Start web server
cd web-interface
python -m http.server 8080
# Or use any static file server
```

### 3. Access the Application

Open your browser and navigate to:
- **Web Interface:** `http://localhost:8080`
- **Rasa API:** `http://localhost:5005`

## 📁 Project Structure

```
arabic-travel-chatbot/
├── 📁 data/
│   ├── nlu.yml              # NLU training data in Arabic
│   ├── stories.yml          # Conversation flows
│   └── rules.yml            # Conversation rules
├── 📁 actions/
│   ├── __init__.py
│   └── actions.py           # Custom action implementations
├── 📁 web-interface/
│   ├── index.html           # Main web interface
│   ├── style.css            # Styling (included in HTML)
│   └── script.js            # JavaScript logic (included in HTML)
├── 📁 models/               # Trained Rasa models
├── 📁 tests/
│   ├── test_stories.yml     # Test conversations
│   └── conversation_tests.yml
├── 📁 docs/
│   ├── images/              # Screenshots and diagrams
│   └── api.md               # API documentation
├── config.yml               # Rasa pipeline configuration
├── domain.yml               # Domain definition
├── endpoints.yml            # Endpoint configuration
├── credentials.yml          # Channel credentials
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Docker setup
└── README.md               # This file
```

## ⚙️ Configuration

### Domain Configuration (`domain.yml`)

```yaml
version: "3.1"

intents:
  - greet
  - book_flight
  - book_hotel
  - confirm_booking
  - deny
  - affirm
  - ask_map

entities:
  - city
  - date
  - hotel_name
  - price

slots:
  departure_city:
    type: text
    mappings:
    - type: from_entity
      entity: city
  
  arrival_city:
    type: text
    mappings:
    - type: from_entity
      entity: city

responses:
  utter_greet:
    - text: "مرحباً! كيف يمكنني مساعدتك في حجز رحلتك؟"
  
  utter_ask_destination:
    - text: "إلى أين تريد السفر؟"

actions:
  - action_search_flights
  - action_search_hotels
  - action_show_map
```

### Pipeline Configuration (`config.yml`)

```yaml
version: "3.1"

pipeline:
  - name: WhitespaceTokenizer
  - name: RegexFeaturizer
  - name: LexicalSyntacticFeaturizer
  - name: CountVectorsFeaturizer
  - name: CountVectorsFeaturizer
    analyzer: char_wb
    min_ngram: 1
    max_ngram: 4
  - name: DIETClassifier
    epochs: 100
  - name: EntitySynonymMapper
  - name: ResponseSelector
    epochs: 100

policies:
  - name: MemoizationPolicy
  - name: TEDPolicy
    max_history: 5
    epochs: 100
  - name: RulePolicy
```

## 🎯 Usage

### Basic Conversation Flow

1. **Greeting**
   ```
   User: مرحبا
   Bot: مرحباً! كيف يمكنني مساعدتك في حجز رحلتك؟
   ```

2. **Flight Booking**
   ```
   User: أريد رحلة من الدار البيضاء إلى باريس
   Bot: رائع! وجدت رحلات متاحة من الدار البيضاء إلى باريس
   [Map button appears: عرض مسار الرحلة]
   ```

3. **Hotel Search**
   ```
   User: أريد فنادق في مراكش
   Bot: إليك أفضل الفنادق في مراكش:
   [Map button appears: عرض موقع الفنادق]
   ```

4. **Map Interaction**
   - Click map buttons to view interactive locations
   - Click hotel markers to see details and book
   - View flight routes with departure/arrival information

### Quick Action Buttons

The interface provides quick action buttons for common queries:

- 🛩️ **حجز رحلة** - Book Flight
- 🏨 **حجز فندق** - Book Hotel  
- 🗺️ **فنادق مراكش** - Hotels in Marrakech
- ✈️ **رحلة باريس** - Flight to Paris
- ✅ **تأكيد الفندق/الرحلة** - Confirm Booking (context-aware)

## 🔗 API Documentation

### Rasa Webhook Endpoint

**POST** `/webhooks/rest/webhook`

```json
{
  "sender": "user_123",
  "message": "أريد حجز فندق في مراكش"
}
```

**Response:**
```json
[
  {
    "text": "إليك أفضل الفنادق في مراكش",
    "buttons": [
      {
        "title": "فندق الأطلس",
        "payload": "select_hotel_atlas"
      }
    ]
  }
]
```

### Custom Actions

#### `action_search_flights`
- Searches for available flights between cities
- Returns flight options with prices and times

#### `action_search_hotels`
- Finds hotels in specified city
- Provides hotel details and booking options

#### `action_show_map`
- Triggers map display in frontend
- Sends location coordinates and markers

## 🧪 Testing

### Run Rasa Tests

```bash
# Test NLU model
rasa test nlu

# Test Core model
rasa test core

# Test end-to-end conversations
rasa test
```

### Manual Testing

```bash
# Interactive shell testing
rasa shell

# Test with custom actions
rasa shell --debug
```




## 📸 Screenshots

### Main Chat Interface
![Chat Interface](docs/images/chat-interface.png)

### Interactive Flight Map
![Flight Map](docs/images/flight-map.png)

### Hotel Locations
![Hotel Map](docs/images/hotel-map.png)

### Mobile Responsive Design
![Mobile Design](docs/images/mobile-interface.png)

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 for Python code
- Add tests for new features
- Update documentation
- Use meaningful commit messages

### Adding New Languages

To add support for additional languages:

1. Create new NLU data files in `data/nlu_{language}.yml`
2. Add language-specific responses in `domain.yml`
3. Update pipeline configuration for language support
4. Test thoroughly with native speakers

## 🐛 Troubleshooting

### Common Issues

1. **Rasa Server Not Starting**
   ```bash
   # Check if port 5005 is already in use
   lsof -i :5005
   
   # Kill existing process
   kill -9 <PID>
   ```

2. **CORS Errors**
   ```bash
   # Start Rasa with CORS enabled
   rasa run --enable-api --cors "*"
   ```

3. **Model Training Fails**
   ```bash
   # Check data format
   rasa data validate
   
   # Validate stories
   rasa data validate stories
   ```

4. **Map Not Loading**
   - Check internet connection for map tiles
   - Verify Leaflet.js CDN is accessible
   - Check browser console for JavaScript errors

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Rasa Open Source** for the conversational AI framework
- **Leaflet.js** for interactive mapping capabilities
- **OpenStreetMap** for map tile data
