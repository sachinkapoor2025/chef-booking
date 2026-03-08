import json
import boto3
import os
import uuid
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# Environment variables
SUBMISSIONS_TABLE = os.environ['SUBMISSIONS_TABLE']
S3_BUCKET = os.environ['S3_BUCKET']

def lambda_handler(event, context):
    """
    Lambda function to handle general form submissions
    """
    try:
        # Parse the incoming request
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
            
        # Validate required fields based on form type
        form_type = body.get('formType', 'general')
        
        if form_type == 'general':
            required_fields = ['name', 'email', 'message']
        elif form_type == 'book-chef':
            required_fields = ['name', 'email', 'phone', 'event-type', 'event-date', 'location', 'guests']
        elif form_type == 'chef-application':
            required_fields = ['fullName', 'email', 'phone', 'location', 'experience', 'specialty', 'culinaryPhilosophy', 'availability']
        elif form_type == 'blog-submission':
            required_fields = ['fullName', 'email', 'profession', 'blogTitle', 'blogCategory', 'blogContent', 'blogSummary']
        elif form_type == 'catering-submission':
            required_fields = ['name', 'email', 'phone', 'event-type', 'event-date', 'location', 'guests', 'event-time']
        else:
            required_fields = ['name', 'email', 'message']
        
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
        
        # Generate submission ID
        submission_id = f"SUB-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Prepare submission data
        submission_data = {
            'id': submission_id,
            'formType': form_type,
            'data': body,
            'status': 'PENDING',
            'submittedAt': datetime.now().isoformat(),
            'processed': False
        }
        
        # Save to DynamoDB
        table = dynamodb.Table(SUBMISSIONS_TABLE)
        table.put_item(Item=submission_data)
        
        # Save to S3 for backup
        s3_key = f"submissions/{form_type}/{submission_id}.json"
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(submission_data, indent=2),
            ContentType='application/json'
        )
        
        # Send confirmation email (optional)
        send_confirmation_email(submission_data)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'message': 'Form submission received successfully!',
                'submissionId': submission_id,
                'formType': form_type,
                'status': 'PENDING'
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing form submission: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Failed to process form submission',
                'details': str(e)
            })
        }

def send_confirmation_email(submission_data):
    """
    Send confirmation email for form submissions
    """
    try:
        ses = boto3.client('ses')
        
        form_type = submission_data['formType']
        data = submission_data['data']
        
        # Email content based on form type
        if form_type == 'general':
            subject = f"Form Submission Received - {submission_data['id']}"
            name = data.get('name', 'Customer')
            body_text = f"""
            Dear {name},

            Thank you for contacting us!

            Your form submission has been received. Here are the details:

            - Submission ID: {submission_data['id']}
            - Form Type: General Contact
            - Name: {data.get('name', 'N/A')}
            - Email: {data.get('email', 'N/A')}
            - Submitted: {submission_data['submittedAt']}

            We will review your submission and get back to you shortly.

            Best regards,
            Maharaja Chef Services Team
            """
            
        elif form_type == 'book-chef':
            subject = f"Booking Request Received - {submission_data['id']}"
            name = data.get('name', 'Customer')
            body_text = f"""
            Dear {name},

            Thank you for booking with Maharaja Chef Services!

            Your booking request has been received. Here are the details:

            - Booking ID: {submission_data['id']}
            - Event Type: {data.get('event-type', 'N/A')}
            - Event Date: {data.get('event-date', 'N/A')}
            - Event Time: {data.get('event-time', 'N/A')}
            - Location: {data.get('location', 'N/A')}
            - Number of Guests: {data.get('guests', 'N/A')}
            - Status: {submission_data['status']}

            We will contact you shortly to confirm your booking and discuss menu options.

            Best regards,
            Maharaja Chef Services Team
            """
            
        elif form_type == 'chef-application':
            subject = f"Chef Application Received - {submission_data['id']}"
            name = data.get('fullName', 'Applicant')
            body_text = f"""
            Dear {name},

            Thank you for applying to join Maharaja Chef Services!

            Your application has been successfully received. Here are the details:

            - Application ID: {submission_data['id']}
            - Name: {data.get('fullName', 'N/A')}
            - Email: {data.get('email', 'N/A')}
            - Phone: {data.get('phone', 'N/A')}
            - Experience: {data.get('experience', 'N/A')}
            - Specialty: {data.get('specialty', 'N/A')}
            - Submitted: {submission_data['submittedAt']}

            Our team will review your application within 3-5 business days.
            You will receive an email notification regarding our decision.

            Best regards,
            Maharaja Chef Services Team
            """
            
        elif form_type == 'blog-submission':
            subject = f"Blog Submission Received - {submission_data['id']}"
            name = data.get('fullName', 'Author')
            body_text = f"""
            Dear {name},

            Thank you for submitting your blog post to Maharaja Chef Services!

            Your submission has been received. Here are the details:

            - Submission ID: {submission_data['id']}
            - Author: {data.get('fullName', 'N/A')}
            - Email: {data.get('email', 'N/A')}
            - Blog Title: {data.get('blogTitle', 'N/A')}
            - Category: {data.get('blogCategory', 'N/A')}
            - Submitted: {submission_data['submittedAt']}

            Our editorial team will review your submission within 3-5 business days.
            You will receive an email notification regarding our decision.

            Best regards,
            Maharaja Chef Services Editorial Team
            """
            
        elif form_type == 'catering-submission':
            subject = f"Catering Request Received - {submission_data['id']}"
            name = data.get('name', 'Customer')
            body_text = f"""
            Dear {name},

            Thank you for your catering inquiry with Maharaja Chef Services!

            Your catering request has been received. Here are the details:

            - Request ID: {submission_data['id']}
            - Event Type: {data.get('event-type', 'N/A')}
            - Event Date: {data.get('event-date', 'N/A')}
            - Event Time: {data.get('event-time', 'N/A')}
            - Location: {data.get('location', 'N/A')}
            - Number of Guests: {data.get('guests', 'N/A')}
            - Status: {submission_data['status']}

            We will contact you shortly to discuss your catering needs and provide a quote.

            Best regards,
            Maharaja Chef Services Team
            """
        else:
            subject = f"Submission Received - {submission_data['id']}"
            name = data.get('name', 'Customer')
            body_text = f"""
            Dear {name},

            Thank you for your submission!

            Your form submission has been received. Here are the details:

            - Submission ID: {submission_data['id']}
            - Form Type: {form_type}
            - Submitted: {submission_data['submittedAt']}

            We will review your submission and get back to you shortly.

            Best regards,
            Maharaja Chef Services Team
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
                    }
                }
            }
        )
        
        logger.info(f"Confirmation email sent to {data.get('email', 'info@maharajachef.com')}")
        
    except Exception as e:
        logger.error(f"Failed to send confirmation email: {str(e)}")
        # Don't fail the submission if email fails