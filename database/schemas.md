# MongoDB Database Schema

## Collections

### users
Stores anonymized user information.

```json
{
  "_id": ObjectId,
  "user_id": "uuid-string",          // Anonymized unique identifier
  "created_at": ISODate,              // When user was created
  "anonymous_mode": true,             // Whether user opted for anonymous mode
  "consent": true,                    // User consent for data logging
  "last_active": ISODate              // Last activity timestamp
}
```

**Indexes:**
- `user_id` (unique)

---

### chat_logs
Stores all chat messages between users and AI.

```json
{
  "_id": ObjectId,
  "user_id": "uuid-string",           // Reference to user
  "message": "string",                // Message content
  "role": "user" | "ai",              // Who sent the message
  "timestamp": ISODate,               // When message was sent
  "emotion": "string",                // Detected emotion (sadness, joy, etc.)
  "emotion_confidence": 0.95,         // Confidence score 0-1
  "sentiment_score": -0.5,            // Sentiment score -1 to 1
  "sentiment_polarity": "negative"    // positive/negative/neutral
}
```

**Indexes:**
- `user_id` + `timestamp` (compound, descending)

---

### mood_logs
Stores user mood and stress entries.

```json
{
  "_id": ObjectId,
  "user_id": "uuid-string",
  "mood_score": 6,                    // 1-10 scale
  "stress_score": 4,                  // 1-10 scale
  "notes": "string",                  // Optional user notes
  "date": ISODate,                    // Date of entry
  "created_at": ISODate               // When entry was created
}
```

**Indexes:**
- `user_id` + `date` (compound, descending)

---

### risk_scores
Stores calculated risk scores from chat analysis.

```json
{
  "_id": ObjectId,
  "user_id": "uuid-string",
  "level": "LOW" | "MEDIUM" | "HIGH", // Risk level
  "score": 45.5,                      // Numeric score 0-100
  "timestamp": ISODate,               // When calculated
  "factors": ["array", "of", "factors"], // What contributed to risk
  "trigger_message": "string"         // Message that triggered (if applicable)
}
```

**Indexes:**
- `user_id` + `timestamp` (compound, descending)

---

### alerts
Stores alerts for psychiatrist review.

```json
{
  "_id": ObjectId,
  "user_id": "uuid-string",
  "risk_level": "HIGH" | "MEDIUM",    // Alert severity
  "trigger_message": "string",        // Message that triggered alert
  "created_at": ISODate,              // When alert was created
  "resolved": false,                  // Whether reviewed/resolved
  "resolved_at": ISODate,             // When resolved (if applicable)
  "notes": "string"                   // Psychiatrist notes
}
```

**Indexes:**
- `created_at` (descending)
- `resolved`

---

## Risk Level Definitions

| Level  | Score Range | Description |
|--------|-------------|-------------|
| LOW    | 0-34        | Normal stress, general conversation |
| MEDIUM | 35-69       | Concerning patterns, distress indicators |
| HIGH   | 70-100      | Self-harm language, crisis indicators |

## Emotion Labels

From HuggingFace emotion classifier:
- `joy` - Happiness, excitement
- `sadness` - Grief, depression, melancholy
- `anger` - Frustration, rage
- `fear` - Anxiety, worry, panic
- `disgust` - Revulsion
- `surprise` - Shock, amazement
- `neutral` - No strong emotion

## Data Retention

- Chat logs: Retained for therapeutic continuity
- Mood logs: Retained for trend analysis
- Alerts: Retained until resolved + 30 days
- All data is anonymized (no PII stored)
