import json
import boto3
import os
import hashlib
from botocore.exceptions import ClientError
import openai
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')

# Get environment variables
CHEF_TABLE = os.environ['CHEF_TABLE']
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# Configure OpenAI only if API key is provided
if OPENAI_API_KEY and OPENAI_API_KEY.strip():
    openai.api_key = OPENAI_API_KEY
else:
    print("Info: OPENAI_API_KEY not configured. Beautify function will run in basic mode without AI enhancements.")

def handler(event, context):
    try:
        http_method = event['httpMethod']
        path = event['resource']

        if http_method == 'POST' and path == '/admin/beautify-chef':
            return beautify_chef_data(event)
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'error': 'Not found'})
            }

    except Exception as e:
        print(f"Error: {str(e)}")
        # Check if this is a Secrets Manager error
        if "SecretsManager" in str(e) and "ResourceNotFoundException" in str(e):
            print("Secrets Manager secret not found - this is expected if OpenAI integration is not configured")
            # Return a response that indicates the service is available but AI features are disabled
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({
                    'message': 'Beautify service available',
                    'aiFeatures': 'disabled',
                    'reason': 'OpenAI API key not configured'
                })
            }
        else:
            return {
                'statusCode': 500,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'error': 'Internal server error'})
            }

def beautify_chef_data(event):
    """Beautify chef data using AI to enhance descriptions and details"""
    try:
        body = json.loads(event['body'])
        chef_data = body.get('chefData', {})

        if not chef_data:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'error': 'Missing chef data'})
            }

        # Check if OpenAI API key is available
        if not OPENAI_API_KEY:
            return {
                'statusCode': 500,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'error': 'AI beautification service not configured'})
            }

        # Beautify each section using AI
        beautified_data = {}

        # Beautify description
        if 'description' in chef_data and chef_data['description']:
            beautified_data['description'] = beautify_text(
                chef_data['description'],
                f"Enhance this chef description to be more detailed, professional, and engaging. "
                f"Make it approximately 3-4 sentences long, highlighting the chef's expertise, "
                f"passion, and unique qualities. Cuisine type: {chef_data.get('cuisine', 'gourmet')}"
            )

        # Beautify specialties
        if 'specialties' in chef_data and chef_data['specialties']:
            beautified_data['specialties'] = beautify_list(
                chef_data['specialties'],
                chef_data.get('cuisine', 'gourmet')
            )

        # Beautify pricing notes
        if 'pricing' in chef_data and chef_data['pricing']:
            beautified_data['pricing'] = []
            for price in chef_data['pricing']:
                if 'note' in price and price['note']:
                    beautified_price = price.copy()
                    beautified_price['note'] = beautify_text(
                        price['note'],
                        f"Enhance this pricing description to be more detailed and professional. "
                        f"Make it clear what's included and any special conditions. "
                        f"Service type: {price.get('type', 'Dinner Service')}"
                    )
                    beautified_data['pricing'].append(beautified_price)
                else:
                    beautified_data['pricing'].append(price)

        # Beautify menu options
        if 'menuOptions' in chef_data and chef_data['menuOptions']:
            beautified_data['menuOptions'] = {}
            for category, items in chef_data['menuOptions'].items():
                if items and len(items) > 0:
                    # Beautify menu item descriptions
                    beautified_items = []
                    for item in items:
                        beautified_item = beautify_text(
                            item,
                            f"Enhance this menu item description to be more appetizing and detailed. "
                            f"Make it sound delicious and professional. "
                            f"Cuisine: {chef_data.get('cuisine', 'gourmet')}, Category: {category}"
                        )
                        beautified_items.append(beautified_item)
                    beautified_data['menuOptions'][category] = beautified_items
                else:
                    beautified_data['menuOptions'][category] = items

        # Beautify reviews if needed
        if 'reviews' in chef_data and chef_data['reviews']:
            beautified_data['reviews'] = []
            for review in chef_data['reviews']:
                if 'text' in review and review['text']:
                    beautified_review = review.copy()
                    beautified_review['text'] = beautify_text(
                        review['text'],
                        "Enhance this customer review to be more detailed and expressive while "
                        "maintaining the original sentiment and meaning. Make it sound like "
                        "an authentic, enthusiastic review."
                    )
                    beautified_data['reviews'].append(beautified_review)
                else:
                    beautified_data['reviews'].append(review)

        # Merge beautified data with original
        final_data = {**chef_data, **beautified_data}

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'message': 'Chef data beautified successfully',
                'beautifiedChefData': final_data,
                'originalChefData': chef_data
            })
        }

    except Exception as e:
        print(f"Error beautifying chef data: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'error': 'Failed to beautify chef data'})
        }

def beautify_text(original_text, prompt_context):
    """Use OpenAI to enhance and beautify text"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional content enhancer specializing in chef profiles and culinary descriptions. "
                              "Your responses should be detailed, engaging, and maintain a professional tone suitable "
                              "for a premium chef services website."
                },
                {
                    "role": "user",
                    "content": f"Original text: '{original_text}'\n\nContext: {prompt_context}\n\n"
                              f"Please enhance this text following the instructions in the context. "
                              f"Make it more detailed, professional, and engaging while preserving the original meaning."
                }
            ],
            temperature=0.7,
            max_tokens=150,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        return response.choices[0].message['content'].strip()

    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        # Fallback: return original text if AI fails
        return original_text

def beautify_list(original_list, cuisine_type):
    """Enhance a list of items (like specialties) using AI"""
    try:
        items_str = ", ".join(original_list)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a culinary expert helping to enhance chef specialty lists. "
                              "Make each item more specific, professional, and appetizing."
                },
                {
                    "role": "user",
                    "content": f"Original specialties: {items_str}\n\nCuisine type: {cuisine_type}\n\n"
                              f"Please enhance each specialty to be more specific and professional. "
                              f"For example, instead of 'Italian', you might suggest 'Authentic Northern Italian cuisine' "
                              f"or 'Handmade pasta specialties'. Provide an enhanced list."
                }
            ],
            temperature=0.7,
            max_tokens=200,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        # Parse the response to extract the enhanced list
        enhanced_text = response.choices[0].message['content'].strip()

        # Try to extract list items (simple parsing)
        if "," in enhanced_text:
            return [item.strip() for item in enhanced_text.split(",")]
        elif "\n" in enhanced_text:
            return [item.strip() for item in enhanced_text.split("\n") if item.strip()]
        else:
            return [enhanced_text]

    except Exception as e:
        print(f"OpenAI API error for list beautification: {str(e)}")
        # Fallback: return original list if AI fails
        return original_list

# Export for testing
if __name__ == "__main__":
    # Test data
    test_chef = {
        "name": "Test Chef",
        "cuisine": "Italian",
        "description": "Great chef",
        "specialties": ["Pasta", "Pizza"],
        "pricing": [{"type": "Dinner", "price": "$75", "note": "Min 2 hours"}],
        "menuOptions": {"Dinner": ["Spaghetti", "Lasagna"]},
        "reviews": [{"reviewer": "Test", "stars": "★★★★★", "text": "Good food"}]
    }

    # Mock OpenAI for testing
    class MockResponse:
        def __init__(self, content):
            self.choices = [type('obj', (object,), {'message': {'content': content}})]

    openai.ChatCompletion.create = lambda **kwargs: MockResponse("Enhanced description")

    result = beautify_chef_data(type('obj', (object,), {
        'httpMethod': 'POST',
        'resource': '/admin/beautify-chef',
        'body': json.dumps({'chefData': test_chef})
    }))

    print("Test result:", result)
