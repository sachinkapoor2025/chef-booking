import json
import boto3
import os
from datetime import datetime
import uuid

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# Environment variables
SUBMISSIONS_TABLE = os.environ['SUBMISSIONS_TABLE']
BLOGS_BUCKET = os.environ['BLOGS_BUCKET']

def lambda_handler(event, context):
    """
    Handle blog submission form submissions
    """
    try:
        # Parse the request body
        body = json.loads(event['body'])
        
        # Validate required fields
        required_fields = ['title', 'author', 'content', 'email']
        for field in required_fields:
            if field not in body or not body[field].strip():
                return {
                    'statusCode': 400,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                        'Access-Control-Allow-Methods': 'POST,OPTIONS'
                    },
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
            'title': body['title'].strip(),
            'author': body['author'].strip(),
            'email': body['email'].strip(),
            'content': body['content'].strip(),
            'status': 'pending',  # pending, approved, rejected
            'submittedAt': timestamp,
            'approvedAt': None,
            'rejectedAt': None,
            'approvedBy': None,
            'rejectedBy': None,
            'rejectionReason': None
        }
        
        # Add optional fields if provided
        if 'category' in body and body['category'].strip():
            submission_data['category'] = body['category'].strip()
        
        if 'tags' in body and isinstance(body['tags'], list):
            submission_data['tags'] = body['tags']
        
        if 'featuredImage' in body and body['featuredImage'].strip():
            submission_data['featuredImage'] = body['featuredImage'].strip()
        
        # Save to DynamoDB
        table = dynamodb.Table(SUBMISSIONS_TABLE)
        table.put_item(Item=submission_data)
        
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
                'message': 'Blog submission received successfully. It will be reviewed and published if approved.',
                'submissionId': submission_id
            })
        }
        
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
                'message': 'Invalid JSON in request body'
            })
        }
    
    except Exception as e:
        print(f"Error processing blog submission: {str(e)}")
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

def get_pending_blogs(event, context):
    """
    Get all pending blog submissions for admin review
    """
    try:
        table = dynamodb.Table(SUBMISSIONS_TABLE)
        
        # Query for pending blog submissions
        response = table.query(
            IndexName='formType-index',
            KeyConditionExpression='formType = :form_type',
            ExpressionAttributeValues={
                ':form_type': 'blog-submission'
            }
        )
        
        pending_blogs = [item for item in response['Items'] if item.get('status') == 'pending']
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,OPTIONS'
            },
            'body': json.dumps({
                'success': True,
                'blogs': pending_blogs
            })
        }
        
    except Exception as e:
        print(f"Error fetching pending blogs: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,OPTIONS'
            },
            'body': json.dumps({
                'success': False,
                'message': 'Internal server error'
            })
        }

def approve_blog(event, context):
    """
    Approve a blog submission and create the blog post
    """
    try:
        # Parse path parameters
        submission_id = event['pathParameters']['submissionId']
        
        # Parse request body
        body = json.loads(event['body'])
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
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'PUT,OPTIONS'
            },
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
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'PUT,OPTIONS'
            },
            'body': json.dumps({
                'success': False,
                'message': 'Internal server error'
            })
        }

def reject_blog(event, context):
    """
    Reject a blog submission
    """
    try:
        # Parse path parameters
        submission_id = event['pathParameters']['submissionId']
        
        # Parse request body
        body = json.loads(event['body'])
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
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'PUT,OPTIONS'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Blog rejected successfully'
            })
        }
        
    except Exception as e:
        print(f"Error rejecting blog: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'PUT,OPTIONS'
            },
            'body': json.dumps({
                'success': False,
                'message': 'Internal server error'
            })
        }