```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from google import genai

app = Flask(__name__)
CORS(app)


# =========================================================
# GEMINI API CONFIGURATION
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    client = None


# =========================================================
# HOME ROUTE
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "message": "AquaSense AI Gemini API is running",
        "gemini": "enabled" if client else "disabled"
    })


# =========================================================
# AI WATER QUALITY ADVICE
# =========================================================

@app.route("/ai-advice", methods=["POST"])
def ai_advice():

    try:

        # Check Gemini API
        if client is None:
            return jsonify({
                "status": "error",
                "error": "Gemini API key is not configured"
            }), 500

        # Get JSON data
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "error": "JSON data is required"
            }), 400

        # Get sensor values
        turbidity = float(data["turbidity"])
        do = float(data["do"])
        ph = float(data["ph"])
        temp = float(data["temp"])
        bod = float(data["bod"])

        # ML prediction
        water_quality = data.get(
            "water_quality",
            "Unknown"
        )

        # =====================================================
        # GEMINI PROMPT
        # =====================================================

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

        # =====================================================
        # GEMINI GENERATION
        # =====================================================

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        # =====================================================
        # SUCCESS RESPONSE
        # =====================================================

        return jsonify({
            "status": "success",
            "water_quality": water_quality,
            "ai_advice": response.text
        })

    except KeyError as e:

        return jsonify({
            "status": "error",
            "error_type": "MissingField",
            "error": f"Missing required field: {str(e)}"
        }), 400

    except ValueError as e:

        return jsonify({
            "status": "error",
            "error_type": "InvalidValue",
            "error": f"Invalid sensor value: {str(e)}"
        }), 400

    except Exception as e:

        import traceback

        print("====================================")
        print("GEMINI ERROR")
        print("====================================")
        print(traceback.format_exc())

        return jsonify({
            "status": "error",
            "error_type": type(e).__name__,
            "error": str(e)
        }), 500


# =========================================================
# AI CHATBOT
# =========================================================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        # Check Gemini API
        if client is None:
            return jsonify({
                "status": "error",
                "error": "Gemini API key is not configured"
            }), 500

        # Get JSON data
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "error": "JSON data is required"
            }), 400

        question = data.get(
            "question",
            ""
        )

        # Check question
        if not question.strip():
            return jsonify({
                "status": "error",
                "error": "Question is required"
            }), 400

        # =====================================================
        # CHATBOT PROMPT
        # =====================================================

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

        # =====================================================
        # GEMINI GENERATION
        # =====================================================

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        # =====================================================
        # SUCCESS RESPONSE
        # =====================================================

        return jsonify({
            "status": "success",
            "answer": response.text
        })

    except Exception as e:

        import traceback

        print("====================================")
        print("CHAT GEMINI ERROR")
        print("====================================")
        print(traceback.format_exc())

        return jsonify({
            "status": "error",
            "error_type": type(e).__name__,
            "error": str(e)
        }), 500


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        )
    )
```
