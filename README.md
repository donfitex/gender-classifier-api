# Gender Classification API

A Django REST API that classifies names by gender using the Genderize API, with additional processing and validation.

---

## 🌐 Live API

Base URL:

<https://gender-classifier-api-production.up.railway.app/>

Endpoint:

GET /api/classify/?name={name}

Example:

<https://gender-classifier-api-production.up.railway.app/api/classify/?name=Raphael>

---

## 📌 Features

- External API integration (Genderize)
- Clean data processing
- Confidence scoring logic
- Input validation
- Structured error handling
- Logging for monitoring
- Timeout handling for reliability
- CORS enabled for public access

---

## 🧠 Processing Logic

- Extract:
  - gender
  - probability
  - count → renamed to "sample_size"

- Compute:

is_confident = probability >= 0.7 AND sample_size >= 100

- Generate:
  - "processed_at" (UTC, ISO 8601)

---

## ✅ Success Response

<```json>
{
 "status": "success",
    "data": {
        "name": "raphael",
        "gender": "male",
        "probability": 0.99,
        "sample_size": 124068,
        "is_confident": true,
        "processed_at": "2026-04-11T18:06:25.541357Z"
  }
}

---

## ❌ Error Responses

Missing name (400)
{
  "status": "error",
  "message": "Name is required"
}

Invalid name (422)
{
  "status": "error",
  "message": "Name must be a string"
}

No prediction
{
  "status": "error",
  "message": "No prediction available for the provided name"
}

External API error (502)
{
  "status": "error",
  "message": "External API error"
}

---

## 🛠 Tech Stack

Python
Django
Django REST Framework
Requests

## ⚙️ Setup Instructions

git clone <https://github.com/yourusername/gender-classifier-api.git>
cd gender-classifier-api

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python manage.py runserver

---

## 🌍 Deployment

Deployed on Railway.

📊 Performance Notes
API response time under 500ms (excluding external API latency)
External API calls use timeout to prevent hanging
Logging enabled for monitoring and debugging

---

## 🔗 Author

Raphael Eze.
