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

# Initialize SES for email
ses = boto3.client('ses')

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('SUBMISSIONS_TABLE', 'chef-services-backend-submissions')
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
            'formType': 'enquiry',
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
        
        # Send confirmation email
        send_confirmation_email(item)
        
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


def send_confirmation_email(enquiry_data):
    """
    Send confirmation email to the customer
    """
    try:
        # Email content
        subject = f"Live Counter - Enquiry"
        
        # Format services list
        services_list = ', '.join(enquiry_data.get('services', [])) if enquiry_data.get('services') else 'Not specified'
        
        body_text = f"""
        Dear {enquiry_data['name']},

        Thank you for your enquiry with Maharaja Chef Services!

        Your enquiry details:
        - Enquiry ID: {enquiry_data['id']}
        - Event Type: {enquiry_data.get('eventType', 'Not specified')}
        - Event Date: {enquiry_data.get('eventDate', 'Not specified')}
        - Location: {enquiry_data.get('location', 'Not specified')}
        - Number of Guests: {enquiry_data.get('guests', 'Not specified')}
        - Services Interested In: {services_list}
        - Contact Number: {enquiry_data['phone']}
        - Message: {enquiry_data.get('message', 'Not specified')}

        We will contact you shortly to discuss your requirements and provide a quote.

        Best regards,
        Maharaja Chef Services Team
        """
        
        body_html = f"""
        <html>
        <head></head>
        <body>
            <h2>Enquiry Confirmation</h2>
            <p>Dear {enquiry_data['name']},</p>
            <p>Thank you for your enquiry with Maharaja Chef Services!</p>
            
            <h3>Your enquiry details:</h3>
            <ul>
                <li><strong>Enquiry ID:</strong> {enquiry_data['id']}</li>
                <li><strong>Event Type:</strong> {enquiry_data.get('eventType', 'Not specified')}</li>
                <li><strong>Event Date:</strong> {enquiry_data.get('eventDate', 'Not specified')}</li>
                <li><strong>Location:</strong> {enquiry_data.get('location', 'Not specified')}</li>
                <li><strong>Number of Guests:</strong> {enquiry_data.get('guests', 'Not specified')}</li>
                <li><strong>Services Interested In:</strong> {services_list}</li>
                <li><strong>Contact Number:</strong> {enquiry_data['phone']}</li>
                <li><strong>Message:</strong> {enquiry_data.get('message', 'Not specified')}</li>
            </ul>
            
            <p>We will contact you shortly to discuss your requirements and provide a quote.</p>
            
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
        
        print(f"Confirmation email sent to {enquiry_data['email']}")
        
    except Exception as e:
        print(f"Failed to send confirmation email: {str(e)}")
        # Don't fail the enquiry if email fails
