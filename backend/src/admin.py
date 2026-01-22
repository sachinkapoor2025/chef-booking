import json
import boto3
import os
import hashlib
from botocore.exceptions import ClientError
from decimal import Decimal
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')

SUBMISSIONS_TABLE = os.environ['SUBMISSIONS_TABLE']
ADMIN_CREDENTIALS_TABLE = os.environ['ADMIN_CREDENTIALS_TABLE']
WEEKLY_SUBMISSIONS_TABLE = os.environ['WEEKLY_SUBMISSIONS_TABLE']
CHEF_TABLE = os.environ['CHEF_TABLE']


# =========================
# COMMON HELPERS
# =========================

def cors_headers():
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS'
    }


def debug_log(title, data):
    print(f"\n===== {title} =====")
    try:
        print(json.dumps(data, indent=2, default=str))
    except Exception:
        print(data)
    print("===== END =====\n")


def convert_numbers(obj):
    """
    Recursively convert int/float to Decimal for DynamoDB
    """
    if isinstance(obj, list):
        return [convert_numbers(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_numbers(v) for k, v in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, int):
        return Decimal(obj)
    else:
        return obj


# =========================
# MAIN HANDLER
# =========================

def handler(event, context):
    try:
        http_method = event.get('httpMethod')
        path = event.get('resource')

        debug_log("RAW API GATEWAY EVENT", event)

        if http_method == 'POST' and path == '/admin/login':
            return login(event)

        elif http_method == 'GET' and path.startswith('/admin/data/'):
            return get_data(event)

        elif http_method == 'GET' and path in ['/admin/chefs', '/chefs']:
            return get_chefs()

        elif http_method == 'POST' and path == '/admin/chefs':
            return add_chef(event)

        elif http_method == 'GET' and path == '/admin/s3-presigned-url':
            return generate_presigned_url(event)

        elif http_method == 'GET' and path == '/admin/weekly-data':
            return get_weekly_data()

        return {
            'statusCode': 404,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Not found'})
        }

    except Exception as e:
        print("UNHANDLED ERROR:", str(e))
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Internal server error'})
        }


# =========================
# LOGIN
# =========================

def login(event):
    body = json.loads(event['body'])
    username = body.get('username')
    password = body.get('password')

    table = dynamodb.Table(ADMIN_CREDENTIALS_TABLE)

    response = table.get_item(Key={'username': username})
    if 'Item' not in response:
        return {'statusCode': 401, 'headers': cors_headers(), 'body': json.dumps({'error': 'Invalid credentials'})}

    stored_hash = response['Item']['password_hash']
    if hashlib.sha256(password.encode()).hexdigest() == stored_hash:
        return {'statusCode': 200, 'headers': cors_headers(), 'body': json.dumps({'message': 'Login successful'})}

    return {'statusCode': 401, 'headers': cors_headers(), 'body': json.dumps({'error': 'Invalid credentials'})}


# =========================
# GET DATA
# =========================

def get_data(event):
    form_type = event['pathParameters']['formType']
    table = dynamodb.Table(SUBMISSIONS_TABLE)

    response = table.query(
        IndexName='formType-index',
        KeyConditionExpression=Key('formType').eq(form_type)
    )

    return {
        'statusCode': 200,
        'headers': cors_headers(),
        'body': json.dumps(response['Items'], default=str)
    }


# =========================
# GET CHEFS
# =========================

def get_chefs():
    table = dynamodb.Table(CHEF_TABLE)
    response = table.scan()

    def convert_decimals(obj):
        if isinstance(obj, list):
            return [convert_decimals(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: convert_decimals(v) for k, v in obj.items()}
        elif isinstance(obj, Decimal):
            return float(obj)
        return obj

    items = [convert_decimals(i) for i in response['Items']]

    return {
        'statusCode': 200,
        'headers': cors_headers(),
        'body': json.dumps(items)
    }


# =========================
# ADD CHEF (FIXED + LOGGED)
# =========================

def add_chef(event):
    body = json.loads(event['body'])
    chef_data = body.get('chefData', {})

    debug_log("RAW CHEF DATA FROM UI", chef_data)

    required_fields = [
        'name', 'location', 'cuisine', 'imageUrl',
        'description', 'specialties', 'pricing',
        'menuOptions', 'dietaryTags', 'reviews'
    ]

    for field in required_fields:
        if field not in chef_data:
            return {
                'statusCode': 400,
                'headers': cors_headers(),
                'body': json.dumps({'error': f'Missing required field: {field}'})
            }

    debug_log("PRICING FIELD (RAW)", chef_data.get("pricing"))
    debug_log("RATING FIELD", {
        "value": chef_data.get("rating"),
        "type": str(type(chef_data.get("rating")))
    })

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

    # 🔥 CRITICAL FIX
    item = convert_numbers(item)

    debug_log("FINAL ITEM BEFORE DYNAMODB PUT", item)

    table = dynamodb.Table(CHEF_TABLE)
    try:
        table.put_item(Item=item)
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({'message': 'Chef added successfully'})
        }
    except Exception as e:
        print("DYNAMODB ERROR:", str(e))
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': str(e)})
        }


# =========================
# S3 PRE-SIGNED URL GENERATOR
# =========================

def generate_presigned_url(event):
    import boto3
    import uuid
    import os

    # Extract filename from query parameters
    filename = event.get('queryStringParameters', {}).get('filename', 'unknown-file')

    # Generate unique filename to prevent collisions
    unique_filename = f"images/add-chef/{uuid.uuid4()}_{filename}"

    # Create S3 client
    s3 = boto3.client('s3')
    bucket_name = 'maharajachefservices.com'  # Replace with actual bucket name

    try:
        # Generate pre-signed URL for PUT operation
        presigned_url = s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': unique_filename,
                'ContentType': 'image/*'
            },
            ExpiresIn=3600  # URL expires in 1 hour
        )

        # Return the pre-signed URL and the final public URL
        public_url = f"https://{bucket_name}/{unique_filename}"

        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'presignedUrl': presigned_url,
                'publicUrl': public_url,
                'filename': unique_filename
            })
        }

    except Exception as e:
        print("S3 PRE-SIGNED URL ERROR:", str(e))
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

# =========================
# WEEKLY DATA
# =========================

def get_weekly_data():
    table = dynamodb.Table(WEEKLY_SUBMISSIONS_TABLE)
    response = table.scan()
    return {
        'statusCode': 200,
        'headers': cors_headers(),
        'body': json.dumps(response['Items'], default=str)
    }
