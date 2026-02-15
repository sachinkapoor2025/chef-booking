import json
import boto3
import os
from datetime import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# Environment variables
BOOKINGS_TABLE = os.environ['BOOKINGS_TABLE']
S3_BUCKET = os.environ['S3_BUCKET']

def lambda_handler(event, context):
    """
    Lambda function to handle book a chef form submissions
    """
    try:
        # Parse the incoming request
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
            
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'event-type', 'event-date', 'location', 'guests']
        for field in required_fields:
            if field not in body:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'POST,OPTIONS'
                    },
                    'body': json.dumps({
                        'error': f'Missing required field: {field}'
                    })
                }
        
        # Generate booking ID
        booking_id = f"BOOK-{datetime.now().strftime('%Y%m%d%H%M%S')}-{body['name'].replace(' ', '').upper()[:3]}"
        
        # Prepare booking data
        booking_data = {
            'booking_id': booking_id,
            'name': body['name'],
            'email': body['email'],
            'phone': body['phone'],
            'event_type': body['event-type'],
            'event_date': body['event-date'],
            'event_time': f"{body.get('event-hour', '12')}:{body.get('event-minute', '00')} {body.get('event-ampm', 'PM')}",
            'location': body['location'],
            'guests': int(body['guests']),
            'dietary_preferences': body.get('dietary', ''),
            'message': body.get('message', ''),
            'status': 'PENDING',
            'created_at': datetime.now().isoformat(),
            'form_type': 'book-chef'
        }
        
        # Save to DynamoDB
        table = dynamodb.Table(BOOKINGS_TABLE)
        table.put_item(Item=booking_data)
        
        # Save to S3 for backup
        s3_key = f"bookings/{booking_id}.json"
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(booking_data, indent=2),
            ContentType='application/json'
        )
        
        # Send confirmation email (optional)
        send_confirmation_email(booking_data)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'message': 'Booking request submitted successfully!',
                'booking_id': booking_id,
                'status': 'PENDING'
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing booking: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Failed to process booking request',
                'details': str(e)
            })
        }

def send_confirmation_email(booking_data):
    """
    Send confirmation email to the customer
    """
    try:
        ses = boto3.client('ses')
        
        # Email content
        subject = f"Booking Confirmation - {booking_data['booking_id']}"
        
        body_text = f"""
        Dear {booking_data['name']},

        Thank you for booking with Maharaja Chef Services!

        Your booking details:
        - Booking ID: {booking_data['booking_id']}
        - Event Type: {booking_data['event_type']}
        - Event Date: {booking_data['event_date']}
        - Event Time: {booking_data['event_time']}
        - Location: {booking_data['location']}
        - Number of Guests: {booking_data['guests']}
        - Status: {booking_data['status']}

        We will contact you shortly to confirm your booking and discuss menu options.

        Best regards,
        Maharaja Chef Services Team
        """
        
        body_html = f"""
        <html>
        <head></head>
        <body>
            <h2>Booking Confirmation</h2>
            <p>Dear {booking_data['name']},</p>
            <p>Thank you for booking with Maharaja Chef Services!</p>
            
            <h3>Your booking details:</h3>
            <ul>
                <li><strong>Booking ID:</strong> {booking_data['booking_id']}</li>
                <li><strong>Event Type:</strong> {booking_data['event_type']}</li>
                <li><strong>Event Date:</strong> {booking_data['event_date']}</li>
                <li><strong>Event Time:</strong> {booking_data['event_time']}</li>
                <li><strong>Location:</strong> {booking_data['location']}</li>
                <li><strong>Number of Guests:</strong> {booking_data['guests']}</li>
                <li><strong>Status:</strong> {booking_data['status']}</li>
            </ul>
            
            <p>We will contact you shortly to confirm your booking and discuss menu options.</p>
            
            <p>Best regards,<br>
            Maharaja Chef Services Team</p>
        </body>
        </html>
        """
        
        # Send email
        response = ses.send_email(
            Source='noreply@maharajachef.com',  # Replace with your verified email
            Destination={
                'ToAddresses': [booking_data['email']]
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
        
        logger.info(f"Confirmation email sent to {booking_data['email']}")
        
    except Exception as e:
        logger.error(f"Failed to send confirmation email: {str(e)}")
        # Don't fail the booking if email fails