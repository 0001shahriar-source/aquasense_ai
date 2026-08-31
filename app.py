from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import traceback

from google import genai

app = Flask(**name**)
CORS(app)

# =========================================================

# GEMINI API CONFIGURATION

# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
client = genai.Client(api_key=GEMINI_API_KEY)
else:
client = None

# Current Gemini model

GEMINI_MODEL = "gemini-3.7-flash"

# =========================================================

# HOME ROUTE

# =========================================================

@app.route("/", methods=["GET"])
def home():
return jsonify({
"message": "AquaSense AI Gemini API is running",
"gemini": "enabled" if client else "disabled",
"model": GEMINI_MODEL
})

# =========================================================

# HEALTH CHECK

# =========================================================

@app.route("/health", methods=["GET"])
def health():
return jsonify({
"status": "healthy",
"gemini": "enabled" if client else "disabled",
"model": GEMINI_MODEL
})

# =========================================================

# AI WATER QUALITY ADVICE

# =========================================================

@app.route("/ai-advice", methods=["POST"])
def ai_advice():

```
try:

    # Check API key
    if client is None:
        return jsonify({
            "status": "error",
            "error_type": "ConfigurationError",
            "error": "GEMINI_API_KEY is not configured in Render."
        }), 500

    # Get JSON
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "error_type": "InvalidJSON",
            "error": "JSON data is required."
        }), 400

    # Required sensor values
    required_fields = [
        "turbidity",
        "do",
        "ph",
        "temp",
        "bod"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "status": "error",
                "error_type": "MissingField",
                "error": f"Missing required field: {field}"
            }), 400

    # Convert sensor values
    turbidity = float(data["turbidity"])
    do = float(data["do"])
    ph = float(data["ph"])
    temp = float(data["temp"])
    bod = float(data["bod"])

    # ML prediction
    water_quality = str(
        data.get("water_quality", "Unknown")
    )

    # =====================================================
    # PROMPT
    # =====================================================

    prompt = f"""
```

You are AquaSense AI, an intelligent water-quality
assistant for aquaculture and fish farming.

Analyze the following REAL sensor measurements:

pH: {ph}
Dissolved Oxygen (DO): {do} mg/L
Turbidity: {turbidity} cm
Temperature: {temp} °C
BOD: {bod} mg/L

Machine Learning Prediction:
{water_quality}

Give a concise and useful analysis for a fish farmer.

Use exactly these sections:

1. Overall Condition
2. Main Reasons
3. Possible Risks
4. Recommended Actions
5. Parameters to Monitor

Rules:

* Use only the sensor values provided above.
* Do not invent any measurements.
* Explain problems in simple language.
* Give general pond-management recommendations.
* Do not provide dangerous chemical dosages.
* Do not recommend unsafe chemical treatments.
* Keep the response practical and concise.
  """

  ```
    # =====================================================
    # GEMINI REQUEST
    # =====================================================

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    ai_advice = response.text

    if not ai_advice:
        ai_advice = "Gemini returned an empty response."

    # =====================================================
    # SUCCESS
    # =====================================================

    return jsonify({
        "status": "success",
        "water_quality": water_quality,
        "ai_advice": ai_advice
    }), 200
  ```

  except ValueError as e:

  ```
    return jsonify({
        "status": "error",
        "error_type": "InvalidValue",
        "error": f"Invalid sensor value: {str(e)}"
    }), 400
  ```

  except Exception as e:

  ```
    print("==========================================")
    print("AquaSense AI - WATER ADVICE ERROR")
    print("==========================================")
    print(traceback.format_exc())

    return jsonify({
        "status": "error",
        "error_type": type(e).__name__,
        "error": str(e)
    }), 500
  ```

# =========================================================

# AI CHATBOT

# =========================================================

@app.route("/chat", methods=["POST"])
def chat():

```
try:

    # Check API key
    if client is None:
        return jsonify({
            "status": "error",
            "error_type": "ConfigurationError",
            "error": "GEMINI_API_KEY is not configured in Render."
        }), 500

    # Get JSON
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "error_type": "InvalidJSON",
            "error": "JSON data is required."
        }), 400

    # Get question
    question = data.get("question", "")

    if not isinstance(question, str) or not question.strip():
        return jsonify({
            "status": "error",
            "error_type": "MissingQuestion",
            "error": "Question is required."
        }), 400

    # =====================================================
    # CHAT PROMPT
    # =====================================================

    prompt = f"""
```

You are AquaSense AI, an intelligent assistant
for aquaculture and water quality monitoring.

User question:

{question}

Answer in simple and understandable language.

Focus on:

* Fish farming
* Water quality
* pH
* Dissolved oxygen
* Turbidity
* Temperature
* BOD
* Pond management

Rules:

* Do not invent sensor readings.
* Do not claim to have sensor data unless the user provides it.
* Do not provide dangerous chemical dosages.
* Do not recommend unsafe chemical treatments.
* Give practical general guidance.
  """

  ```
    # =====================================================
    # GEMINI REQUEST
    # =====================================================

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    answer = response.text

    if not answer:
        answer = "Gemini returned an empty response."

    # =====================================================
    # SUCCESS
    # =====================================================

    return jsonify({
        "status": "success",
        "answer": answer
    }), 200
  ```

  except Exception as e:

  ```
    print("==========================================")
    print("AquaSense AI - CHAT ERROR")
    print("==========================================")
    print(traceback.format_exc())

    return jsonify({
        "status": "error",
        "error_type": type(e).__name__,
        "error": str(e)
    }), 500
  ```

# =========================================================

# RUN SERVER

# =========================================================

if **name** == "**main**":

```
port = int(
    os.environ.get(
        "PORT",
        5000
    )
)

app.run(
    host="0.0.0.0",
    port=port
)
```
