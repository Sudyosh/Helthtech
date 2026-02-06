# 🌿 MindfulMe - AI Mental Health Companion Platform

A supportive AI companion platform designed for teenagers to discuss mental health, with risk detection and a psychiatrist dashboard for monitoring.

![Platform Overview](https://img.shields.io/badge/Status-Development-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🎯 Overview

MindfulMe provides a safe, private space for teenagers to talk about their mental health. The platform features:

- **AI Chat Companion** - Empathetic conversations using natural language processing
- **Mood Tracking** - Daily mood and stress logging with trend visualization
- **Risk Detection** - Automatic detection of concerning language patterns
- **Psychiatrist Dashboard** - Analytics and alerts for mental health professionals

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React App     │────▶│   FastAPI       │────▶│   MongoDB       │
│   (Frontend)    │     │   (Backend)     │     │   (Database)    │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                        ┌────────▼────────┐
                        │   AI Service    │
                        │ ┌─────────────┐ │
                        │ │ Emotion     │ │
                        │ │ Classifier  │ │
                        │ ├─────────────┤ │
                        │ │ Sentiment   │ │
                        │ │ Analyzer    │ │
                        │ ├─────────────┤ │
                        │ │ Risk        │ │
                        │ │ Detector    │ │
                        │ ├─────────────┤ │
                        │ │ LLM         │ │
                        │ │ Companion   │ │
                        │ └─────────────┘ │
                        └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- MongoDB (local or Docker)
- OpenAI API key (optional, has fallback)

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/Helthtech.git
cd Helthtech

# Start all services
docker-compose up -d

# Access the app
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

#### 1. Start MongoDB

```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:7.0

# Or install locally
# See: https://docs.mongodb.com/manual/installation/
```

#### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run the server
uvicorn main:app --reload --port 8000
```

#### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

#### 4. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
Helthtech/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic
│   │   └── database/       # MongoDB connection
│   ├── main.py             # FastAPI app
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── styles/         # CSS styles
│   └── package.json
├── ai_service/             # AI/ML modules
│   ├── emotion_classifier.py
│   ├── sentiment_analyzer.py
│   ├── risk_detector.py
│   └── llm_companion.py
├── database/               # Database schemas
├── docker-compose.yml
└── README.md
```

## 🔌 API Endpoints

### User Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users` | Create anonymous user |
| GET | `/api/users/{id}` | Get user details |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send message, get AI response |
| GET | `/api/chat/history/{user_id}` | Get conversation history |

### Mood Tracking
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/mood` | Log mood entry |
| GET | `/api/mood/history/{user_id}` | Get mood history |
| GET | `/api/mood/trends/{user_id}` | Get mood trends |

### Dashboard (Psychiatrist)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard` | Get dashboard analytics |
| GET | `/api/dashboard/users` | List all users |
| GET | `/api/dashboard/user/{id}` | Get user details |

### Alerts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/alerts` | Get all alerts |
| PUT | `/api/alerts/{id}/resolve` | Resolve an alert |

## 📊 Example API Calls

### Create User
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"anonymous_mode": true, "consent": true}'
```

### Send Chat Message
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "your-user-id",
    "message": "I have been feeling stressed about school"
  }'
```

### Log Mood
```bash
curl -X POST http://localhost:8000/api/mood \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "your-user-id",
    "mood_score": 6,
    "stress_score": 7,
    "notes": "Exam week"
  }'
```

### Get Dashboard
```bash
curl http://localhost:8000/api/dashboard
```

## 🔒 Security & Privacy

- **Anonymized IDs**: Users are identified by UUID, no personal information required
- **Consent**: Users must consent before data logging
- **No PII**: No names, emails, or identifying information stored
- **Secure Logging**: All data is encrypted in transit and at rest
- **Crisis Resources**: Help button with crisis hotline information

## 🧠 AI Pipeline

```
User Message
    ↓
┌─────────────────┐
│ Emotion Classifier │  → joy, sadness, fear, anger, etc.
└─────────────────┘
    ↓
┌─────────────────┐
│ Sentiment Analyzer │ → positive/negative score
└─────────────────┘
    ↓
┌─────────────────┐
│ Risk Detector    │  → LOW / MEDIUM / HIGH
└─────────────────┘
    ↓
┌─────────────────┐
│ LLM Companion   │  → Empathetic response
└─────────────────┘
    ↓
Response + Logging
```

## ⚠️ Risk Detection

The system monitors for concerning patterns:

| Risk Level | Triggers | Actions |
|------------|----------|---------|
| LOW | Normal stress | Continue conversation |
| MEDIUM | Hopelessness, persistent sadness | Flag for review |
| HIGH | Self-harm language | Create alert, supportive response |

**High-risk keywords monitored:**
- "kill myself", "want to die", "hurt myself"
- "end my life", "suicide", "self harm"

## 🆘 Crisis Resources

Built-in crisis resources for users:
- **988 Suicide & Crisis Lifeline**: Call or text 988
- **Crisis Text Line**: Text HOME to 741741
- **Emergency**: Call 911

## 🛠️ Development

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# AI service tests
cd ai_service
python -m pytest tests/ -v
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_URL` | `mongodb://localhost:27017` | MongoDB connection URL |
| `DATABASE_NAME` | `mental_health_companion` | Database name |
| `OPENAI_API_KEY` | - | OpenAI API key (optional) |
| `DEBUG` | `true` | Enable debug mode |

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Disclaimer

**This is not a replacement for professional mental health care.** MindfulMe is a supportive tool designed to complement, not replace, professional therapy and counseling. If you or someone you know is in crisis, please contact emergency services or a crisis hotline immediately.

---

Built with ❤️ for mental health awareness