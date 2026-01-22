import json
import boto3
import os
import uuid
import time
from datetime import datetime
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from openai import OpenAI

# =========================================================
# CONFIG
# =========================================================

CHAT_HISTORY_TABLE = os.environ.get("CHAT_HISTORY_TABLE", "chat-history")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
SERVICE_NAME = "chat-lambda"

dynamodb = boto3.resource("dynamodb")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# =========================================================
# LANGUAGE CONFIG
# =========================================================

SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "zh": "Chinese",
    "tag": "Tagalog",
    "vi": "Vietnamese",
    "fr": "French",
    "ar": "Arabic",
    "ko": "Korean",
    "ru": "Russian",
    "de": "German",
    "hi": "Hindi",
    "pt": "Portuguese",
    "it": "Italian",
    "ja": "Japanese",
    "pl": "Polish",
    "uk": "Ukrainian",
    "ht": "Haitian Creole",
    "bn": "Bengali",
    "pa": "Punjabi",
    "tl": "Filipino",
}

LANGUAGE_MODELS = {lang: "gpt-4o-mini" for lang in SUPPORTED_LANGUAGES}

# =========================================================
# LOGGING HELPERS
# =========================================================

def log(level, message, **data):
    """Structured JSON logging for CloudWatch"""
    print(json.dumps({
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "service": SERVICE_NAME,
        "message": message,
        **data
    }))


# =========================================================
# LAMBDA HANDLER
# =========================================================

def handler(event, context):
    start_time = time.time()
    request_id = context.aws_request_id

    log(
        "INFO",
        "Lambda invocation started",
        requestId=request_id,
        httpMethod=event.get("httpMethod"),
        resource=event.get("resource"),
        sourceIp=event.get("requestContext", {}).get("identity", {}).get("sourceIp"),
        userAgent=event.get("requestContext", {}).get("identity", {}).get("userAgent"),
        rawEvent=event,
    )

    try:
        method = event.get("httpMethod")
        path = event.get("resource")

        if method == "POST" and path == "/chat":
            response = handle_chat_request(event, request_id)

        elif method == "GET" and path == "/chat/history":
            response = get_chat_history(event, request_id)

        else:
            response = api_response(404, {"error": "Not found"})

        log(
            "INFO",
            "Lambda invocation completed",
            requestId=request_id,
            durationMs=int((time.time() - start_time) * 1000),
            responseStatus=response["statusCode"],
        )

        return response

    except Exception as e:
        log(
            "ERROR",
            "Unhandled lambda exception",
            requestId=request_id,
            error=str(e),
        )
        return api_response(500, {"error": "Internal server error"})


# =========================================================
# CHAT HANDLER
# =========================================================

def handle_chat_request(event, request_id):
    body = json.loads(event.get("body", "{}"))

    message = body.get("message", "").strip()
    language = body.get("language", "en")
    session_id = body.get("sessionId") or str(uuid.uuid4())

    log(
        "INFO",
        "Incoming chat request",
        requestId=request_id,
        sessionId=session_id,
        language=language,
        userMessage=message,
    )

    if not message:
        return api_response(400, {"error": "Message is required"})

    if language not in SUPPORTED_LANGUAGES:
        language = "en"

    save_chat_message(session_id, "user", message, language)

    ai_response = generate_ai_response(message, language, request_id, session_id)

    save_chat_message(session_id, "assistant", ai_response, language)

    log(
        "INFO",
        "Chat response sent",
        requestId=request_id,
        sessionId=session_id,
        aiResponse=ai_response,
    )

    return api_response(
        200,
        {
            "message": ai_response,
            "sessionId": session_id,
            "language": language,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# =========================================================
# OPENAI
# =========================================================

def generate_ai_response(message, language, request_id, session_id):
    if not OPENAI_API_KEY:
        log("WARN", "OpenAI API key missing", requestId=request_id)
        return "AI service is not configured."

    try:
        log(
            "INFO",
            "Calling OpenAI",
            requestId=request_id,
            sessionId=session_id,
            model=LANGUAGE_MODELS[language],
            promptPreview=message[:200],
        )

        completion = openai_client.chat.completions.create(
            model=LANGUAGE_MODELS[language],
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant for Maharaja Chef Services. "
                        f"Respond in {SUPPORTED_LANGUAGES[language]}. "
                        "Keep responses concise and professional."
                    ),
                },
                {"role": "user", "content": message},
            ],
            temperature=0.7,
            max_tokens=500,
        )

        response_text = completion.choices[0].message.content.strip()

        log(
            "INFO",
            "OpenAI response received",
            requestId=request_id,
            sessionId=session_id,
            tokensUsed=completion.usage.total_tokens if completion.usage else None,
        )

        return response_text

    except Exception as e:
        log(
            "ERROR",
            "OpenAI call failed",
            requestId=request_id,
            sessionId=session_id,
            error=str(e),
        )
        return "Sorry, I encountered an error. Please try again."


# =========================================================
# CHAT HISTORY
# =========================================================

def get_chat_history(event, request_id):
    params = event.get("queryStringParameters") or {}
    session_id = params.get("sessionId")

    log(
        "INFO",
        "Fetching chat history",
        requestId=request_id,
        sessionId=session_id,
    )

    if not session_id:
        return api_response(400, {"error": "Session ID is required"})

    try:
        table = dynamodb.Table(CHAT_HISTORY_TABLE)
        result = table.query(KeyConditionExpression=Key("sessionId").eq(session_id))
        items = sorted(result.get("Items", []), key=lambda x: x["timestamp"])

        return api_response(200, {"sessionId": session_id, "history": items})

    except Exception as e:
        log(
            "ERROR",
            "Failed to fetch chat history",
            requestId=request_id,
            error=str(e),
        )
        return api_response(500, {"error": "Failed to get chat history"})


# =========================================================
# DYNAMODB
# =========================================================

def save_chat_message(session_id, role, content, language):
    try:
        table = dynamodb.Table(CHAT_HISTORY_TABLE)
        table.put_item(
            Item={
                "sessionId": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "role": role,
                "content": content,
                "language": language,
            }
        )
    except ClientError as e:
        log("ERROR", "DynamoDB write failed", error=e.response["Error"]["Message"])


# =========================================================
# RESPONSE
# =========================================================

def api_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        },
        "body": json.dumps(body),
    }
