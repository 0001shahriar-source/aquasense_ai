from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from google import genai

app = Flask(__name__)
CORS(app)

# =========================
# GEMINI API CONFIGURATION
# =========================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    client = None


# =========================
# HOME ROUTE
# =========================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "AquaSense AI Gemini API is running",
        "gemini": "enabled" if client else "disabled"
    })


# =========================
# AI WATER QUALITY ADVICE
# =========================

@app.route("/ai-advice", methods=["POST"])
def ai_advice():

    try:

        if client is None:
            return jsonify({
                "error": "Gemini API key is not configured"
            }), 500

        data = request.get_json()

        turbidity = float(data["turbidity"])
        do = float(data["do"])
        ph = float(data["ph"])
        temp = float(data["temp"])
        bod = float(data["bod"])

        water_quality = data.get(
            "water_quality",
            "Unknown"
        )

        prompt = f"""
You are AquaSense AI, an intelligent
water-quality assistant for aquaculture.

Analyze the following water quality data:

pH: {ph}
Dissolved Oxygen (DO): {do} mg/L
Turbidity: {turbidity} cm
Temperature: {temp} °C
BOD: {bod} mg/L

Machine Learning Prediction:
{water_quality}

Provide a concise analysis using these sections:

1. Overall Condition
2. Main Reasons
3. Possible Risks
4. Recommended Actions
5. Parameters to Monitor

Use simple language suitable for a fish farmer.

Do not invent sensor measurements.
Do not provide dangerous chemical dosages.
Recommendations should be general monitoring guidance.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return jsonify({
            "status": "success",
            "water_quality": water_quality,
            "ai_advice": response.text
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


# =========================
# AI CHATBOT
# =========================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        if client is None:
            return jsonify({
                "error": "Gemini API key is not configured"
            }), 500

        data = request.get_json()

        question = data.get("question", "")

        if not question:
            return jsonify({
                "error": "Question is required"
            }), 400

        prompt = f"""
You are AquaSense AI, an AI assistant
for aquaculture and water quality monitoring.

User question:
{question}

Answer in simple and understandable language.

Focus on:
- Fish farming
- Water quality
- pH
- Dissolved oxygen
- Turbidity
- Temperature
- BOD
- Pond management

Do not invent sensor readings.
Do not provide unsafe chemical treatment instructions.
"""

        response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

        return jsonify({
            "status": "success",
            "answer": response.text
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
