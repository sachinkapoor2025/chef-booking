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
S3_BUCKET = os.environ.get('S3_BUCKET', 'maharaja-chef-diet-plans')
S3_REGION = 'us-east-1'

def handler(event, context):
    """Background worker to process diet plan generation"""
    try:
        print(f"DEBUG: Worker received event: {json.dumps(event, indent=2)}")
        
        # Extract plan ID from event
        plan_id = event.get('planId')
        if not plan_id:
            print("ERROR: No planId in event")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing planId'})
            }
        
        # Get the pending plan from DynamoDB
        plans_table = dynamodb.Table(DIET_PLANS_TABLE)
        response = plans_table.get_item(Key={'planId': plan_id})
        
        if 'Item' not in response:
            print(f"ERROR: Plan {plan_id} not found")
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Plan not found'})
            }
        
        plan = response['Item']
        form_data = plan.get('form_data', {})
        
        print(f"DEBUG: Processing plan {plan_id} for user {form_data.get('email')}")
        
        # Generate the diet plan
        result = process_diet_plan(plan_id, form_data)
        
        if result['success']:
            print(f"DEBUG: Successfully processed plan {plan_id}")
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Plan processed successfully', 'planId': plan_id})
            }
        else:
            print(f"ERROR: Failed to process plan {plan_id}: {result.get('error')}")
            # Update plan status to failed
            plans_table.update_item(
                Key={'planId': plan_id},
                UpdateExpression='SET #status = :failed, errorMessage = :error',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':failed': 'failed',
                    ':error': result.get('error', 'Unknown error')
                }
            )
            return {
                'statusCode': 500,
                'body': json.dumps({'error': result.get('error', 'Unknown error')})
            }
            
    except Exception as e:
        print(f"ERROR: Worker failed: {str(e)}")
        # Update plan status to failed
        if 'plan_id' in locals():
            try:
                plans_table = dynamodb.Table(DIET_PLANS_TABLE)
                plans_table.update_item(
                    Key={'planId': plan_id},
                    UpdateExpression='SET #status = :failed, errorMessage = :error',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={
                        ':failed': 'failed',
                        ':error': str(e)
                    }
                )
            except:
                pass
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def process_diet_plan(plan_id, form_data):
    """Process the diet plan generation"""
    try:
        print(f"DEBUG: Starting diet plan processing for {plan_id}")
        
        # Calculate BMI and daily calorie needs
        weight = float(form_data['weight'])
        height = float(form_data['height']) / 100  # Convert to meters
        age = int(form_data['age'])
        gender = form_data.get('gender', 'male')  # Default to male if not specified
        
        # Calculate BMR using Mifflin-St Jeor Equation with gender
        if gender.lower() == 'female':
            bmr = 10 * weight + 6.25 * (height * 100) - 5 * age - 161
        else:
            bmr = 10 * weight + 6.25 * (height * 100) - 5 * age + 5
        
        bmi = weight / (height ** 2)
        
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
        
        print(f"DEBUG: Calculated daily calories: {daily_calories}")
        
        # Prepare prompt for OpenAI
        prompt = create_diet_plan_prompt(form_data, daily_calories, bmi, gender)
        
        # Call OpenAI API
        plan_response = call_openai_api(prompt)
        
        if not plan_response:
            return {'success': False, 'error': 'Failed to get response from OpenAI'}
        
        print(f"DEBUG: OpenAI response received, length: {len(plan_response)}")
        
        # Parse and structure the response
        structured_plan = parse_openai_response(plan_response)
        
        # Update the plan in DynamoDB with the generated content
        plans_table = dynamodb.Table(DIET_PLANS_TABLE)
        
        update_expression = """
            SET #status = :ready,
                planDetails = :planDetails,
                dailyCalories = :dailyCalories,
                bmi = :bmi,
                processedAt = :processedAt
        """
        
        expression_attribute_values = {
            ':ready': 'ready',
            ':planDetails': structured_plan,
            ':dailyCalories': round(daily_calories),
            ':bmi': round(bmi, 2),
            ':processedAt': datetime.utcnow().isoformat()
        }
        
        # Add optional fields if they exist
        if 'gender' in form_data:
            update_expression += ", gender = :gender"
            expression_attribute_values[':gender'] = form_data['gender']
        
        plans_table.update_item(
            Key={'planId': plan_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues=expression_attribute_values
        )
        
        print(f"DEBUG: Successfully updated plan {plan_id} in DynamoDB")
        
        return {'success': True}
        
    except Exception as e:
        print(f"ERROR: Failed to process diet plan: {str(e)}")
        return {'success': False, 'error': str(e)}

def create_diet_plan_prompt(form_data, daily_calories, bmi, gender):
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
- Gender: {gender}
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