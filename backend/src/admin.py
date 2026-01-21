import json
import boto3
import os
import hashlib
from botocore.exceptions import ClientError
from decimal import Decimal
from boto3.dynamodb.types import TypeDeserializer

# Set up DynamoDB type deserializer to handle Decimal types
type_deserializer = TypeDeserializer()

dynamodb = boto3.resource('dynamodb')

SUBMISSIONS_TABLE = os.environ['SUBMISSIONS_TABLE']
ADMIN_CREDENTIALS_TABLE = os.environ['ADMIN_CREDENTIALS_TABLE']
WEEKLY_SUBMISSIONS_TABLE = os.environ['WEEKLY_SUBMISSIONS_TABLE']
CHEF_TABLE = os.environ['CHEF_TABLE']

def handler(event, context):
    try:
        http_method = event['httpMethod']
        path = event['resource']

        if http_method == 'POST' and path == '/admin/login':
            return login(event)
        elif http_method == 'GET' and path.startswith('/admin/data/'):
            return get_data(event)
        elif http_method == 'GET' and path == '/admin/chefs':
            return get_chefs()
        elif http_method == 'POST' and path == '/admin/chefs':
            return add_chef(event)
        elif http_method == 'GET' and path == '/chefs':
            return get_chefs()
        elif http_method == 'GET' and path == '/admin/weekly-data':
            return get_weekly_data()
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

def login(event):
    body = json.loads(event['body'])
    username = body.get('username')
    password = body.get('password')

    if not username or not password:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'error': 'Username and password required'})
        }

    table = dynamodb.Table(ADMIN_CREDENTIALS_TABLE)
    try:
        response = table.get_item(Key={'username': username})
        if 'Item' not in response:
            return {
                'statusCode': 401,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'error': 'Invalid credentials'})
            }

        stored_hash = response['Item']['password_hash']
        if hashlib.sha256(password.encode()).hexdigest() == stored_hash:
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'message': 'Login successful'})
            }
        else:
            return {
                'statusCode': 401,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'error': 'Invalid credentials'})
            }
    except ClientError as e:
        print(e)
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'error': 'Database error'})
        }

def get_data(event):
    form_type = event['pathParameters']['formType']

    table = dynamodb.Table(SUBMISSIONS_TABLE)
    try:
        response = table.query(
            IndexName='formType-index',  # Assuming we add a GSI for formType
            KeyConditionExpression=boto3.dynamodb.conditions.Key('formType').eq(form_type)
        )
        items = response['Items']

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps(items)
        }
    except ClientError as e:
        print(e)
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps({'error': 'Database error'})
        }

def get_chefs():
    table = dynamodb.Table(CHEF_TABLE)
    try:
        response = table.scan()
        items = response['Items']

        # Convert Decimal objects to float for JSON serialization
        def convert_decimals(obj):
            if isinstance(obj, list):
                return [convert_decimals(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: convert_decimals(value) for key, value in obj.items()}
            elif isinstance(obj, Decimal):
                return float(obj)
            else:
                return obj

        # Apply the conversion to all items
        converted_items = [convert_decimals(item) for item in items]

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps(converted_items)
        }
    except ClientError as e:
        print(e)
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps({'error': 'Database error'})
        }

def add_chef(event):
    body = json.loads(event['body'])
    chef_data = body.get('chefData', {})

    # Validate required fields
    required_fields = ['name', 'location', 'cuisine', 'imageUrl', 'description', 'specialties', 'pricing', 'menuOptions', 'dietaryTags', 'reviews']
    for field in required_fields:
        if field not in chef_data:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'error': f'Missing required field: {field}'})
            }

    table = dynamodb.Table(CHEF_TABLE)
    try:
        # Generate chef ID
        chef_id = hashlib.md5(chef_data['name'].encode()).hexdigest()

        item = {
            'chefId': chef_id,
            'name': chef_data['name'],
            'location': chef_data['location'],
            'cuisine': chef_data['cuisine'],
            'imageUrl': chef_data['imageUrl'],
            'description': chef_data['description'],
            'specialties': chef_data['specialties'],
            'pricing': chef_data['pricing'],
            'menuOptions': chef_data['menuOptions'],
            'dietaryTags': chef_data['dietaryTags'],
            'reviews': chef_data['reviews'],
            'rating': chef_data.get('rating', 4.5),
            'reviewCount': chef_data.get('reviewCount', 0)
        }

        table.put_item(Item=item)

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'message': 'Chef added successfully'})
        }
    except ClientError as e:
        print(e)
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'error': 'Database error'})
        }

def get_weekly_data():
    table = dynamodb.Table(WEEKLY_SUBMISSIONS_TABLE)
    try:
        response = table.scan()
        items = response['Items']

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps(items)
        }
    except ClientError as e:
        print(e)
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps({'error': 'Database error'})
        }
