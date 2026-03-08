import json
import boto3
import os
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
import re

# Initialize SES for email
ses = boto3.client('ses')

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
submissions_table = dynamodb.Table(os.environ['SUBMISSIONS_TABLE'])

def lambda_handler(event, context):
    """
    Lambda function to handle catering service form submissions
    """
    try:
        # ✅ Parse the request body safely (FIXED)
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
        required_fields = [
            'name', 'email', 'phone', 'event-type', 'event-date',
            'event-hour', 'event-minute', 'event-ampm', 'location',
            'guests', 'meal-type', 'service-type'
        ]

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

        # Validate guest count
        try:
            guests = int(body['guests'])
            if guests < 1 or guests > 1000:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                        'Access-Control-Allow-Methods': 'POST,OPTIONS'
                    },
                    'body': json.dumps({
                        'success': False,
                        'message': 'Number of guests must be between 1 and 1000'
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

        # Format event time
        event_time = f"{body['event-hour']}:{body['event-minute']} {body['event-ampm']}"

        # Get cuisine preferences
        cuisine_preferences = []
        if 'cuisine' in body and isinstance(body['cuisine'], list):
            cuisine_preferences = body['cuisine']
        elif 'cuisine' in body:
            cuisine_preferences = [body['cuisine']]

        # Add "other" cuisine if specified
        if body.get('cuisine-other'):
            cuisine_preferences.append(f"Other: {body['cuisine-other']}")

        # Get dietary requirements
        dietary_requirements = []
        if 'dietary' in body and isinstance(body['dietary'], list):
            dietary_requirements = body['dietary']
        elif 'dietary' in body:
            dietary_requirements = [body['dietary']]

        # Build submission record
        submission_record = {
            'id': submission_id,
            'formType': 'catering',
            'submissionTime': submission_time,
            'name': body['name'],
            'email': body['email'],
            'phone': body['phone'],
            'eventType': body['event-type'],
            'eventDate': body['event-date'],
            'eventTime': event_time,
            'location': body['location'],
            'guests': guests,
            'budget': body.get('budget', ''),
            'cuisinePreferences': cuisine_preferences,
            'mealType': body['meal-type'],
            'dietaryRequirements': dietary_requirements,
            'specialRequirements': body.get('special-requirements', ''),
            'serviceType': body['service-type'],
            'status': 'pending'
        }

        # Save to DynamoDB
        submissions_table.put_item(Item=submission_record)

        # Send confirmation email
        send_catering_confirmation_email(submission_record)

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
                'message': 'Catering enquiry submitted successfully',
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


def send_catering_confirmation_email(submission_data):
    """
    Send confirmation email to the customer for catering enquiry
    """
    try:
        # Email content
        subject = f"Party Catering - Enquiry"
        
        # Format cuisine preferences
        cuisine_list = ', '.join(submission_data.get('cuisinePreferences', [])) if submission_data.get('cuisinePreferences') else 'Not specified'
        
        # Format dietary requirements
        dietary_list = ', '.join(submission_data.get('dietaryRequirements', [])) if submission_data.get('dietaryRequirements') else 'Not specified'
        
        body_text = f"""
        Dear {submission_data['name']},

        Thank you for your catering enquiry with Maharaja Chef Services!

        Your enquiry details:
        - Enquiry ID: {submission_data['id']}
        - Event Type: {submission_data.get('eventType', 'Not specified')}
        - Event Date: {submission_data.get('eventDate', 'Not specified')}
        - Event Time: {submission_data.get('eventTime', 'Not specified')}
        - Location: {submission_data.get('location', 'Not specified')}
        - Number of Guests: {submission_data.get('guests', 'Not specified')}
        - Budget Range: {submission_data.get('budget', 'Not specified')}
        - Cuisine Preferences: {cuisine_list}
        - Meal Type: {submission_data.get('mealType', 'Not specified')}
        - Dietary Requirements: {dietary_list}
        - Service Type: {submission_data.get('serviceType', 'Not specified')}
        - Contact Number: {submission_data['phone']}
        - Special Requirements: {submission_data.get('specialRequirements', 'Not specified')}

        We will contact you shortly to discuss your catering requirements and provide a personalized quote.

        Best regards,
        Maharaja Chef Services Team
        """
        
        body_html = f"""
        <html>
        <head></head>
        <body>
            <h2>Catering Enquiry Confirmation</h2>
            <p>Dear {submission_data['name']},</p>
            <p>Thank you for your catering enquiry with Maharaja Chef Services!</p>
            
            <h3>Your enquiry details:</h3>
            <ul>
                <li><strong>Enquiry ID:</strong> {submission_data['id']}</li>
                <li><strong>Event Type:</strong> {submission_data.get('eventType', 'Not specified')}</li>
                <li><strong>Event Date:</strong> {submission_data.get('eventDate', 'Not specified')}</li>
                <li><strong>Event Time:</strong> {submission_data.get('eventTime', 'Not specified')}</li>
                <li><strong>Location:</strong> {submission_data.get('location', 'Not specified')}</li>
                <li><strong>Number of Guests:</strong> {submission_data.get('guests', 'Not specified')}</li>
                <li><strong>Budget Range:</strong> {submission_data.get('budget', 'Not specified')}</li>
                <li><strong>Cuisine Preferences:</strong> {cuisine_list}</li>
                <li><strong>Meal Type:</strong> {submission_data.get('mealType', 'Not specified')}</li>
                <li><strong>Dietary Requirements:</strong> {dietary_list}</li>
                <li><strong>Service Type:</strong> {submission_data.get('serviceType', 'Not specified')}</li>
                <li><strong>Contact Number:</strong> {submission_data['phone']}</li>
                <li><strong>Special Requirements:</strong> {submission_data.get('specialRequirements', 'Not specified')}</li>
            </ul>
            
            <p>We will contact you shortly to discuss your catering requirements and provide a personalized quote.</p>
            
            <p>Best regards,<br>
            Maharaja Chef Services Team</p>
        </body>
        </html>
        """
        
        # Send email
        response = ses.send_email(
            Source='chef@mydgv.com',  # Replace with your verified SES email
            Destination={
                'ToAddresses': ['dgv@mydgv.com', 'priya.yadav@mydgv.com', 'amanmanrai1@gmail.com', 'aman@thegreatmaharaja.com', 'info@maharajachef.com']  # Replace with your admin emails
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': body_text,
                        'Charset': 'UTF-8'
                    },
                    'Html': {
                        'Data': body_html,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        
        print(f"Catering confirmation email sent to {submission_data['email']}")
        
    except Exception as e:
        print(f"Failed to send catering confirmation email: {str(e)}")
        # Don't fail the enquiry if email fails
