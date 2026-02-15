import json
import boto3
import os
import uuid
import logging
from datetime import datetime
import base64
import urllib.parse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
ses = boto3.client('ses')

# Environment variables
CHEF_APPLICATION_TABLE = os.environ['CHEF_APPLICATION_TABLE']
CHEF_APPLICATION_BUCKET = os.environ['CHEF_APPLICATION_BUCKET']
FROM_EMAIL = os.environ['FROM_EMAIL']


def lambda_handler(event, context):
    """
    Lambda function to handle chef application form submissions
    """

    # ✅ Handle CORS preflight request (OPTIONS)
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST,OPTIONS"
            },
            "body": json.dumps({"message": "CORS preflight success"})
        }

    try:
        logger.info("Event received: %s", json.dumps(event))

        # Parse the incoming request
        if 'body' in event and event['body'] is not None:
            body = event['body']
            is_base64 = event.get('isBase64Encoded', False)

            if is_base64:
                body = base64.b64decode(body).decode('utf-8')

            # Try JSON first
            try:
                application_data = json.loads(body)
            except Exception:
                # If not JSON, check content type and parse accordingly
                content_type = event.get('headers', {}).get('content-type', '')
                if 'multipart/form-data' in content_type:
                    application_data = parse_multipart_form_data(body, content_type)
                else:
                    # Handle URL-encoded form data
                    application_data = parse_form_data(body)

        else:
            application_data = event

        logger.info("Parsed application data: %s", json.dumps(application_data))

        # Validate required fields
        required_fields = [
            'fullName',
            'email',
            'phone',
            'location',
            'experience',
            'specialty',
            'culinaryPhilosophy',
            'availability'
        ]

        for field in required_fields:
            if field not in application_data or str(application_data[field]).strip() == "":
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

        # Generate application ID
        application_id = f"CHEF-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"

        # Prepare application data
        chef_application = {
            'applicationId': application_id,
            'fullName': application_data['fullName'].strip(),
            'email': application_data['email'].strip(),
            'phone': application_data['phone'].strip(),
            'location': application_data['location'].strip(),
            'experience': application_data['experience'].strip(),
            'specialty': application_data['specialty'].strip(),
            'certifications': application_data.get('certifications', '').strip(),
            'website': application_data.get('website', '').strip(),
            'culinaryPhilosophy': application_data['culinaryPhilosophy'].strip(),
            'availability': application_data['availability'].strip(),
            'termsAgreement': application_data.get('termsAgreement', False),
            'backgroundCheck': application_data.get('backgroundCheck', False),
            'newsletterSignup': application_data.get('newsletterSignup', False),
            'status': 'PENDING',
            'submittedAt': datetime.now().isoformat(),
            'resumeUploaded': False,
            'photosUploaded': False
        }

        # Save to DynamoDB
        table = dynamodb.Table(CHEF_APPLICATION_TABLE)
        table.put_item(Item=chef_application)

        logger.info(f"Saved chef application to DynamoDB: {application_id}")

        # Send confirmation email
        send_confirmation_email(chef_application)

        # Send admin notification email
        send_admin_notification(chef_application)

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'message': 'Chef application submitted successfully!',
                'applicationId': application_id,
                'status': 'PENDING'
            })
        }

    except Exception as e:
        logger.error(f"Error processing chef application: {str(e)}")

        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Failed to process chef application',
                'details': str(e)
            })
        }


def parse_form_data(body):
    """
    Parse form data from URL-encoded string
    """
    parsed_data = {}
    pairs = body.split('&')

    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            key = urllib.parse.unquote_plus(key)
            value = urllib.parse.unquote_plus(value)
            parsed_data[key] = value

    return parsed_data


def parse_multipart_form_data(body, content_type):
    """
    Parse multipart form data (handles file uploads)
    """
    import re
    
    # Extract boundary from content-type
    boundary_match = re.search(r'boundary=([^;]+)', content_type)
    if not boundary_match:
        raise ValueError("No boundary found in multipart form data")
    
    boundary = boundary_match.group(1)
    boundary_line = f'--{boundary}'
    
    # Split body by boundary
    parts = body.split(boundary_line)
    
    # Remove first and last empty parts
    if parts and not parts[0].strip():
        parts.pop(0)
    if parts and not parts[-1].strip():
        parts.pop(-1)
    
    parsed_data = {}
    
    for part in parts:
        if not part.strip():
            continue
            
        # Split headers and content
        if '\r\n\r\n' in part:
            headers_part, content = part.split('\r\n\r\n', 1)
        else:
            continue
        
        # Parse headers
        headers = {}
        for line in headers_part.strip().split('\r\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip().lower()] = value.strip()
        
        # Check if this is a form field
        if 'content-disposition' in headers:
            content_disposition = headers['content-disposition']
            name_match = re.search(r'name="([^"]+)"', content_disposition)
            
            if name_match:
                field_name = name_match.group(1)
                
                # Remove trailing \r\n from content
                content = content.rstrip('\r\n')
                
                # For file uploads, we'll just store the filename for now
                if 'filename=' in content_disposition:
                    filename_match = re.search(r'filename="([^"]*)"', content_disposition)
                    if filename_match:
                        filename = filename_match.group(1)
                        if filename:  # Only add if filename is not empty
                            parsed_data[field_name] = filename
                else:
                    # Regular form field
                    parsed_data[field_name] = content
    
    return parsed_data


def send_confirmation_email(application_data):
    """
    Send confirmation email to the applicant
    """
    try:
        subject = f"Chef Application Received - {application_data['applicationId']}"

        body_text = f"""
Dear {application_data['fullName']},

Thank you for applying to join Maharaja Chef Services!

Your application has been successfully received.

Application Details:
- Application ID: {application_data['applicationId']}
- Name: {application_data['fullName']}
- Email: {application_data['email']}
- Phone: {application_data['phone']}
- Location: {application_data['location']}
- Experience: {application_data['experience']}
- Specialty: {application_data['specialty']}
- Availability: {application_data['availability']}
- Submitted: {application_data['submittedAt']}

Our team will review your application within 3-5 business days.
You will receive an email notification regarding our decision.

Best regards,
The Maharaja Chef Services Team
"""

        body_html = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: white; padding: 20px; text-align: center; border-radius: 8px; }}
        .content {{ background: #f8fafc; padding: 20px; border-radius: 8px; margin-top: 20px; }}
        .details {{ background: white; padding: 15px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #3b82f6; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🎉 Chef Application Received!</h2>
            <p>Thank you for applying to Maharaja Chef Services</p>
        </div>

        <div class="content">
            <p>Dear <strong>{application_data['fullName']}</strong>,</p>

            <p>Your chef application has been successfully received.</p>

            <div class="details">
                <h3>Application Details:</h3>
                <ul>
                    <li><strong>Application ID:</strong> {application_data['applicationId']}</li>
                    <li><strong>Name:</strong> {application_data['fullName']}</li>
                    <li><strong>Email:</strong> {application_data['email']}</li>
                    <li><strong>Phone:</strong> {application_data['phone']}</li>
                    <li><strong>Location:</strong> {application_data['location']}</li>
                    <li><strong>Experience:</strong> {application_data['experience']}</li>
                    <li><strong>Specialty:</strong> {application_data['specialty']}</li>
                    <li><strong>Availability:</strong> {application_data['availability']}</li>
                    <li><strong>Submitted:</strong> {application_data['submittedAt']}</li>
                </ul>
            </div>

            <p>Our team will review your application within 3-5 business days.</p>

            <p>Best regards,<br>
            <strong>The Maharaja Chef Services Team</strong></p>
        </div>

        <div class="footer">
            <p>For questions, contact us at info@maharajachef.com</p>
            <p>&copy; 2024 Maharaja Chef Services. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""

        ses.send_email(
            Source=FROM_EMAIL,
            Destination={'ToAddresses': [application_data['email']]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Text': {'Data': body_text, 'Charset': 'UTF-8'},
                    'Html': {'Data': body_html, 'Charset': 'UTF-8'}
                }
            }
        )

        logger.info(f"Confirmation email sent to {application_data['email']}")

    except Exception as e:
        logger.error(f"Failed to send confirmation email: {str(e)}")


def send_admin_notification(application_data):
    """
    Send notification email to admin about new chef application
    """
    try:
        subject = f"New Chef Application - {application_data['fullName']}"

        body_text = f"""
New Chef Application Received!

Application Details:
- Application ID: {application_data['applicationId']}
- Name: {application_data['fullName']}
- Email: {application_data['email']}
- Phone: {application_data['phone']}
- Location: {application_data['location']}
- Experience: {application_data['experience']}
- Specialty: {application_data['specialty']}
- Availability: {application_data['availability']}
- Submitted: {application_data['submittedAt']}
- Background Check Consent: {application_data['backgroundCheck']}
- Newsletter Signup: {application_data['newsletterSignup']}

Please review this application in the admin panel.
"""

        admin_emails = ['admin@maharajachef.com']  # change if needed

        ses.send_email(
            Source=FROM_EMAIL,
            Destination={'ToAddresses': admin_emails},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Text': {'Data': body_text, 'Charset': 'UTF-8'}
                }
            }
        )

        logger.info(f"Admin notification sent for application {application_data['applicationId']}")

    except Exception as e:
        logger.error(f"Failed to send admin notification: {str(e)}")
