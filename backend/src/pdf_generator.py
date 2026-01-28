import json
import boto3
import os
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS services
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Environment variables
DIET_CHARTS_TABLE = os.environ.get('DIET_CHARTS_TABLE', 'DietCharts')
S3_BUCKET = os.environ.get('PDF_BUCKET', 'maharaja-chef-diet-charts')

def lambda_handler(event, context):
    """
    Lambda function to generate PDF from diet chart data
    """
    try:
        # Parse the request body
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
        
        chart_id = body.get('chart_id')
        diet_chart_content = body.get('diet_chart_content')
        user_name = body.get('user_name')
        email = body.get('email')
        
        if not chart_id or not diet_chart_content:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({
                    'error': 'Missing chart_id or diet_chart_content'
                })
            }
        
        # Generate PDF content
        pdf_content = generate_pdf_content(diet_chart_content, user_name, email)
        
        # Upload PDF to S3
        pdf_key = f"diet-charts/{chart_id}.pdf"
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=pdf_key,
            Body=pdf_content,
            ContentType='application/pdf',
            ACL='private'
        )
        
        # Generate presigned URL
        pdf_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': pdf_key},
            ExpiresIn=3600  # 1 hour
        )
        
        # Update DynamoDB with PDF URL
        table = dynamodb.Table(DIET_CHARTS_TABLE)
        table.update_item(
            Key={'chart_id': chart_id},
            UpdateExpression='SET pdf_url = :pdf_url, status = :status, pdf_generated_at = :timestamp',
            ExpressionAttributeValues={
                ':pdf_url': pdf_url,
                ':status': 'completed',
                ':timestamp': datetime.utcnow().isoformat()
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
                'message': 'PDF generated successfully',
                'pdf_url': pdf_url,
                'chart_id': chart_id
            })
        }
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
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

def generate_pdf_content(diet_chart_content, user_name, email):
    """
    Generate PDF content using HTML to PDF conversion
    This is a simplified version - in production, you'd use a proper PDF library
    """
    # Create HTML content for the diet chart
    html_content = create_html_diet_chart(diet_chart_content, user_name, email)
    
    # Convert HTML to PDF (simplified - would use a proper library in production)
    # For now, return HTML content that can be converted by a client-side library
    return html_content.encode('utf-8')

def create_html_diet_chart(diet_chart_content, user_name, email):
    """
    Create HTML content for the diet chart
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{user_name}'s Personalized Diet Chart</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f8f9fa;
            }}
            .header {{
                background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header h1 {{
                margin: 0;
                font-size: 2.5rem;
                font-weight: 300;
            }}
            .header p {{
                margin: 10px 0 0 0;
                font-size: 1.1rem;
                opacity: 0.9;
            }}
            .user-info {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 30px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .user-info h3 {{
                margin-top: 0;
                color: #1e3a8a;
                border-bottom: 2px solid #e5e7eb;
                padding-bottom: 10px;
            }}
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }}
            .info-item {{
                background: #f3f4f6;
                padding: 15px;
                border-radius: 6px;
            }}
            .info-item strong {{
                display: block;
                color: #1e3a8a;
                margin-bottom: 5px;
            }}
            .meal-plan {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 30px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .day-card {{
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                background: #fafafa;
            }}
            .day-header {{
                background: #1e3a8a;
                color: white;
                padding: 10px 15px;
                border-radius: 6px;
                margin-bottom: 15px;
                font-weight: bold;
                font-size: 1.2rem;
            }}
            .meal-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }}
            .meal-card {{
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                padding: 15px;
            }}
            .meal-title {{
                color: #1e3a8a;
                font-weight: bold;
                margin-bottom: 10px;
                font-size: 1.1rem;
            }}
            .meal-details {{
                font-size: 0.9rem;
                color: #666;
            }}
            .nutrition-info {{
                display: flex;
                justify-content: space-between;
                margin-top: 10px;
                font-size: 0.8rem;
                color: #666;
            }}
            .tips-section {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .tips-title {{
                color: #1e3a8a;
                margin-top: 0;
                border-bottom: 2px solid #e5e7eb;
                padding-bottom: 10px;
            }}
            .tip-item {{
                background: #f3f4f6;
                padding: 10px 15px;
                border-radius: 6px;
                margin-bottom: 10px;
                border-left: 4px solid #1e3a8a;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                color: #666;
                font-size: 0.9rem;
                border-top: 1px solid #e5e7eb;
                padding-top: 20px;
            }}
            .calorie-summary {{
                background: #1e3a8a;
                color: white;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🥗</h1>
            <h1>Personalized Diet Chart</h1>
            <p>Generated for {user_name} • {datetime.utcnow().strftime('%B %d, %Y')}</p>
        </div>

        <div class="user-info">
            <h3>👤 User Information</h3>
            <div class="info-grid">
                <div class="info-item">
                    <strong>Name</strong>
                    {user_name}
                </div>
                <div class="info-item">
                    <strong>Email</strong>
                    {email}
                </div>
                <div class="info-item">
                    <strong>Meal Preference</strong>
                    {diet_chart_content.get('meal_preference', 'Not specified').title()}
                </div>
                <div class="info-item">
                    <strong>Daily Calories</strong>
                    {diet_chart_content.get('daily_calories', 'Not calculated')}
                </div>
            </div>
        </div>

        <div class="calorie-summary">
            <h3 style="margin: 0;">Daily Calorie Target: {diet_chart_content.get('daily_calories', 'Not calculated')} kcal</h3>
            <p style="margin: 5px 0 0 0; opacity: 0.8;">Based on your preferences and goals</p>
        </div>

        <div class="meal-plan">
            <h3>🍽️ 7-Day Meal Plan</h3>
    """
    
    # Add meal plan days
    for day_data in diet_chart_content.get('meal_plan', []):
        html += f"""
            <div class="day-card">
                <div class="day-header">Day {day_data['day']}</div>
                <div class="meal-grid">
        """
        
        for meal_type, meal_data in day_data.items():
            if meal_type == 'day':
                continue
                
            html += f"""
                    <div class="meal-card">
                        <div class="meal-title">{meal_type.title()}</div>
                        <div class="meal-details">
                            <strong>{meal_data['name']}</strong><br>
                            <em>Ingredients:</em> {', '.join(meal_data['ingredients'])}<br>
                            <em>Prep Time:</em> {meal_data['preparation_time']}<br>
                            <em>Difficulty:</em> {meal_data['difficulty']}
                        </div>
                        <div class="nutrition-info">
                            <span>🔥 {meal_data['calories']} kcal</span>
                            <span>🍗 {meal_data['protein']}g protein</span>
                            <span>🍞 {meal_data['carbs']}g carbs</span>
                            <span>🥑 {meal_data['fat']}g fat</span>
                        </div>
                    </div>
            """
        
        html += """
                </div>
            </div>
        """
    
    # Add nutrition tips
    html += """
        </div>

        <div class="tips-section">
            <h3 class="tips-title">💡 Nutrition Tips</h3>
    """
    
    for tip in diet_chart_content.get('nutrition_tips', []):
        html += f"""
            <div class="tip-item">
                {tip}
            </div>
        """
    
    html += """
        </div>

        <div class="footer">
            <p><strong>Maharaja Chef Services</strong></p>
            <p>For extended plans (2+ weeks), premium service is available at $5.99/week</p>
            <p>Contact us: +1 (669) 260-3819 • info@maharajachef.com</p>
        </div>
    </body>
    </html>
    """
    
    return html