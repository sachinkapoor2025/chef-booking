"""
New Lambda function for Enquiry Form submission
Handles Live Counter / Speciality enquiries
"""
import json
import boto3
import os
import uuid
from datetime import datetime
from botocore.exceptions import ClientError

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('SUBMISSIONS_TABLE', 'chef-services-submissions')
enquiries_table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    """
    Handle enquiry form submissions
    """
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': ''
        }
    
    try:
        # Parse body
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body)
        
        # Extract fields
        name = body.get('name', '').strip()
        email = body.get('email', '').strip()
        phone = body.get('phone', '').strip()
        event_date = body.get('event_date', '')
        event_type = body.get('event_type', '')
        guests = body.get('guests', '')
        message = body.get('message', '')
        services = body.get('services', [])
        
        # Validation
        if not name:
            return error_response('Name is required')
        if not email:
            return error_response('Email is required')
        if not phone:
            return error_response('Phone number is required')
        
        # Validate email format
        if '@' not in email or '.' not in email.split('@')[-1]:
            return error_response('Invalid email format')
        
        # Create submission record
        submission_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        item = {
            'id': submission_id,
            'type': 'enquiry_form',
            'timestamp': timestamp,
            'name': name,
            'email': email,
            'phone': phone,
            'eventDate': event_date,
            'eventType': event_type,
            'guests': int(guests) if guests and str(guests).isdigit() else 0,
            'services': services if isinstance(services, list) else [services],
            'message': message,
            'status': 'new'
        }
        
        # Save to DynamoDB
        enquiries_table.put_item(Item=item)
        
        # Return success
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'POST,OPTIONS',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Enquiry submitted successfully!',
                'submissionId': submission_id
            })
        }
        
    except ClientError as e:
        print(f"DynamoDB error: {str(e)}")
        return error_response('Database error occurred')
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return error_response('An error occurred while processing your request')


def error_response(message):
    """Return error response"""
    return {
        'statusCode': 400,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'POST,OPTIONS',
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'success': False,
            'message': message
        })
    }
