import json
import boto3
import os
import uuid
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

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
    try:
        # Parse the incoming request
        if 'body' in event:
            # Handle form data
            body = event['body']
            is_base64 = event.get('isBase64Encoded', False)
            
            if is_base64:
                import base64
                body = base64.b64decode(body).decode('utf-8')
            
            # Parse form data
            application_data = parse_form_data(body)
        else:
            # Handle JSON data
            application_data = event
            
        # Validate required fields
        required_fields = ['fullName', 'email', 'phone', 'location', 'experience', 'specialty', 'culinaryPhilosophy', 'availability']
        for field in required_fields:
            if field not in application_data:
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
            'fullName': application_data['fullName'],
            'email': application_data['email'],
            'phone': application_data['phone'],
            'location': application_data['location'],
            'experience': application_data['experience'],
            'specialty': application_data['specialty'],
            'certifications': application_data.get('certifications', ''),
            'website': application_data.get('website', ''),
            'culinaryPhilosophy': application_data['culinaryPhilosophy'],
            'availability': application_data['availability'],
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
        
        # Send confirmation email
        send_confirmation_email(chef_application)
        
        # Send notification to admin
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
    import urllib.parse
    
    # Parse the form data
    parsed_data = {}
    pairs = body.split('&')
    
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            key = urllib.parse.unquote_plus(key)
            value = urllib.parse.unquote_plus(value)
            parsed_data[key] = value
    
    return parsed_data

def send_confirmation_email(application_data):
    """
    Send confirmation email to the applicant
    """
    try:
        # Email content
        subject = f"Chef Application Received - {application_data['applicationId']}"
        
        body_text = f"""
        Dear {application_data['fullName']},

        Thank you for applying to join Maharaja Chef Services!

        Your application has been successfully received. Here are the details:

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

        Next Steps:
        1. We may contact you for additional information or documentation
        2. If selected, you'll be invited for an interview and skills assessment
        3. Upon approval, you'll need to complete a background check
        4. Finally, you'll create your professional profile on our platform

        Thank you for your interest in joining our team of elite chefs!

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
                .steps {{ background: white; padding: 15px; border-radius: 6px; margin: 15px 0; }}
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
                    
                    <p>Thank you for applying to join Maharaja Chef Services! Your application has been successfully received.</p>
                    
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
                    
                    <div class="steps">
                        <h3>Next Steps:</h3>
                        <ol>
                            <li>We will review your application within 3-5 business days</li>
                            <li>We may contact you for additional information or documentation</li>
                            <li>If selected, you'll be invited for an interview and skills assessment</li>
                            <li>Upon approval, you'll need to complete a background check</li>
                            <li>Finally, you'll create your professional profile on our platform</li>
                        </ol>
                    </div>
                    
                    <p>We appreciate your interest in joining our team of elite chefs. We look forward to reviewing your application!</p>
                    
                    <p>Best regards,<br>
                    <strong>The Maharaja Chef Services Team</strong></p>
                </div>
                
                <div class="footer">
                    <p>For questions, please contact us at info@maharajachef.com</p>
                    <p>&copy; 2024 Maharaja Chef Services. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send email
        response = ses.send_email(
            Source=FROM_EMAIL,
            Destination={
                'ToAddresses': [application_data['email']]
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
        
        logger.info(f"Confirmation email sent to {application_data['email']}")
        
    except Exception as e:
        logger.error(f"Failed to send confirmation email: {str(e)}")
        # Don't fail the application if email fails

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
        
        body_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #1f2937; color: white; padding: 20px; text-align: center; border-radius: 8px; }}
                .content {{ background: #f8fafc; padding: 20px; border-radius: 8px; margin-top: 20px; }}
                .details {{ background: white; padding: 15px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #3b82f6; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>📋 New Chef Application</h2>
                    <p>Application received from {application_data['fullName']}</p>
                </div>
                
                <div class="content">
                    <h3>Application Details:</h3>
                    <div class="details">
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
                            <li><strong>Background Check Consent:</strong> {application_data['backgroundCheck']}</li>
                            <li><strong>Newsletter Signup:</strong> {application_data['newsletterSignup']}</li>
                        </ul>
                    </div>
                    
                    <p>Please review this application in the admin panel and take appropriate action.</p>
                </div>
                
                <div class="footer">
                    <p>This is an automated notification from Maharaja Chef Services</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send email to admin (you can add multiple admin emails here)
        admin_emails = ['admin@maharajachef.com']  # Add your admin emails here
        
        response = ses.send_email(
            Source=FROM_EMAIL,
            Destination={
                'ToAddresses': admin_emails
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
        
        logger.info(f"Admin notification sent for application {application_data['applicationId']}")
        
    except Exception as e:
        logger.error(f"Failed to send admin notification: {str(e)}")
        # Don't fail the application if email fails