import json
import boto3
import os
import uuid
import hashlib
import base64
from datetime import datetime, timedelta
import requests
from botocore.exceptions import ClientError

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

def generate_diet_plan(form_data):
    """Generate a personalized diet plan using OpenAI API"""
    try:
        print(f"DEBUG: Starting generate_diet_plan with form_data: {json.dumps(form_data, indent=2)}")
        
        # Validate required fields
        required_fields = ['fullName', 'email', 'age', 'weight', 'height', 'mealPreference', 'exerciseFrequency', 'jobType', 'primaryGoal', 'targetWeight']
        for field in required_fields:
            if not form_data.get(field):
                print(f"DEBUG: Missing required field: {field}")
                return {
                    'statusCode': 400,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                        'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
                    },
                    'body': json.dumps({'error': f'Missing required field: {field}'})
                }
        
        print("DEBUG: All required fields validated successfully")
        
        # Calculate BMI and daily calorie needs
        weight = float(form_data['weight'])
        height = float(form_data['height']) / 100  # Convert to meters
        age = int(form_data['age'])
        bmi = weight / (height ** 2)
        
        # Calculate BMR (Basal Metabolic Rate) using Mifflin-St Jeor Equation
        # Assuming male for simplicity, in production you'd want gender field
        bmr = 10 * weight + 6.25 * (height * 100) - 5 * age + 5
        
        # Activity multiplier based on job type and exercise frequency
        activity_multipliers = {
            'sedentary': {'rarely': 1.2, '1-2-times-week': 1.375, '3-4-times-week': 1.45, '5-6-times-week': 1.55, 'daily': 1.725},
            'light-activity': {'rarely': 1.375, '1-2-times-week': 1.45, '3-4-times-week': 1.55, '5-6-times-week': 1.65, 'daily': 1.825},
            'moderate-activity': {'rarely': 1.45, '1-2-times-week': 1.55, '3-4-times-week': 1.65, '5-6-times-week': 1.75, 'daily': 1.925},
            'heavy-activity': {'rarely': 1.55, '1-2-times-week': 1.65, '3-4-times-week': 1.75, '5-6-times-week': 1.85, 'daily': 2.025}
        }
        
        job_type = form_data['jobType']
        exercise_freq = form_data['exerciseFrequency']
        activity_multiplier = activity_multipliers.get(job_type, {}).get(exercise_freq, 1.4)
        
        daily_calories = bmr * activity_multiplier
        
        # Adjust calories based on goal
        goal = form_data['primaryGoal']
        target_weight = float(form_data['targetWeight'])
        
        if goal == 'weight-loss':
            daily_calories -= 500  # 0.5kg weight loss per week
        elif goal == 'weight-gain':
            daily_calories += 500  # 0.5kg weight gain per week
        elif goal == 'muscle-building':
            daily_calories += 300  # Moderate surplus for muscle gain
        
        # Prepare prompt for OpenAI
        prompt = create_diet_plan_prompt(form_data, daily_calories, bmi)
        
        # Call OpenAI API
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
        
        # Parse and structure the response
        structured_plan = parse_openai_response(plan_response)
        
        # Generate unique plan ID
        plan_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        # Create plan record
        plan_data = {
            'planId': plan_id,
            'userId': None,  # Will be set when user signs up
            'email': form_data['email'],
            'title': f"Weekly Diet Plan for {form_data['fullName']}",
            'createdAt': created_at,
            'status': 'pending',
            'mealPreference': form_data['mealPreference'],
            'primaryGoal': goal,
            'targetWeight': target_weight,
            'currentWeight': weight,
            'height': height * 100,  # Store in cm
            'age': age,
            'bmi': round(bmi, 2),
            'dailyCalories': round(daily_calories),
            'planDetails': structured_plan,
            'form_data': form_data
        }
        
        # Store in DynamoDB
        plans_table = dynamodb.Table(DIET_PLANS_TABLE)
        plans_table.put_item(Item=plan_data)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
            },
            'body': json.dumps({
                'message': 'Diet plan generated successfully',
                'planId': plan_id,
                'plan': plan_data
            })
        }
        
    except Exception as e:
        print(f"Error generating diet plan: {str(e)}")
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
    try:
        email = form_data['email']
        password = form_data['password']
        full_name = form_data['fullName']
        plan_data = form_data.get('planData', {})
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Generate user ID
        user_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        # Check if email already exists
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
        
        # Create user record
        user_data = {
            'userId': user_id,
            'email': email,
            'fullName': full_name,
            'passwordHash': password_hash,
            'createdAt': created_at,
            'lastLogin': created_at
        }
        
        users_table.put_item(Item=user_data)
        
        # If there's a pending plan, associate it with the user
        if plan_data and plan_data.get('planId'):
            plans_table = dynamodb.Table(DIET_PLANS_TABLE)
            plans_table.update_item(
                Key={'planId': plan_data['planId']},
                UpdateExpression='SET userId = :uid, #status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':uid': user_id,
                    ':status': 'active'
                }
            )
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
            },
            'body': json.dumps({
                'message': 'User created successfully',
                'userId': user_id,
                'email': email,
                'fullName': full_name
            })
        }
        
    except Exception as e:
        print(f"Error creating user: {str(e)}")
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
    try:
        email = form_data['email']
        password = form_data['password']
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Check user credentials
        users_table = dynamodb.Table(DIET_PLAN_USERS_TABLE)
        response = users_table.get_item(Key={'email': email})
        
        if 'Item' not in response:
            return {
                'statusCode': 401,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
                },
                'body': json.dumps({'error': 'Invalid email or password'})
            }
        
        user = response['Item']
        
        if user['passwordHash'] != password_hash:
            return {
                'statusCode': 401,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
                },
                'body': json.dumps({'error': 'Invalid email or password'})
            }
        
        # Update last login
        users_table.update_item(
            Key={'userId': user['userId']},
            UpdateExpression='SET lastLogin = :time',
            ExpressionAttributeValues={':time': datetime.utcnow().isoformat()}
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
            },
            'body': json.dumps({
                'message': 'Login successful',
                'userId': user['userId'],
                'email': user['email'],
                'fullName': user['fullName']
            })
        }
        
    except Exception as e:
        print(f"Error during login: {str(e)}")
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
                    'content': 'You are a professional nutritionist and dietitian. Create detailed, personalized diet plans that are scientifically sound, practical, and tailored to individual needs.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 4000,
            'temperature': 0.7
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
    """Parse the OpenAI response and extract structured data"""
    # This is a simplified parser - in production, you might want to use a more robust JSON parsing approach
    # or ask OpenAI to return valid JSON directly
    
    try:
        # Try to extract JSON from the response
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group()
            # Clean up the JSON string
            json_str = json_str.replace('\n', '').replace('\t', '')
            return json.loads(json_str)
        else:
            # If no JSON found, return a basic structure
            return {
                'weekOverview': {'dailyCalorieTarget': 0, 'mealDistribution': '', 'keyFocusAreas': []},
                'dailyPlans': [],
                'shoppingList': {'produce': [], 'proteins': [], 'pantry': []},
                'prepTips': [],
                'notes': response_text[:500]  # Truncate long text
            }
            
    except Exception as e:
        print(f"Error parsing OpenAI response: {str(e)}")
        return {
            'weekOverview': {'dailyCalorieTarget': 0, 'mealDistribution': '', 'keyFocusAreas': []},
            'dailyPlans': [],
            'shoppingList': {'produce': [], 'proteins': [], 'pantry': []},
            'prepTips': [],
            'notes': 'Error parsing response'
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