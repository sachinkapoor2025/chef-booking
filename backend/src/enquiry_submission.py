import json
import boto3
import os
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
import re

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
submissions_table = dynamodb.Table(os.environ['SUBMISSIONS_TABLE'])

def lambda_handler(event, context):
    """
    Lambda function to handle Live Counter/Enquiry form submissions
    """
    try:
        # Parse the request body safely
        if 'body' not in event or event['body'] is None or event['body'] == "":
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({
                    'success': False,
                    'message': 'No request body provided'
                })
            }

        try:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({
                    'success': False,
                    'message': 'Invalid JSON format in request body'
                })
            }

        # Validate required fields
        required_fields = ['name', 'email', 'phone']

        missing_fields = [field for field in required_fields if not body.get(field)]

        if missing_fields:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({
                    'success': False,
                    'message': f'Missing required fields: {", ".join(missing_fields)}'
                })
            }

        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, body['email']):
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({
                    'success': False,
                    'message': 'Invalid email format'
                })
            }

        # Validate phone number
        phone_pattern = r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$'
        if not re.match(phone_pattern, body['phone']):
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({
                    'success': False,
                    'message': 'Invalid phone number format'
                })
            }

        # Validate guest count if provided
        guests = None
        if body.get('guests'):
            try:
                guests = int(body['guests'])
                if guests < 1 or guests > 5000:
                    return {
                        'statusCode': 400,
                        'headers': {
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                            'Access-Control-Allow-Methods': 'POST,OPTIONS'
                        },
                        'body': json.dumps({
                            'success': False,
                            'message': 'Number of guests must be between 1 and 5000'
                        })
                    }
            except ValueError:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                        'Access-Control-Allow-Methods': 'POST,OPTIONS'
                    },
                    'body': json.dumps({
                        'success': False,
                        'message': 'Invalid guest count'
                    })
                }

        # Build the submission record
        submission_id = str(uuid.uuid4())
        submission_time = datetime.utcnow().isoformat()

        # Get services interested in
        services = []
        if 'services' in body:
            if isinstance(body['services'], list):
                services = body['services']
            else:
                services = [body['services']]

        # Build submission record
        submission_record = {
            'id': submission_id,
            'formType': 'enquiry',
            'submissionTime': submission_time,
            'name': body['name'],
            'email': body['email'],
            'phone': body['phone'],
            'eventType': body.get('event_type', ''),
            'eventDate': body.get('event_date', ''),
            'guests': guests,
            'services': services,
            'message': body.get('message', ''),
            'status': 'pending'
        }

        # Save to DynamoDB
        submissions_table.put_item(Item=submission_record)

        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Enquiry submitted successfully',
                'submissionId': submission_id
            })
        }

    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'success': False,
                'message': 'Internal server error'
            })
        }

    except Exception as e:
        print(f"Error processing request: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'success': False,
                'message': 'Internal server error'
            })
        }
