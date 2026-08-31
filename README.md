[app.py.txt](https://github.com/user-attachments/files/31667331/app.py.txt)
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import traceback

from google import genai


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)
CORS(app)


# =========================================================
# GEMINI API CONFIGURATION
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = None

if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        print("Gemini API client initialized successfully.")
    except Exception as e:
        print("Failed to initialize Gemini client:")
        print(str(e))
else:
    print("WARNING: GEMINI_API_KEY is not configured.")


# =========================================================
# HOME ROUTE
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "status": "success",
        "message": "AquaSense AI API is running",
        "gemini": "enabled" if client else "disabled",
        "endpoints": {
            "home": "/",
            "ai_advice": "/ai-advice",
            "chat": "/chat"
        }
    })


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "healthy",
        "gemini": "enabled" if client else "disabled"
    })


# =========================================================
# AI WATER QUALITY ADVICE
# =========================================================

@app.route("/ai-advice", methods=["POST"])
def ai_advice():

    try:

        # -----------------------------------------------------
        # Check Gemini
        # -----------------------------------------------------

        if client is None:
            return jsonify({
                "status": "error",
                "error_type": "ConfigurationError",
                "error": "Gemini API key is not configured on the server."
            }), 500


        # -----------------------------------------------------
        # Get JSON
        # -----------------------------------------------------

        data = request.get_json(silent=True)

        if not data:

            return jsonify({
                "status": "error",
                "error_type": "InvalidJSON",
                "error": "JSON data is required."
            }), 400


        # -----------------------------------------------------
        # Get sensor values
        # -----------------------------------------------------

        required_fields = [
            "turbidity",
            "do",
            "ph",
            "temp",
            "bod"
        ]

        missing_fields = [
            field
            for field in required_fields
            if field not in data
        ]

        if missing_fields:

            return jsonify({
                "status": "error",
                "error_type": "MissingField",
                "missing_fields": missing_fields,
                "error": "Required sensor field(s) are missing."
            }), 400


        # -----------------------------------------------------
        # Convert values to float
        # -----------------------------------------------------

        turbidity = float(data["turbidity"])
        dissolved_oxygen = float(data["do"])
        ph = float(data["ph"])
        temperature = float(data["temp"])
        bod = float(data["bod"])


        # -----------------------------------------------------
        # Optional ML prediction
        # -----------------------------------------------------

        water_quality = data.get(
            "water_quality",
            "Unknown"
        )


        # -----------------------------------------------------
        # Gemini Prompt
        # -----------------------------------------------------

        prompt = f"""
You are AquaSense AI, an intelligent water-quality assistant
for aquaculture and fish farming.

Analyze the following REAL sensor measurements:

pH: {ph}
Dissolved Oxygen (DO): {dissolved_oxygen} mg/L
Turbidity: {turbidity} cm
Temperature: {temperature} °C
BOD: {bod} mg/L

Machine Learning Prediction:
{water_quality}

Provide a concise and practical analysis using exactly these sections:

1. Overall Condition
2. Main Reasons
3. Possible Risks
4. Recommended Actions
5. Parameters to Monitor

Use simple language suitable for a fish farmer.

Important rules:

- Use only the sensor values provided above.
- Do not invent sensor measurements.
- Do not claim measurements that were not provided.
- Do not provide dangerous chemical dosages.
- Give general and safe pond-management guidance.
- If a parameter appears abnormal, explain why it may be a concern.
- Keep the answer practical and easy to understand.
"""


        # -----------------------------------------------------
        # Gemini API Call
        # -----------------------------------------------------

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )


        # -----------------------------------------------------
        # Get response text
        # -----------------------------------------------------

        ai_text = getattr(response, "text", None)

        if not ai_text:

            return jsonify({
                "status": "error",
                "error_type": "GeminiResponseError",
                "error": "Gemini returned an empty response."
            }), 500


        # -----------------------------------------------------
        # Success
        # -----------------------------------------------------

        return jsonify({

            "status": "success",

            "sensor_data": {
                "turbidity": turbidity,
                "do": dissolved_oxygen,
                "ph": ph,
                "temp": temperature,
                "bod": bod
            },

            "water_quality": water_quality,

            "ai_advice": ai_text
        })


    # =========================================================
    # ERROR HANDLING
    # =========================================================

    except KeyError as e:

        return jsonify({
            "status": "error",
            "error_type": "MissingField",
            "error": f"Missing required field: {str(e)}"
        }), 400


    except (ValueError, TypeError) as e:

        return jsonify({
            "status": "error",
            "error_type": "InvalidValue",
            "error": f"Invalid sensor value: {str(e)}"
        }), 400


    except Exception as e:

        print("====================================")
        print("GEMINI AI ADVICE ERROR")
        print("====================================")
        traceback.print_exc()

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

        # -----------------------------------------------------
        # Check Gemini
        # -----------------------------------------------------

        if client is None:

            return jsonify({
                "status": "error",
                "error_type": "ConfigurationError",
                "error": "Gemini API key is not configured on the server."
            }), 500


        # -----------------------------------------------------
        # Get JSON
        # -----------------------------------------------------

        data = request.get_json(silent=True)

        if not data:

            return jsonify({
                "status": "error",
                "error_type": "InvalidJSON",
                "error": "JSON data is required."
            }), 400


        # -----------------------------------------------------
        # Get question
        # -----------------------------------------------------

        question = data.get(
            "question",
            ""
        )


        if not isinstance(question, str):

            return jsonify({
                "status": "error",
                "error_type": "InvalidQuestion",
                "error": "Question must be a text value."
            }), 400


        question = question.strip()


        if not question:

            return jsonify({
                "status": "error",
                "error_type": "MissingQuestion",
                "error": "Question is required."
            }), 400


        # -----------------------------------------------------
        # Gemini Chat Prompt
        # -----------------------------------------------------

        prompt = f"""
You are AquaSense AI, an AI assistant for aquaculture,
fish farming, and water-quality monitoring.

User question:

{question}

Answer in simple, clear, and understandable language.

Focus mainly on:

- Fish farming
- Pond management
- Water quality
- pH
- Dissolved oxygen
- Turbidity
- Temperature
- BOD
- Fish health related to water quality

Important rules:

- Do not invent sensor readings.
- Do not pretend to have access to sensor data unless it is provided.
- Do not provide unsafe chemical treatment instructions.
- Do not provide dangerous chemical dosages.
- Give practical and general guidance.
"""


        # -----------------------------------------------------
        # Gemini API Call
        # -----------------------------------------------------

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )


        # -----------------------------------------------------
        # Response text
        # -----------------------------------------------------

        answer = getattr(response, "text", None)

        if not answer:

            return jsonify({
                "status": "error",
                "error_type": "GeminiResponseError",
                "error": "Gemini returned an empty response."
            }), 500


        # -----------------------------------------------------
        # Success
        # -----------------------------------------------------

        return jsonify({
            "status": "success",
            "question": question,
            "answer": answer
        })


    # =========================================================
    # ERROR HANDLING
    # =========================================================

    except Exception as e:

        print("====================================")
        print("GEMINI CHAT ERROR")
        print("====================================")
        traceback.print_exc()

        return jsonify({
            "status": "error",
            "error_type": type(e).__name__,
            "error": str(e)
        }), 500


# =========================================================
# 404 HANDLER
# =========================================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({
        "status": "error",
        "error_type": "NotFound",
        "error": "The requested endpoint was not found."
    }), 404


# =========================================================
# GLOBAL ERROR HANDLER
# =========================================================

@app.errorhandler(500)
def internal_error(error):

    return jsonify({
        "status": "error",
        "error_type": "InternalServerError",
        "error": "An internal server error occurred."
    }), 500


# =========================================================
# LOCAL DEVELOPMENT SERVER
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
