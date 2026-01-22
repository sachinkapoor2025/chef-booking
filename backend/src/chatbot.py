import json
import boto3
import os
import uuid
import time
from datetime import datetime
from botocore.exceptions import ClientError

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')

# Get environment variables
CHAT_HISTORY_TABLE = os.environ.get('CHAT_HISTORY_TABLE', 'chat-history')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# Supported languages (top 20 US languages)
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'zh': 'Chinese',
    'tag': 'Tagalog',
    'vi': 'Vietnamese',
    'fr': 'French',
    'ar': 'Arabic',
    'ko': 'Korean',
    'ru': 'Russian',
    'de': 'German',
    'hi': 'Hindi',
    'pt': 'Portuguese',
    'it': 'Italian',
    'ja': 'Japanese',
    'pl': 'Polish',
    'uk': 'Ukrainian',
    'ht': 'Haitian Creole',
    'bn': 'Bengali',
    'pa': 'Punjabi',
    'tl': 'Filipino'
}

# Language to OpenAI model mapping
LANGUAGE_MODELS = {
    'en': 'gpt-3.5-turbo',
    'es': 'gpt-3.5-turbo',
    'zh': 'gpt-3.5-turbo',
    'tag': 'gpt-3.5-turbo',
    'vi': 'gpt-3.5-turbo',
    'fr': 'gpt-3.5-turbo',
    'ar': 'gpt-3.5-turbo',
    'ko': 'gpt-3.5-turbo',
    'ru': 'gpt-3.5-turbo',
    'de': 'gpt-3.5-turbo',
    'hi': 'gpt-3.5-turbo',
    'pt': 'gpt-3.5-turbo',
    'it': 'gpt-3.5-turbo',
    'ja': 'gpt-3.5-turbo',
    'pl': 'gpt-3.5-turbo',
    'uk': 'gpt-3.5-turbo',
    'ht': 'gpt-3.5-turbo',
    'bn': 'gpt-3.5-turbo',
    'pa': 'gpt-3.5-turbo',
    'tl': 'gpt-3.5-turbo'
}

def handler(event, context):
    try:
        http_method = event['httpMethod']
        path = event['resource']

        if http_method == 'POST' and path == '/chat':
            return handle_chat_request(event)
        elif http_method == 'GET' and path == '/chat/history':
            return get_chat_history(event)
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS'
                },
                'body': json.dumps({'error': 'Not found'})
            }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }

def handle_chat_request(event):
    """Handle chat requests with language support"""
    try:
        # Parse request body
        body = json.loads(event['body'])
        message = body.get('message', '').strip()
        language = body.get('language', 'en')
        session_id = body.get('sessionId') or str(uuid.uuid4())

        if not message:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'error': 'Message is required'})
            }

        if language not in SUPPORTED_LANGUAGES:
            language = 'en'

        # Save user message to history
        save_chat_message(session_id, 'user', message, language)

        # Generate AI response
        if OPENAI_API_KEY:
            try:
                import openai
                openai.api_key = OPENAI_API_KEY

                # Get response from OpenAI
                response = openai.ChatCompletion.create(
                    model=LANGUAGE_MODELS[language],
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are a helpful assistant for Maharaja Chef Services. Respond in {SUPPORTED_LANGUAGES[language]} language. Keep responses concise and helpful."
                        },
                        {
                            "role": "user",
                            "content": message
                        }
                    ],
                    temperature=0.7,
                    max_tokens=500,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.0
                )

                ai_response = response.choices[0].message['content'].strip()

            except Exception as e:
                print(f"OpenAI API error: {str(e)}")
                ai_response = f"Sorry, I encountered an error processing your request. Please try again. (Error: {str(e)})"
        else:
            ai_response = "AI service is not configured. Here's a helpful response: Thank you for your message! Our team will get back to you soon."

        # Save AI response to history
        save_chat_message(session_id, 'assistant', ai_response, language)

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'message': ai_response,
                'sessionId': session_id,
                'language': language,
                'timestamp': datetime.utcnow().isoformat()
            })
        }

    except Exception as e:
        print(f"Error handling chat request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'error': 'Failed to process chat request'})
        }

def get_chat_history(event):
    """Get chat history for a session"""
    try:
        session_id = event['queryStringParameters'].get('sessionId')
        if not session_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS'
                },
                'body': json.dumps({'error': 'Session ID is required'})
            }

        # Get chat history from DynamoDB
        table = dynamodb.Table(CHAT_HISTORY_TABLE)
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('sessionId').eq(session_id)
        )

        # Sort by timestamp
        items = sorted(response['Items'], key=lambda x: x['timestamp'])

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps({
                'history': items,
                'sessionId': session_id
            })
        }

    except Exception as e:
        print(f"Error getting chat history: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps({'error': 'Failed to get chat history'})
        }

def save_chat_message(session_id, role, content, language):
    """Save a chat message to DynamoDB"""
    try:
        table = dynamodb.Table(CHAT_HISTORY_TABLE)
        table.put_item(
            Item={
                'sessionId': session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'role': role,
                'content': content,
                'language': language
            }
        )
    except Exception as e:
        print(f"Error saving chat message: {str(e)}")

# Export for testing
if __name__ == "__main__":
    # Test data
    test_event = {
        'httpMethod': 'POST',
        'resource': '/chat',
        'body': json.dumps({
            'message': 'Hello, what services do you offer?',
            'language': 'en'
        })
    }

    result = handler(test_event, {})
    print("Test result:", result)
