import json
import boto3
import os
import uuid
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS services
dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')

# Environment variables
USERS_TABLE = os.environ.get('USERS_TABLE', 'Users')
DIET_CHARTS_TABLE = os.environ.get('DIET_CHARTS_TABLE', 'DietCharts')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@maharajachef.com')

def lambda_handler(event, context):
    """
    Lambda function to handle authentication requests
    Supports: signup, signin, forgot-password, verify-email, download-diet-chart
    """
    try:
        # Parse the request body
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
        
        action = body.get('action')
        
        if action == 'signup':
            return handle_signup(body)
        elif action == 'signin':
            return handle_signin(body)
        elif action == 'forgot-password':
            return handle_forgot_password(body)
        elif action == 'verify-email':
            return handle_verify_email(body)
        elif action == 'download-diet-chart':
            return handle_download_diet_chart(body)
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({
                    'error': 'Invalid action'
                })
            }
        
    except Exception as e:
        logger.error(f"Error in auth handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

def handle_signup(body):
    """
    Handle user signup
    """
    email = body.get('email')
    password = body.get('password')
    name = body.get('name')
    
    if not email or not password or not name:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Missing required fields'
            })
        }
    
    # Hash password
    password_hash = hash_password(password)
    
    # Generate verification token
    verification_token = str(uuid.uuid4())
    
    # Save user to DynamoDB
    table = dynamodb.Table(USERS_TABLE)
    
    try:
        table.put_item(
            Item={
                'email': email,
                'password_hash': password_hash,
                'name': name,
                'is_verified': False,
                'verification_token': verification_token,
                'created_at': datetime.utcnow().isoformat(),
                'last_login': None
            },
            ConditionExpression='attribute_not_exists(email)'
        )
        
        # Send verification email
        send_verification_email(email, name, verification_token)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'message': 'User registered successfully. Please check your email for verification.',
                'email': email
            })
        }
        
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        return {
            'statusCode': 409,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'error': 'User already exists with this email'
            })
        }

def handle_signin(body):
    """
    Handle user signin
    """
    email = body.get('email')
    password = body.get('password')
    
    if not email or not password:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Missing email or password'
            })
        }
    
    table = dynamodb.Table(USERS_TABLE)
    response = table.get_item(Key={'email': email})
    
    if 'Item' not in response:
        return {
            'statusCode': 401,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Invalid email or password'
            })
        }
    
    user = response['Item']
    
    if not user.get('is_verified', False):
        return {
            'statusCode': 403,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Please verify your email before signing in'
            })
        }
    
    if not verify_password(password, user['password_hash']):
        return {
            'statusCode': 401,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Invalid email or password'
            })
        }
    
    # Generate JWT token
    token = generate_jwt_token(email, user['name'])
    
    # Update last login
    table.update_item(
        Key={'email': email},
        UpdateExpression='SET last_login = :login_time',
        ExpressionAttributeValues={
            ':login_time': datetime.utcnow().isoformat()
        }
    )
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        },
        'body': json.dumps({
            'message': 'Signin successful',
            'token': token,
            'user': {
                'email': email,
                'name': user['name']
            }
        })
    }

def handle_forgot_password(body):
    """
    Handle forgot password request
    """
    email = body.get('email')
    
    if not email:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Email is required'
            })
        }
    
    table = dynamodb.Table(USERS_TABLE)
    response = table.get_item(Key={'email': email})
    
    if 'Item' not in response:
        return {
            'statusCode': 404,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'error': 'User not found with this email'
            })
        }
    
    # Generate reset token
    reset_token = str(uuid.uuid4())
    
    # Update user with reset token
    table.update_item(
        Key={'email': email},
        UpdateExpression='SET reset_token = :token, reset_token_expires = :expires',
        ExpressionAttributeValues={
            ':token': reset_token,
            ':expires': (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
    )
    
    # Send reset email
    send_reset_email(email, reset_token)
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        },
        'body': json.dumps({
            'message': 'Password reset link sent to your email'
        })
    }

def handle_verify_email(body):
    """
    Handle email verification
    """
    email = body.get('email')
    token = body.get('token')
    
    if not email or not token:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Email and token are required'
            })
        }
    
    table = dynamodb.Table(USERS_TABLE)
    response = table.get_item(Key={'email': email})
    
    if 'Item' not in response:
        return {
            'statusCode': 404,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'error': 'User not found'
            })
        }
    
    user = response['Item']
    
    if user.get('verification_token') != token:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Invalid verification token'
            })
        }
    
    # Mark user as verified
    table.update_item(
        Key={'email': email},
        UpdateExpression='SET is_verified = :verified, verification_token = :null',
        ExpressionAttributeValues={
            ':verified': True,
            ':null': None
        }
    )
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        },
        'body': json.dumps({
            'message': 'Email verified successfully'
        })
    }

def handle_download_diet_chart(body):
    """
    Handle diet chart download with authentication
    """
    chart_id = body.get('chart_id')
    token = body.get('token')
    
    if not chart_id or not token:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Chart ID and token are required'
            })
        }
    
    # Verify JWT token
    try:
        user_data = verify_jwt_token(token)
        email = user_data['email']
    except Exception as e:
        return {
            'statusCode': 401,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Invalid or expired token'
            })
        }
    
    # Check if user owns this diet chart
    table = dynamodb.Table(DIET_CHARTS_TABLE)
    response = table.get_item(Key={'chart_id': chart_id})
    
    if 'Item' not in response:
        return {
            'statusCode': 404,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Diet chart not found'
            })
        }
    
    diet_chart = response['Item']
    
    if diet_chart['email'] != email:
        return {
            'statusCode': 403,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Access denied'
            })
        }
    
    # Check if chart is completed
    if diet_chart.get('status') != 'completed':
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Diet chart is still being generated'
            })
        }
    
    # Check if user needs to pay for premium service
    if diet_chart.get('is_premium', False):
        # Check if user has already paid
        if not diet_chart.get('is_paid', False):
            return {
                'statusCode': 402,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({
                    'error': 'Payment required',
                    'message': 'This is a premium diet chart. Please pay $5.99 to download.',
                    'payment_url': f"https://maharajachef.com/payment?chart_id={chart_id}"
                })
            }
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        },
        'body': json.dumps({
            'message': 'Download authorized',
            'pdf_url': diet_chart.get('pdf_url'),
            'chart_id': chart_id
        })
    }

# Helper functions

def hash_password(password):
    """
    Hash password using SHA-256
    """
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """
    Verify password against hash
    """
    return hash_password(password) == password_hash

def generate_jwt_token(email, name):
    """
    Generate a simple JWT-like token
    In production, use a proper JWT library
    """
    import time
    
    payload = {
        'email': email,
        'name': name,
        'exp': int(time.time()) + 3600,  # 1 hour expiry
        'iat': int(time.time())
    }
    
    # Simple encoding (not secure for production)
    token_data = f"{json.dumps(payload)}"
    signature = hashlib.sha256(token_data.encode()).hexdigest()
    
    return f"{base64.urlsafe_b64encode(token_data.encode()).decode()}.{signature}"

def verify_jwt_token(token):
    """
    Verify JWT token
    """
    import time
    
    try:
        parts = token.split('.')
        if len(parts) != 2:
            raise Exception("Invalid token format")
        
        payload_data = base64.urlsafe_b64decode(parts[0]).decode()
        payload = json.loads(payload_data)
        
        # Check expiration
        if payload['exp'] < int(time.time()):
            raise Exception("Token expired")
        
        return payload
        
    except Exception as e:
        raise Exception(f"Token verification failed: {str(e)}")

def send_verification_email(email, name, token):
    """
    Send email verification link
    """
    try:
        subject = "Verify Your Email Address"
        
        verification_link = f"https://maharajachef.com/verify-email?email={email}&token={token}"
        
        body_text = f"""
Hello {name},

Thank you for signing up with Maharaja Chef Services!

Please verify your email address by clicking the link below:

{verification_link}

This link will expire in 24 hours.

If you didn't create an account with us, please ignore this email.

Best regards,
Maharaja Chef Services Team
        """
        
        body_html = f"""
        <html>
        <head></head>
        <body>
            <h2>Welcome to Maharaja Chef Services, {name}!</h2>
            <p>Thank you for signing up with us!</p>
            
            <p>Please verify your email address by clicking the button below:</p>
            
            <p><a href="{verification_link}" style="background-color: #1e3a8a; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Verify Email Address</a></p>
            
            <p><em>This link will expire in 24 hours.</em></p>
            
            <p>If you didn't create an account with us, please ignore this email.</p>
            
            <p>Best regards,<br>
            Maharaja Chef Services Team</p>
        </body>
        </html>
        """
        
        ses.send_email(
            Source=FROM_EMAIL,
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Text': {'Data': body_text},
                    'Html': {'Data': body_html}
                }
            }
        )
        
        logger.info(f"Verification email sent to {email}")
        
    except Exception as e:
        logger.error(f"Error sending verification email: {e}")

def send_reset_email(email, token):
    """
    Send password reset email
    """
    try:
        subject = "Reset Your Password"
        
        reset_link = f"https://maharajachef.com/reset-password?email={email}&token={token}"
        
        body_text = f"""
Hello,

We received a request to reset your password for your Maharaja Chef Services account.

Please click the link below to reset your password:

{reset_link}

This link will expire in 1 hour.

If you didn't request this password reset, please ignore this email.

Best regards,
Maharaja Chef Services Team
        """
        
        body_html = f"""
        <html>
        <head></head>
        <body>
            <h2>Password Reset Request</h2>
            <p>We received a request to reset your password.</p>
            
            <p>Please click the button below to reset your password:</p>
            
            <p><a href="{reset_link}" style="background-color: #1e3a8a; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a></p>
            
            <p><em>This link will expire in 1 hour.</em></p>
            
            <p>If you didn't request this password reset, please ignore this email.</p>
            
            <p>Best regards,<br>
            Maharaja Chef Services Team</p>
        </body>
        </html>
        """
        
        ses.send_email(
            Source=FROM_EMAIL,
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Text': {'Data': body_text},
                    'Html': {'Data': body_html}
                }
            }
        )
        
        logger.info(f"Reset email sent to {email}")
        
    except Exception as e:
        logger.error(f"Error sending reset email: {e}")