import json
import boto3
import os
from datetime import datetime
import uuid
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB, S3, and SES clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
ses = boto3.client('ses')

# Environment variables
SUBMISSIONS_TABLE = os.environ['SUBMISSIONS_TABLE']
BLOGS_BUCKET = os.environ['BLOGS_BUCKET']


# Common CORS Headers
def cors_headers(methods="POST,OPTIONS"):
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': methods
    }


def lambda_handler(event, context):
    """
    Handle blog submission form submissions
    """

    # ✅ Handle OPTIONS Preflight Request (CORS Fix)
    if event.get("httpMethod") == "OPTIONS":
        return {
            'statusCode': 200,
            'headers': cors_headers("POST,OPTIONS"),
            'body': json.dumps({'message': 'CORS preflight success'})
        }

    try:
        # Parse the request body
        if not event.get("body"):
            return {
                'statusCode': 400,
                'headers': cors_headers("POST,OPTIONS"),
                'body': json.dumps({
                    'success': False,
                    'message': 'Request body is missing'
                })
            }

        body = json.loads(event['body'])

        # Validate required fields
        required_fields = ['fullName', 'email', 'blogTitle', 'blogContent', 'blogSummary']
        for field in required_fields:
            if field not in body or not str(body[field]).strip():
                return {
                    'statusCode': 400,
                    'headers': cors_headers("POST,OPTIONS"),
                    'body': json.dumps({
                        'success': False,
                        'message': f'Missing required field: {field}'
                    })
                }

        # Generate unique submission ID
        submission_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        # Prepare submission data
        submission_data = {
            'id': submission_id,
            'formType': 'blog-submission',
            'title': body['blogTitle'].strip(),
            'author': body['fullName'].strip(),
            'email': body['email'].strip(),
            'content': body['blogContent'].strip(),
            'summary': body['blogSummary'].strip(),
            'status': 'pending',  # pending, approved, rejected
            'submittedAt': timestamp,
            'approvedAt': None,
            'rejectedAt': None,
            'approvedBy': None,
            'rejectedBy': None,
            'rejectionReason': None
        }

        # Add optional fields if provided
        if 'category' in body and str(body['category']).strip():
            submission_data['category'] = body['category'].strip()

        if 'tags' in body and isinstance(body['tags'], list):
            submission_data['tags'] = body['tags']

        if 'featuredImage' in body and str(body['featuredImage']).strip():
            submission_data['featuredImage'] = body['featuredImage'].strip()

        # Save to DynamoDB
        table = dynamodb.Table(SUBMISSIONS_TABLE)
        table.put_item(Item=submission_data)

        # Send confirmation email to the author
        send_blog_confirmation_email(submission_data)

        # Return success response
        return {
            'statusCode': 200,
            'headers': cors_headers("POST,OPTIONS"),
            'body': json.dumps({
                'success': True,
                'message': 'Blog submission received successfully. It will be reviewed and published if approved.',
                'submissionId': submission_id
            })
        }

    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': cors_headers("POST,OPTIONS"),
            'body': json.dumps({
                'success': False,
                'message': 'Invalid JSON in request body'
            })
        }

    except Exception as e:
        print(f"Error processing blog submission: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers("POST,OPTIONS"),
            'body': json.dumps({
                'success': False,
                'message': 'Internal server error'
            })
        }


def get_pending_blogs(event, context):
    """
    Get all pending blog submissions for admin review
    """

    # ✅ Handle OPTIONS Preflight Request
    if event.get("httpMethod") == "OPTIONS":
        return {
            'statusCode': 200,
            'headers': cors_headers("GET,OPTIONS"),
            'body': json.dumps({'message': 'CORS preflight success'})
        }

    try:
        table = dynamodb.Table(SUBMISSIONS_TABLE)

        # Query using GSI formType-index
        response = table.query(
            IndexName='formType-index',
            KeyConditionExpression=Key('formType').eq('blog-submission')
        )

        pending_blogs = [item for item in response.get('Items', []) if item.get('status') == 'pending']

        return {
            'statusCode': 200,
            'headers': cors_headers("GET,OPTIONS"),
            'body': json.dumps({
                'success': True,
                'blogs': pending_blogs
            })
        }

    except Exception as e:
        print(f"Error fetching pending blogs: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers("GET,OPTIONS"),
            'body': json.dumps({
                'success': False,
                'message': 'Internal server error'
            })
        }


def approve_blog(event, context):
    """
    Approve a blog submission and create the blog post
    """

    # ✅ Handle OPTIONS Preflight Request
    if event.get("httpMethod") == "OPTIONS":
        return {
            'statusCode': 200,
            'headers': cors_headers("PUT,OPTIONS"),
            'body': json.dumps({'message': 'CORS preflight success'})
        }

    try:
        # Parse path parameters
        submission_id = event['pathParameters']['submissionId']

        # Parse request body
        body = json.loads(event.get('body', '{}'))
        approved_by = body.get('approvedBy', 'Admin')

        table = dynamodb.Table(SUBMISSIONS_TABLE)

        # Update submission status
        response = table.update_item(
            Key={
                'id': submission_id,
                'formType': 'blog-submission'
            },
            UpdateExpression='SET #status = :approved, approvedAt = :timestamp, approvedBy = :approved_by',
            ExpressionAttributeNames={
                '#status': 'status'
            },
            ExpressionAttributeValues={
                ':approved': 'approved',
                ':timestamp': datetime.utcnow().isoformat(),
                ':approved_by': approved_by
            },
            ReturnValues='ALL_NEW'
        )

        # Get the approved blog data
        blog_data = response['Attributes']

        # Create blog post filename
        blog_filename = f"{submission_id}.json"

        # Upload to S3
        s3.put_object(
            Bucket=BLOGS_BUCKET,
            Key=f"approved-blogs/{blog_filename}",
            Body=json.dumps(blog_data, indent=2),
            ContentType='application/json'
        )

        return {
            'statusCode': 200,
            'headers': cors_headers("PUT,OPTIONS"),
            'body': json.dumps({
                'success': True,
                'message': 'Blog approved successfully',
                'blogId': submission_id
            })
        }

    except Exception as e:
        print(f"Error approving blog: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers("PUT,OPTIONS"),
            'body': json.dumps({
                'success': False,
                'message': 'Internal server error'
            })
        }


def reject_blog(event, context):
    """
    Reject a blog submission
    """

    # ✅ Handle OPTIONS Preflight Request
    if event.get("httpMethod") == "OPTIONS":
        return {
            'statusCode': 200,
            'headers': cors_headers("PUT,OPTIONS"),
            'body': json.dumps({'message': 'CORS preflight success'})
        }

    try:
        # Parse path parameters
        submission_id = event['pathParameters']['submissionId']

        # Parse request body
        body = json.loads(event.get('body', '{}'))
        rejected_by = body.get('rejectedBy', 'Admin')
        rejection_reason = body.get('rejectionReason', 'Not specified')

        table = dynamodb.Table(SUBMISSIONS_TABLE)

        # Update submission status
        table.update_item(
            Key={
                'id': submission_id,
                'formType': 'blog-submission'
            },
            UpdateExpression='SET #status = :rejected, rejectedAt = :timestamp, rejectedBy = :rejected_by, rejectionReason = :reason',
            ExpressionAttributeNames={
                '#status': 'status'
            },
            ExpressionAttributeValues={
                ':rejected': 'rejected',
                ':timestamp': datetime.utcnow().isoformat(),
                ':rejected_by': rejected_by,
                ':reason': rejection_reason
            }
        )

        return {
            'statusCode': 200,
            'headers': cors_headers("PUT,OPTIONS"),
            'body': json.dumps({
                'success': True,
                'message': 'Blog rejected successfully'
            })
        }

    except Exception as e:
        print(f"Error rejecting blog: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers("PUT,OPTIONS"),
            'body': json.dumps({
                'success': False,
                'message': 'Internal server error'
            })
        }


def send_blog_confirmation_email(submission_data):
    """
    Send confirmation email to the blog author
    """
    try:
        # Email content
        subject = f"Blog Submission Confirmation - {submission_data['id']}"
        
        # Format submission details
        category = submission_data.get('category', 'Not specified')
        tags = ', '.join(submission_data.get('tags', [])) if submission_data.get('tags') else 'Not specified'
        featured_image = submission_data.get('featuredImage', 'Not provided')
        
        body_text = f"""
        Dear {submission_data['author']},

        Thank you for submitting your blog post to Maharaja Chef Services!

        Your submission details:
        - Submission ID: {submission_data['id']}
        - Blog Title: {submission_data['title']}
        - Author: {submission_data['author']}
        - Category: {category}
        - Tags: {tags}
        - Featured Image: {featured_image}
        - Submission Date: {submission_data['submittedAt']}
        - Status: {submission_data['status']}

        We have received your blog post and it is currently under review. Our editorial team will review your submission within 3-5 business days and you will receive an email notification regarding our decision.

        If your blog post is approved, it will be published on our website and shared with our community of food enthusiasts.

        Thank you for contributing to our blog!

        Best regards,
        Maharaja Chef Services Editorial Team
        """

        body_html = f"""
        <html>
        <head></head>
        <body>
            <h2>Blog Submission Confirmation</h2>
            <p>Dear {submission_data['author']},</p>
            <p>Thank you for submitting your blog post to Maharaja Chef Services!</p>
            
            <h3>Your submission details:</h3>
            <ul>
                <li><strong>Submission ID:</strong> {submission_data['id']}</li>
                <li><strong>Blog Title:</strong> {submission_data['title']}</li>
                <li><strong>Author:</strong> {submission_data['author']}</li>
                <li><strong>Category:</strong> {category}</li>
                <li><strong>Tags:</strong> {tags}</li>
                <li><strong>Featured Image:</strong> {featured_image}</li>
                <li><strong>Submission Date:</strong> {submission_data['submittedAt']}</li>
                <li><strong>Status:</strong> {submission_data['status']}</li>
            </ul>
            
            <p>We have received your blog post and it is currently under review. Our editorial team will review your submission within 3-5 business days and you will receive an email notification regarding our decision.</p>
            
            <p>If your blog post is approved, it will be published on our website and shared with our community of food enthusiasts.</p>
            
            <p>Thank you for contributing to our blog!</p>
            
            <p>Best regards,<br>
            Maharaja Chef Services Editorial Team</p>
        </body>
        </html>
        """

        # Send email
        response = ses.send_email(
            Source='info@maharajachef.com',  # Replace with your verified email
            Destination={
                'ToAddresses': [submission_data['email']]
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

        print(f"Blog confirmation email sent to {submission_data['email']}")

    except Exception as e:
        print(f"Failed to send blog confirmation email: {str(e)}")
        # Don't fail the blog submission if email fails
