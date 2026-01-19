import json
import boto3
import os
import hashlib
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')

SUBMISSIONS_TABLE = os.environ['SUBMISSIONS_TABLE']
ADMIN_CREDENTIALS_TABLE = os.environ['ADMIN_CREDENTIALS_TABLE']

def handler(event, context):
    try:
        http_method = event['httpMethod']
        path = event['resource']

        if http_method == 'POST' and path == '/admin/login':
            return login(event)
        elif http_method == 'GET' and path.startswith('/admin/data/'):
            return get_data(event)
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
