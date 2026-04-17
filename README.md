# Gender Classification API

A Django REST API that classifies names by gender using the Genderize API, with additional processing and validation.

---

## 🌐 Live API

Base URL:

<https://gender-classifier-api-production.up.railway.app/>

## 📌 Endpoints

### 1. GET /api/classify

Classifies gender using external API.

GET /api/classify/?name={name}

#### Example

<https://gender-classifier-api-production.up.railway.app/api/classify/?name=Raphael>

### Response

<```json>
{
  "status": "success",
  "data": {
    "name": "raphael",
    "gender": "male",
    "probability": 0.99,
    "sample_size": 1234,
    "is_confident": true,
    "processed_at": "2026-04-01T12:00:00Z"
  }
}

## 2. POST /api/profiles

Create Profile Using External API

Request:
{
  "name": "ella"
}

### Response (201):

{
  "status": "success",
  "data": {
    "id": "...",
    "name": "ella",
    "gender": "female",
    "gender_probability": 0.99,
    "sample_size": 1234,
    "age": 46,
    "age_group": "adult",
    "country_id": "DRC",
    "country_probability": 0.85,
    "created_at": "2026-04-01T12:00:00Z"
  }
}

### Idempotency

If profile exists:

### Response Example

<```json>
{
    "status": "success",
    "message": "Profile already exists",
    "data": {
        "id": "019d9087-2ce0-7102-a2aa-5241ce898b88",
        "name": "ella",
        "gender": "female",
        "gender_probability": 0.99,
        "sample_size": 97517,
        "age": 53,
        "age_group": "adult",
        "country_id": "CM",
        "country_probability": 0.09677289106552395,
        "created_at": "2026-04-15T09:44:31.201006Z"
    }
}

---

## 3. Get All Profiles

GET /profiles/

- Optional filters:

    gender

    country_id

    age_group

Example:

/profiles/?gender=male&country_id=NG

---

## 4. Get Single Profile

GET /profiles/{id}

---

## 5. Delete Profile

DELETE /profiles/{id}

- Returns:

   204 No Content

---

## Classification Rules

- Age Groups:

    0–12 → child

    13–19 → teenager

    20–59 → adult

    60+ → senior

- Country:

    Highest probability from Nationalize API

---

## 📌 Features

Multi-API integration:
Gender prediction
Age estimation
Nationality prediction
Data processing & transformation
Idempotent profile creation
Input validation (400 / 422)
Error handling (404 / 500 / 502)
UTC timestamps (ISO 8601)
CORS enabled (Access-Control-Allow-Origin: *)
Logging for debugging and monitoring

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
SQLite (default)

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

📌 Notes
• External APIs are used for data enrichment
• User-provided fields (like age) are ignored
• Duplicate names return existing records

---

## 🔗 Author

Raphael Eze.
