import json
import os
import time
from datetime import datetime
from openai import OpenAI

# ==============================
# CONFIG
# ==============================

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
MODEL = "gpt-4o-mini"
LOG_TRUNCATE_LIMIT = 2000  # prevent CloudWatch log explosion

client = OpenAI(api_key=OPENAI_API_KEY)


# ==============================
# LOGGING UTIL
# ==============================

def log(title, data=None):
    print(f"\n===== {title} =====")
    if data is not None:
        try:
            text = json.dumps(data, indent=2)
        except Exception:
            text = str(data)

        if len(text) > LOG_TRUNCATE_LIMIT:
            text = text[:LOG_TRUNCATE_LIMIT] + "... (truncated)"
        print(text)
    print("===== END =====\n")


# ==============================
# HANDLER
# ==============================

def handler(event, context):
    start_time = time.time()
    request_id = context.aws_request_id

    log("REQUEST METADATA", {
        "requestId": request_id,
        "timestamp": datetime.utcnow().isoformat()
    })

    # 1️⃣ RAW API GATEWAY EVENT
    log("RAW API GATEWAY EVENT", event)

    try:
        body = json.loads(event.get("body", "{}"))
        log("PARSED REQUEST BODY", body)

        # 🔧 FIX #1 — READ NESTED chefData
        chef = body.get("chefData", {})

        # Normalize input EXACTLY as frontend sends
        original_data = {
            "name": chef.get("name", ""),
            "description": chef.get("description", ""),
            "location": chef.get("location", ""),
            "cuisine": chef.get("cuisine", ""),
            "specialties": chef.get("specialties", []),
            "dietary_tags": chef.get("dietaryTags", []),
            "rating": chef.get("rating"),
            "reviewCount": chef.get("reviewCount"),
            "pricing": chef.get("pricing", []),
            "menu_options": chef.get("menuOptions", {}),
            "reviews": chef.get("reviews", [])
        }

        log("NORMALIZED INPUT DATA", original_data)

        # Skip OpenAI if key missing
        if not OPENAI_API_KEY:
            log("OPENAI SKIPPED", "OPENAI_API_KEY not configured")
            return success_response(original_data, start_time)

        # 2️⃣ SINGLE LLM CALL
        beautified_data, raw_llm_output, prompt_sent = beautify_all_fields(original_data)

        # 3️⃣ LOG LLM INTERACTION
        log("LLM PROMPT SENT", prompt_sent)
        log("RAW LLM RESPONSE", raw_llm_output)

        # 4️⃣ MERGE WITH FALLBACK
        final_data = merge_with_fallback(original_data, beautified_data)
        log("FINAL RESPONSE DATA", final_data)

        return success_response(final_data, start_time)

    except Exception as e:
        log("LAMBDA ERROR", str(e))
        return error_response("Failed to beautify content", start_time)


# ==============================
# OPENAI LOGIC
# ==============================

def beautify_all_fields(data):
    prompt_text = f"""
You are a professional content editor for a premium personal chef marketplace website.

RULES:
- Improve grammar, clarity, and tone
- Keep facts unchanged
- Do NOT add fake experience or pricing
- Return VALID JSON ONLY
- Keep EXACT SAME keys and structure

INPUT JSON:
{json.dumps(data, indent=2)}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You beautify structured website content without changing meaning."
            },
            {
                "role": "user",
                "content": prompt_text
            }
        ],
        temperature=0.4,
        max_tokens=900
    )

    raw_output = response.choices[0].message.content.strip()

    # 🔧 FIX #2 — STRIP ```json MARKDOWN SAFELY
    cleaned = raw_output
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        parsed = {}

    return parsed, raw_output, prompt_text


# ==============================
# HELPERS
# ==============================

def merge_with_fallback(original, beautified):
    """
    Never let OpenAI break the UI.
    If a field is missing or empty, keep original.
    """
    result = {}
    for key, value in original.items():
        new_value = beautified.get(key)
        if new_value is None or new_value == "":
            result[key] = value
        else:
            result[key] = new_value
    return result


# ==============================
# RESPONSES
# ==============================

def success_response(data, start_time):
    duration_ms = int((time.time() - start_time) * 1000)
    log("REQUEST COMPLETED", {
        "status": "success",
        "duration_ms": duration_ms
    })

    return {
        "statusCode": 200,
        "headers": cors_headers(),
        "body": json.dumps({
            "success": True,
            "data": data
        })
    }

def error_response(message, start_time):
    duration_ms = int((time.time() - start_time) * 1000)
    log("REQUEST FAILED", {
        "status": "error",
        "duration_ms": duration_ms,
        "message": message
    })

    return {
        "statusCode": 500,
        "headers": cors_headers(),
        "body": json.dumps({
            "success": False,
            "error": message
        })
    }

def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "POST, OPTIONS"
    }
