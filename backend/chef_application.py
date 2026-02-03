import json
import boto3
import os
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS services
s3_client = boto3.client('s3')
ses_client = boto3.client('ses')
dynamodb = boto3.resource('dynamodb')

# Environment variables
BUCKET_NAME = os.environ.get('CHEF_APPLICATION_BUCKET')
TABLE_NAME = os.environ.get('CHEF_APPLICATION_TABLE')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@maharajachef.com')

def lambda_handler(event, context):
    """
    Lambda function to handle chef application form submissions
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Parse the form data
        form_data = parse_form_data(event)
        
        # Validate required fields
        validate_form_data(form_data)
        
        # Generate application ID
        application_id = generate_application_id()
        form_data['applicationId'] = application_id
        form_data['submittedAt'] = datetime.utcnow().isoformat()
        form_data['status'] = 'pending'
        
        # Save application to DynamoDB
        save_application_to_dynamodb(form_data)
        
        # Upload files to S3
        if 'resume' in form_data:
            upload_file_to_s3(form_data['resume'], f"applications/{application_id}/resume.pdf")
        
        if 'culinaryPhotos' in form_data:
            for i, photo in enumerate(form_data['culinaryPhotos']):
                upload_file_to_s3(photo, f"applications/{application_id}/photos/photo_{i}.jpg")
        
        # Send confirmation email to applicant
        send_confirmation_email(form_data)
        
        # Send notification email to admin
        send_admin_notification(form_data)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Application submitted successfully',
                'applicationId': application_id
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing application: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Failed to process application',
                'message': str(e)
            })
        }

def parse_form_data(event):
    """
    Parse form data from API Gateway event
    """
    form_data = {}
    
    # Handle different event formats
    if 'body' in event:
        if event.get('isBase64Encoded', False):
            # Handle base64 encoded body
            import base64
            body = base64.b64decode(event['body'])
        else:
            body = event['body'].encode('utf-8')
        
        # Parse multipart form data
        import email
        from email.message import EmailMessage
        
        # Create a message from the raw body
        message = EmailMessage()
        message.set_payload(body)
        
        # Extract form fields
        for part in message.iter_parts():
            if part.get_content_type() == 'text/plain':
                name = part.get('Content-Disposition', '').split('name=')[1].strip('"')
                form_data[name] = part.get_payload(decode=True).decode('utf-8')
            elif part.get_content_type().startswith('application/') or part.get_content_type().startswith('image/'):
                name = part.get('Content-Disposition', '').split('name=')[1].strip('"')
                filename = part.get_filename()
                content = part.get_payload(decode=True)
                
                if name == 'resume':
                    form_data['resume'] = {
                        'filename': filename,
                        'content': content,
                        'content_type': part.get_content_type()
                    }
                elif name == 'culinaryPhotos':
                    if 'culinaryPhotos' not in form_data:
                        form_data['culinaryPhotos'] = []
                    form_data['culinaryPhotos'].append({
                        'filename': filename,
                        'content': content,
                        'content_type': part.get_content_type()
                    })
    
    return form_data

def validate_form_data(form_data):
    """
    Validate required form fields
    """
    required_fields = [
        'fullName', 'email', 'phone', 'location', 
        'experience', 'specialty', 'culinaryPhilosophy', 
        'availability', 'termsAgreement'
    ]
    
    for field in required_fields:
        if field not in form_data or not form_data[field]:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate email format
    import re
    if not re.match(r"[^@]+@[^@]+\.[^@]+", form_data['email']):
        raise ValueError("Invalid email format")
    
    # Validate phone format
    if not re.match(r"^\+?[\d\s\-\(\)]{10,}$", form_data['phone']):
        raise ValueError("Invalid phone format")

def generate_application_id():
    """
    Generate unique application ID
    """
    import uuid
    return f"APP-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

def save_application_to_dynamodb(form_data):
    """
    Save application data to DynamoDB
    """
    table = dynamodb.Table(TABLE_NAME)
    
    # Prepare item for DynamoDB
    item = {
        'applicationId': form_data['applicationId'],
        'fullName': form_data['fullName'],
        'email': form_data['email'],
        'phone': form_data['phone'],
        'location': form_data['location'],
        'experience': form_data['experience'],
        'specialty': form_data['specialty'],
        'certifications': form_data.get('certifications', ''),
        'website': form_data.get('website', ''),
        'culinaryPhilosophy': form_data['culinaryPhilosophy'],
        'availability': form_data['availability'],
        'backgroundCheckConsent': form_data.get('backgroundCheck', False),
        'newsletterSignup': form_data.get('newsletterSignup', False),
        'submittedAt': form_data['submittedAt'],
        'status': form_data['status'],
        'hasResume': 'resume' in form_data,
        'photoCount': len(form_data.get('culinaryPhotos', []))
    }
    
    table.put_item(Item=item)
    logger.info(f"Saved application {form_data['applicationId']} to DynamoDB")

def upload_file_to_s3(file_data, s3_key):
    """
    Upload file to S3 bucket
    """
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=file_data['content'],
        ContentType=file_data['content_type'],
        ServerSideEncryption='AES256'
    )
    logger.info(f"Uploaded file to S3: {s3_key}")

def send_confirmation_email(form_data):
    """
    Send confirmation email to the applicant
    """
    subject = "Chef Application Received - Maharaja Chef Services"
    
    body_text = f"""
    Dear {form_data['fullName']},

    Thank you for your interest in joining Maharaja Chef Services! We have successfully received your application.

    Application Details:
    - Application ID: {form_data['applicationId']}
    - Submitted: {form_data['submittedAt']}
    - Culinary Specialty: {form_data['specialty']}
    - Experience: {form_data['experience']}

    Our team will review your application within 3-5 business days. We will contact you via email to schedule an interview if your application meets our requirements.

    In the meantime, you can:
    - Visit our Chef Guidelines: https://maharajachef.com/chef-guidelines.html
    - Learn about our process: https://maharajachef.com/become-a-chef.html
    - Contact us with questions: info@maharajachef.com

    Thank you for considering Maharaja Chef Services for your culinary career.

    Best regards,
    The Maharaja Chef Services Team
    """

    body_html = f"""
    <html>
    <head></head>
    <body>
        <h2>Application Received Successfully</h2>
        <p>Dear <strong>{form_data['fullName']}</strong>,</p>
        
        <p>Thank you for your interest in joining <strong>Maharaja Chef Services</strong>! We have successfully received your application.</p>
        
        <h3>Application Details:</h3>
        <ul>
            <li><strong>Application ID:</strong> {form_data['applicationId']}</li>
            <li><strong>Submitted:</strong> {form_data['submittedAt']}</li>
            <li><strong>Culinary Specialty:</strong> {form_data['specialty']}</li>
            <li><strong>Experience:</strong> {form_data['experience']}</li>
        </ul>
        
        <p><strong>Next Steps:</strong></p>
        <p>Our team will review your application within <strong>3-5 business days</strong>. We will contact you via email to schedule an interview if your application meets our requirements.</p>
        
        <p><strong>In the meantime, you can:</strong></p>
        <ul>
            <li>Visit our <a href="https://maharajachef.com/chef-guidelines.html">Chef Guidelines</a></li>
            <li>Learn about our <a href="https://maharajachef.com/become-a-chef.html">process</a></li>
            <li>Contact us with questions: <a href="mailto:info@maharajachef.com">info@maharajachef.com</a></li>
        </ul>
        
        <p>Thank you for considering Maharaja Chef Services for your culinary career.</p>
        
        <p>Best regards,<br>
        <strong>The Maharaja Chef Services Team</strong></p>
    </body>
    </html>
    """

    ses_client.send_email(
        Source=FROM_EMAIL,
        Destination={'ToAddresses': [form_data['email']]},
        Message={
            'Subject': {'Data': subject},
            'Body': {
                'Text': {'Data': body_text},
                'Html': {'Data': body_html}
            }
        }
    )
    logger.info(f"Sent confirmation email to {form_data['email']}")

def send_admin_notification(form_data):
    """
    Send notification email to admin team
    """
    subject = f"New Chef Application: {form_data['fullName']} - {form_data['specialty']}"
    
    body_text = f"""
    New Chef Application Received

    Application Details:
    - Application ID: {form_data['applicationId']}
    - Full Name: {form_data['fullName']}
    - Email: {form_data['email']}
    - Phone: {form_data['phone']}
    - Location: {form_data['location']}
    - Culinary Specialty: {form_data['specialty']}
    - Experience: {form_data['experience']}
    - Availability: {form_data['availability']}
    - Submitted: {form_data['submittedAt']}
    
    Files Uploaded:
    - Resume: {'Yes' if 'resume' in form_data else 'No'}
    - Photos: {len(form_data.get('culinaryPhotos', []))} files
    
    Please review this application in the admin panel.
    """

    ses_client.send_email(
        Source=FROM_EMAIL,
        Destination={'ToAddresses': ['admin@maharajachef.com']},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': body_text}}
        }
    )
    logger.info(f"Sent admin notification for application {form_data['applicationId']}")

# Health check endpoint
def health_check(event, context):
    """
    Health check endpoint for the Lambda function
    """
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'chef-application'
        })
    }