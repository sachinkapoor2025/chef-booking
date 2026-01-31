import json
import boto3
import os
import uuid
from datetime import datetime
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')

SUBMISSIONS_TABLE = os.environ['SUBMISSIONS_TABLE']
WEEKLY_SUBMISSIONS_TABLE = os.environ['WEEKLY_SUBMISSIONS_TABLE']

def handler(event, context):
    try:
        # Parse the form data from the API Gateway event
        body = json.loads(event['body'])
        form_type = body.get('formType', 'general')
        form_data = body.get('data', {})

        # Generate unique ID
        submission_id = str(uuid.uuid4())

        # Prepare item for DynamoDB
        item = {
            'id': submission_id,
            'formType': form_type,
            'data': form_data,
            'timestamp': datetime.utcnow().isoformat()
        }

        # Store in appropriate DynamoDB table based on form type
        if form_type == 'book-weekly':
            table = dynamodb.Table(WEEKLY_SUBMISSIONS_TABLE)
        else:
            table = dynamodb.Table(SUBMISSIONS_TABLE)
        table.put_item(Item=item)

        # Send email
        send_email(form_type, form_data)

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'message': 'Form submitted successfully'})
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }

def send_email(form_type, data):
    try:
        # Format the email body
        body = f"New {form_type} submission:\n\n"
        for key, value in data.items():
            body += f"{key}: {value}\n"

        # Set subject based on form type
        if form_type == 'book-chef':
            subject = 'Chef Requirement - Chef Services'
        elif form_type == 'book-weekly':
            subject = 'Weekly Service Requirement - Chef Services'
        elif form_type == 'contact':
            subject = 'Contact Requirement - Chef Services'
        else:
            subject = f'New {form_type} Submission'

        # Send email using SES
        response = ses.send_email(
            Source='chef@mydgv.com',  # Replace with your verified SES email
            Destination={
                'ToAddresses': ['dgv@mydgv.com', 'amanmanrai1@gmail.com']  # Replace with your admin emails
            },
            Message={
                'Subject': {
                    'Data': subject
                },
                'Body': {
                    'Text': {
                        'Data': body
                    }
                }
            }
        )
        print(f"Email sent: {response['MessageId']}")
    except ClientError as e:
        print(f"Failed to send email: {e.response['Error']['Message']}")
