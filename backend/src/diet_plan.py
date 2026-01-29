import json
import boto3
import os
import uuid
import hashlib
import base64
from datetime import datetime, timedelta
import requests
from botocore.exceptions import ClientError
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

DIET_PLAN_USERS_TABLE = os.environ['DIET_PLAN_USERS_TABLE']
DIET_PLANS_TABLE = os.environ['DIET_PLANS_TABLE']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

# S3 configuration
S3_BUCKET = 'maharaja-chef-diet-plans'  # You'll need to create this bucket
S3_REGION = 'us-east-1'

def handler(event, context):
    try:
        print(f"DEBUG: Event received: {json.dumps(event, indent=2)}")
        print(f"DEBUG: Context: {context}")
        
        # Check environment variables
        print(f"DEBUG: DIET_PLAN_USERS_TABLE: {os.environ.get('DIET_PLAN_USERS_TABLE', 'NOT_SET')}")
        print(f"DEBUG: DIET_PLANS_TABLE: {os.environ.get('DIET_PLANS_TABLE', 'NOT_SET')}")
        print(f"DEBUG: OPENAI_API_KEY: {'SET' if os.environ.get('OPENAI_API_KEY') else 'NOT_SET'}")
        print(f"DEBUG: S3_BUCKET: {os.environ.get('S3_BUCKET', 'NOT_SET')}")
        
        # Parse the API Gateway event
        http_method = event.get('httpMethod', '')
        path = event.get("requestContext", {}).get("path", event.get("path", ""))
        print(f"DEBUG: HTTP Method: {http_method}, Path: {path}")
        print("DEBUG: Final resolved path =", path)
        
        # Extract path parameters
        path_params = event.get('pathParameters', {}) or {}
        user_id = path_params.get('userId')
        plan_id = path_params.get('planId')
        print(f"DEBUG: Path params: {path_params}, User ID: {user_id}, Plan ID: {plan_id}")
        
        # Extract query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        print(f"DEBUG: Query params: {query_params}")
        
        # Extract body for POST requests
        body = None
        if http_method == 'POST' and event.get('body'):
            try:
                body = json.loads(event['body'])
                print(f"DEBUG: Parsed body: {json.dumps(body, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"DEBUG: JSON decode error: {e}")
                return {
                    'statusCode': 400,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                        'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
                    },
                    'body': json.dumps({'error': 'Invalid JSON in request body'})
                }
        else:
            print(f"DEBUG: No body or not POST request. Body: {event.get('body')}")
        
        # Route to appropriate function based on path and method
        if path.endswith('/diet-plan/generate') and http_method == 'POST':
            return generate_diet_plan(body)

        elif path.endswith('/diet-plan/signup') and http_method == 'POST':
            return user_signup(body)

        elif path.endswith('/diet-plan/login') and http_method == 'POST':
            return user_login(body)

        elif path.endswith(f'/diet-plan/user/{user_id}/plans') and http_method == 'GET':
            return get_user_plans(user_id)

        elif path.endswith(f'/diet-plan/{plan_id}/download') and http_method == 'GET':
            return download_diet_plan(plan_id)

        elif path.endswith(f'/diet-plan/{plan_id}') and http_method == 'GET':
            return get_diet_plan(plan_id)

        else:
            print("DEBUG: ❌ No route matched")
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
                },
                'body': json.dumps({'error': 'Endpoint not found'})
            }
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
def convert_floats_to_decimal(obj):
    if isinstance(obj, list):
        return [convert_floats_to_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    else:
        return obj

def generate_diet_plan(form_data):
    """Generate a personalized diet plan using OpenAI API"""

    # ✅ SAFETY CHECK (this fixes your crash)
    if not form_data:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
            },
            'body': json.dumps({'error': 'Request body is missing'})
        }

    try:
        print(f"DEBUG: Starting generate_diet_plan with form_data: {json.dumps(form_data, indent=2)}")

        required_fields = ['fullName','email','age','weight','height','mealPreference','exerciseFrequency','jobType','primaryGoal','targetWeight']
        for field in required_fields:
            if not form_data.get(field):
                return {
                    'statusCode': 400,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                        'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
                    },
                    'body': json.dumps({'error': f'Missing required field: {field}'})
                }

        weight = float(form_data['weight'])
        height = float(form_data['height']) / 100
        age = int(form_data['age'])
        bmi = weight / (height ** 2)

        bmr = 10 * weight + 6.25 * (height * 100) - 5 * age + 5

        activity_multipliers = {
            'sedentary': {'rarely': 1.2,'1-2-times-week': 1.375,'3-4-times-week': 1.45,'5-6-times-week': 1.55,'daily': 1.725},
            'light-activity': {'rarely': 1.375,'1-2-times-week': 1.45,'3-4-times-week': 1.55,'5-6-times-week': 1.65,'daily': 1.825},
            'moderate-activity': {'rarely': 1.45,'1-2-times-week': 1.55,'3-4-times-week': 1.65,'5-6-times-week': 1.75,'daily': 1.925},
            'heavy-activity': {'rarely': 1.55,'1-2-times-week': 1.65,'3-4-times-week': 1.75,'5-6-times-week': 1.85,'daily': 2.025}
        }

        daily_calories = bmr * activity_multipliers.get(form_data['jobType'], {}).get(form_data['exerciseFrequency'], 1.4)

        if form_data['primaryGoal'] == 'weight-loss':
            daily_calories -= 500
        elif form_data['primaryGoal'] == 'weight-gain':
            daily_calories += 500
        elif form_data['primaryGoal'] == 'muscle-building':
            daily_calories += 300

        prompt = create_diet_plan_prompt(form_data, daily_calories, bmi)
        plan_response = call_openai_api(prompt)

        if not plan_response:
            return {
                'statusCode': 500,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
                },
                'body': json.dumps({'error': 'Failed to generate diet plan'})
            }

        structured_plan = parse_openai_response(plan_response)
        structured_plan = convert_floats_to_decimal(structured_plan)
        plan_id = str(uuid.uuid4())

        dynamodb.Table(DIET_PLANS_TABLE).put_item(Item={
            'planId': plan_id,
            'userId': f"PENDING#{form_data['email']}",
            'email': form_data['email'],
            'title': f"Weekly Diet Plan for {form_data['fullName']}",
            'createdAt': datetime.utcnow().isoformat(),
            'status': 'pending',
            'mealPreference': form_data['mealPreference'],
            'primaryGoal': form_data['primaryGoal'],
            'targetWeight': Decimal(str(form_data['targetWeight'])),
            'currentWeight': Decimal(str(weight)),
            'height': Decimal(str(height * 100)),
            'age': age,
            'bmi': Decimal(str(round(bmi, 2))),
            'dailyCalories': Decimal(str(round(daily_calories))),
            'planDetails': structured_plan,
            'form_data': form_data
        })

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
            },
            'body': json.dumps({'message': 'Diet plan generated successfully', 'planId': plan_id})
        }

    except Exception as e:
        print("Error generating diet plan:", str(e))
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
            },
            'body': json.dumps({'error': 'Failed to generate diet plan'})
        }

def user_signup(form_data):
    """Create a new user account and associate with diet plan"""

    # ✅ SAFETY CHECK
    if not form_data:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
            },
            'body': json.dumps({'error': 'Request body is missing'})
        }

    try:
        email = form_data['email']
        password = form_data['password']
        full_name = form_data['fullName']
        plan_data = form_data.get('planData', {})

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()

        users_table = dynamodb.Table(DIET_PLAN_USERS_TABLE)
        response = users_table.get_item(Key={'email': email})

        if 'Item' in response:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
                },
                'body': json.dumps({'error': 'Email already registered'})
            }

        users_table.put_item(Item={
            'userId': user_id,
            'email': email,
            'fullName': full_name,
            'passwordHash': password_hash,
            'createdAt': created_at,
            'lastLogin': created_at
        })

        if plan_data and plan_data.get('planId'):
            dynamodb.Table(DIET_PLANS_TABLE).update_item(
                Key={'planId': plan_data['planId']},
                UpdateExpression='SET userId = :uid, #status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':uid': user_id, ':status': 'active'}
            )

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
            },
            'body': json.dumps({'message': 'User created successfully', 'userId': user_id})
        }

    except Exception as e:
        print("Error creating user:", str(e))
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
            },
            'body': json.dumps({'error': 'Failed to create user'})
        }


def user_login(form_data):
    """Authenticate user login"""

    # ✅ SAFETY CHECK
    if not form_data:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
            },
            'body': json.dumps({'error': 'Request body is missing'})
        }

    try:
        email = form_data['email']
        password = form_data['password']
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        users_table = dynamodb.Table(DIET_PLAN_USERS_TABLE)
        response = users_table.get_item(Key={'email': email})

        if 'Item' not in response or response['Item']['passwordHash'] != password_hash:
            return {
                'statusCode': 401,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
                },
                'body': json.dumps({'error': 'Invalid email or password'})
            }

        users_table.update_item(
            Key={'email': email},
            UpdateExpression='SET lastLogin = :time',
            ExpressionAttributeValues={':time': datetime.utcnow().isoformat()}
        )

        user = response['Item']

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
            },
            'body': json.dumps({'message': 'Login successful', 'userId': user['userId'], 'email': user['email']})
        }

    except Exception as e:
        print("Error during login:", str(e))
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
            },
            'body': json.dumps({'error': 'Login failed'})
        }


def get_user_plans(user_id):
    """Get all diet plans for a user"""
    try:
        plans_table = dynamodb.Table(DIET_PLANS_TABLE)
        
        # Query user's plans
        response = plans_table.query(
            IndexName='user-plans-index',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('userId').eq(user_id),
            ScanIndexForward=False  # Most recent first
        )
        
        plans = response.get('Items', [])
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
            },
            'body': json.dumps({'plans': plans})
        }
        
    except Exception as e:
        print(f"Error getting user plans: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
            },
            'body': json.dumps({'error': 'Failed to get user plans'})
        }

def get_diet_plan(plan_id):
    """Get a specific diet plan"""
    try:
        plans_table = dynamodb.Table(DIET_PLANS_TABLE)
        response = plans_table.get_item(Key={'planId': plan_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
                },
                'body': json.dumps({'error': 'Plan not found'})
            }
        
        plan = response['Item']
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
            },
            'body': json.dumps({'plan': plan})
        }
        
    except Exception as e:
        print(f"Error getting diet plan: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
            },
            'body': json.dumps({'error': 'Failed to get diet plan'})
        }

def download_diet_plan(plan_id):
    """Generate and return PDF download URL for diet plan"""
    try:
        # Get the plan
        plans_table = dynamodb.Table(DIET_PLANS_TABLE)
        response = plans_table.get_item(Key={'planId': plan_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
                },
                'body': json.dumps({'error': 'Plan not found'})
            }
        
        plan = response['Item']
        
        # Generate PDF content
        pdf_content = generate_pdf_content(plan)
        
        # Upload to S3
        pdf_key = f"diet-plans/{plan_id}/diet-plan-{plan_id}.pdf"
        
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=pdf_key,
            Body=pdf_content,
            ContentType='application/pdf',
            ACL='private'
        )
        
        # Generate presigned URL
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': pdf_key},
            ExpiresIn=3600  # 1 hour
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
            },
            'body': json.dumps({
                'downloadUrl': presigned_url,
                'fileName': f"diet-plan-{plan_id}.pdf"
            })
        }
        
    except Exception as e:
        print(f"Error downloading diet plan: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
            },
            'body': json.dumps({'error': 'Failed to download diet plan'})
        }

def create_diet_plan_prompt(form_data, daily_calories, bmi):
    """Create a detailed prompt for OpenAI to generate a personalized diet plan"""
    
    # Extract form data
    meal_preference = form_data['mealPreference']
    exercise_freq = form_data['exerciseFrequency']
    job_type = form_data['jobType']
    primary_goal = form_data['primaryGoal']
    target_weight = form_data['targetWeight']
    cuisine_preferences = form_data.get('cuisinePreferences', [])
    disliked_foods = form_data.get('dislikedFoods', '')
    allergies = form_data.get('allergies', '')
    medical_conditions = form_data.get('medicalConditions', '')
    cooking_time = form_data.get('cookingTime', '30-minutes')
    
    # Create detailed prompt
    prompt = f"""Create a comprehensive 1-week personalized diet plan based on the following information:

PERSONAL DETAILS:
- Meal Preference: {meal_preference}
- Daily Calorie Target: {round(daily_calories)} calories
- BMI: {round(bmi, 2)}
- Exercise Frequency: {exercise_freq}
- Job Type: {job_type}
- Primary Goal: {primary_goal}
- Target Weight: {target_weight} kg

PREFERENCES:
- Cuisine Preferences: {', '.join(cuisine_preferences) if cuisine_preferences else 'No specific preferences'}
- Disliked Foods: {disliked_foods if disliked_foods else 'None specified'}
- Cooking Time Available: {cooking_time}

HEALTH CONSIDERATIONS:
- Allergies: {allergies if allergies else 'None specified'}
- Medical Conditions: {medical_conditions if medical_conditions else 'None specified'}

REQUIREMENTS:
1. Create a 7-day meal plan (Day 1 through Day 7)
2. For each day, provide Breakfast, Lunch, and Dinner
3. Each meal should include:
   - Meal name
   - Detailed ingredients list with quantities
   - Step-by-step preparation instructions
   - Approximate calorie count
   - Macronutrient breakdown (protein, carbs, fat)
   - Key vitamins and minerals

4. Ensure the plan is:
   - Nutritionally balanced
   - Suitable for the specified meal preference (vegetarian/vegan/non-vegetarian)
   - Takes into account cooking time constraints
   - Avoids any specified disliked foods or allergens
   - Supports the primary goal (weight loss, muscle building, etc.)

5. Include a weekly shopping list organized by category
6. Provide preparation tips and meal prep suggestions
7. Add any special notes or recommendations

FORMAT: Return the response in a structured JSON format with the following structure:
{{
  "weekOverview": {{
    "dailyCalorieTarget": {round(daily_calories)},
    "mealDistribution": "Breakfast: X%, Lunch: X%, Dinner: X%",
    "keyFocusAreas": ["list", "of", "focus", "areas"]
  }},
  "dailyPlans": [
    {{
      "day": 1,
      "meals": [
        {{
          "mealType": "Breakfast",
          "name": "Meal Name",
          "ingredients": ["ingredient1", "ingredient2"],
          "instructions": ["step1", "step2"],
          "calories": 350,
          "macros": {{"protein": "25g", "carbs": "45g", "fat": "10g"}},
          "nutrients": {{"vitaminA": "50%", "vitaminC": "30%", "iron": "15%"}}
        }}
      ]
    }}
  ],
  "shoppingList": {{
    "produce": ["item1", "item2"],
    "proteins": ["item1", "item2"],
    "pantry": ["item1", "item2"]
  }},
  "prepTips": ["tip1", "tip2"],
  "notes": "Additional notes and recommendations"
}}

Make the plan practical, delicious, and achievable for someone with the specified lifestyle and preferences."""
    
    return prompt

def call_openai_api(prompt):
    """Call OpenAI API to generate diet plan"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPENAI_API_KEY}'
        }
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are a professional nutritionist. You MUST return ONLY valid JSON. No explanation. No markdown. No extra text.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 4000,
            'temperature': 0.4
        }
        
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"OpenAI API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return None

def parse_openai_response(response_text):
    try:
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        json_str = response_text[start:end]
        return json.loads(json_str)

    except Exception as e:
        print("❌ RAW OPENAI RESPONSE (first 3000 chars):\n", response_text[:3000])
        print("❌ JSON PARSE ERROR:", str(e))

        return {
            "weekOverview": {},
            "dailyPlans": [],
            "shoppingList": {},
            "prepTips": [],
            "notes": "AI response could not be parsed. Check CloudWatch logs."
        }

def generate_pdf_content(plan):
    """Generate PDF content for the diet plan"""
    # This is a simplified PDF generator
    # In production, you might want to use a library like ReportLab or WeasyPrint
    
    try:
        # Create HTML content for the PDF
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{plan.get('title', 'Diet Plan')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1, h2, h3 {{ color: #333; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .day {{ margin-bottom: 30px; border-bottom: 1px solid #ddd; padding-bottom: 20px; }}
                .meal {{ margin-bottom: 15px; }}
                .meal h3 {{ color: #007bff; }}
                .ingredients, .instructions {{ margin-left: 20px; }}
                .calories {{ font-weight: bold; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{plan.get('title', 'Weekly Diet Plan')}</h1>
                <p><strong>Client:</strong> {plan.get('email', 'N/A')}</p>
                <p><strong>Meal Preference:</strong> {plan.get('mealPreference', 'N/A')}</p>
                <p><strong>Primary Goal:</strong> {plan.get('primaryGoal', 'N/A')}</p>
                <p><strong>Daily Calories:</strong> {plan.get('dailyCalories', 'N/A')} kcal</p>
            </div>
        """
        
        # Add daily plans
        plan_details = plan.get('planDetails', {})
        daily_plans = plan_details.get('dailyPlans', [])
        
        for day_data in daily_plans:
            day_num = day_data.get('day', 0)
            html_content += f"<div class='day'><h2>Day {day_num}</h2>"
            
            for meal in day_data.get('meals', []):
                meal_type = meal.get('mealType', '')
                meal_name = meal.get('name', '')
                calories = meal.get('calories', 0)
                
                html_content += f"""
                <div class='meal'>
                    <h3>{meal_type}: {meal_name}</h3>
                    <p class='calories'>Calories: {calories}</p>
                    <h4>Ingredients:</h4>
                    <ul class='ingredients'>
                """
                
                for ingredient in meal.get('ingredients', []):
                    html_content += f"<li>{ingredient}</li>"
                
                html_content += "</ul><h4>Instructions:</h4><ol class='instructions'>"
                
                for instruction in meal.get('instructions', []):
                    html_content += f"<li>{instruction}</li>"
                
                html_content += "</ol></div>"
            
            html_content += "</div>"
        
        html_content += """
        </body>
        </html>
        """
        
        # Convert HTML to PDF (simplified - would need proper HTML to PDF conversion)
        # For now, return the HTML content as a text file
        return html_content.encode('utf-8')
        
    except Exception as e:
        print(f"Error generating PDF content: {str(e)}")
        return f"Error generating PDF: {str(e)}".encode('utf-8')