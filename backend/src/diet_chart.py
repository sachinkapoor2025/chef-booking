import json
import boto3
import os
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
import logging
from openai import OpenAI

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS services
dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')
openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', ''))

# Environment variables
DIET_CHARTS_TABLE = os.environ.get('DIET_CHARTS_TABLE', 'DietCharts')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@maharajachef.com')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')

def lambda_handler(event, context):
    """
    Lambda function to handle diet chart requests
    """
    try:
        # Parse the request body
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
        
        # Validate required fields
        required_fields = ['name', 'email', 'mealPreference']
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
        
        # Generate unique ID for the diet chart
        chart_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Create diet chart record
        diet_chart_data = {
            'chart_id': chart_id,
            'name': body['name'],
            'email': body['email'],
            'phone': body.get('phone', ''),
            'meal_preference': body['mealPreference'],
            'allergies': body.get('allergies', ''),
            'medical_conditions': body.get('medicalConditions', ''),
            'goals': body.get('goals', []),
            'gym_frequency': body.get('gymFrequency', ''),
            'activity_level': body.get('activityLevel', ''),
            'work_schedule': body.get('workSchedule', ''),
            'favorite_cuisines': body.get('favoriteCuisines', ''),
            'disliked_foods': body.get('dislikedFoods', ''),
            'cooking_time': body.get('cookingTime', ''),
            'created_at': timestamp,
            'status': 'pending',
            'pdf_url': '',
            'is_premium': False
        }
        
        # Save to DynamoDB
        table = dynamodb.Table(DIET_CHARTS_TABLE)
        table.put_item(Item=diet_chart_data)
        
        # Generate the diet chart content
        diet_chart_content = generate_diet_chart(body)
        
        # Generate PDF (this would be handled by another Lambda or service)
        pdf_url = generate_pdf(chart_id, diet_chart_content, body['name'], body['email'])
        
        # Update the record with PDF URL
        table.update_item(
            Key={'chart_id': chart_id},
            UpdateExpression='SET pdf_url = :pdf_url, status = :status',
            ExpressionAttributeValues={
                ':pdf_url': pdf_url,
                ':status': 'completed'
            }
        )
        
        # Send email notification
        send_diet_chart_email(body['email'], body['name'], pdf_url)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'message': 'Diet chart generated successfully',
                'chart_id': chart_id,
                'pdf_url': pdf_url
            })
        }
        
    except Exception as e:
        logger.error(f"Error generating diet chart: {str(e)}")
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

def generate_diet_chart(user_data):
    """
    Generate personalized diet chart using a single LLM call
    """
    try:
        # Calculate daily calorie needs
        base_calories = calculate_calories(user_data)
        
        # Create prompt for LLM
        prompt = create_diet_chart_prompt(user_data, base_calories)
        
        # Make single LLM call
        llm_response = call_llm_for_diet_chart(prompt)
        
        # Parse and validate LLM response
        diet_chart_content = parse_llm_response(llm_response, user_data, base_calories)
        
        return diet_chart_content
        
    except Exception as e:
        logger.error(f"Error generating diet chart with LLM: {str(e)}")
        # Fallback to traditional method
        return generate_diet_chart_fallback(user_data)

def create_diet_chart_prompt(user_data, base_calories):
    """
    Create a comprehensive prompt for the LLM to generate the entire diet chart
    """
    goals_str = ', '.join(user_data.get('goals', [])) or 'General health'
    medical_conditions = user_data.get('medicalConditions', 'None')
    gym_frequency = user_data.get('gymFrequency', 'No gym routine')
    activity_level = user_data.get('activityLevel', 'moderate')
    cooking_time = user_data.get('cookingTime', '30 minutes')
    
    prompt = f"""Create a comprehensive 7-day personalized diet chart for {user_data['name']}.

User Profile:
- Meal Preference: {user_data['mealPreference']}
- Daily Calorie Target: {base_calories} calories
- Goals: {goals_str}
- Medical Conditions: {medical_conditions}
- Gym Frequency: {gym_frequency}
- Activity Level: {activity_level}
- Cooking Time Available: {cooking_time}
- Favorite Cuisines: {user_data.get('favoriteCuisines', 'No preference')}
- Disliked Foods: {user_data.get('dislikedFoods', 'No dislikes')}
- Allergies: {user_data.get('allergies', 'No allergies')}

Requirements:
1. Generate a 7-day meal plan with breakfast, lunch, dinner, and snack for each day
2. Each meal must include: name, ingredients, calories, protein (g), carbs (g), fat (g), preparation time, difficulty level
3. Total daily calories should match the target of {base_calories} calories
4. Consider dietary restrictions and preferences
5. Provide nutrition tips specific to the user's goals and medical conditions
6. Include easy-to-follow recipes suitable for the available cooking time
7. Ensure variety across the 7 days

Format the response as JSON with this exact structure:
{{
  "user_name": "{user_data['name']}",
  "email": "{user_data['email']}",
  "meal_preference": "{user_data['mealPreference']}",
  "goals": {json.dumps(user_data.get('goals', []))},
  "daily_calories": {base_calories},
  "meal_plan": [
    {{
      "day": 1,
      "breakfast": {{
        "name": "Meal name",
        "ingredients": ["ingredient1", "ingredient2"],
        "calories": 300,
        "protein": 15.0,
        "carbs": 45.0,
        "fat": 8.0,
        "preparation_time": "15-30 minutes",
        "difficulty": "Easy"
      }},
      "lunch": {{...}},
      "dinner": {{...}},
      "snack": {{...}}
    }}
    // ... days 2-7
  ],
  "nutrition_tips": [
    "Tip 1",
    "Tip 2"
  ],
  "generated_at": "2024-01-01T00:00:00"
}}

IMPORTANT: Return ONLY the JSON object, no additional text, explanations, or formatting."""
    
    return prompt

def call_llm_for_diet_chart(prompt):
    """
    Make a single LLM call to generate the complete diet chart using OpenAI
    """
    try:
        logger.info("Calling OpenAI API for diet chart generation")
        
        completion = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional nutritionist and dietitian. "
                        "Create comprehensive, personalized diet charts with detailed meal plans, "
                        "accurate nutrition information, and practical recipes. "
                        "Ensure all dietary restrictions and health conditions are considered."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=4096,
        )
        
        response_text = completion.choices[0].message.content.strip()
        
        logger.info(f"OpenAI response received, tokens used: {completion.usage.total_tokens if completion.usage else 'unknown'}")
        return response_text
        
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}")
        raise

def parse_llm_response(llm_response, user_data, base_calories):
    """
    Parse the LLM response and validate the JSON structure
    """
    try:
        # Extract JSON from response (handle cases where LLM adds extra text)
        import re
        json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            diet_chart = json.loads(json_str)
        else:
            # Try to parse the entire response as JSON
            diet_chart = json.loads(llm_response)
        
        # Validate required fields
        required_fields = ['user_name', 'email', 'meal_preference', 'daily_calories', 'meal_plan', 'nutrition_tips']
        for field in required_fields:
            if field not in diet_chart:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate meal plan structure
        if len(diet_chart['meal_plan']) != 7:
            raise ValueError("Meal plan must contain exactly 7 days")
        
        # Validate each day's meals
        for day_data in diet_chart['meal_plan']:
            required_meals = ['breakfast', 'lunch', 'dinner', 'snack']
            for meal_type in required_meals:
                if meal_type not in day_data:
                    raise ValueError(f"Missing {meal_type} in day {day_data.get('day', 'unknown')}")
                
                meal = day_data[meal_type]
                meal_fields = ['name', 'ingredients', 'calories', 'protein', 'carbs', 'fat', 'preparation_time', 'difficulty']
                for field in meal_fields:
                    if field not in meal:
                        raise ValueError(f"Missing {field} in {meal_type} for day {day_data.get('day', 'unknown')}")
        
        # Add metadata
        diet_chart['generated_at'] = datetime.utcnow().isoformat()
        diet_chart['goals'] = user_data.get('goals', [])
        
        return diet_chart
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in LLM response: {str(e)}")
        raise ValueError("LLM response is not valid JSON")
    except Exception as e:
        logger.error(f"Error parsing LLM response: {str(e)}")
        raise

def generate_diet_chart_fallback(user_data):
    """
    Fallback method using traditional logic if LLM fails
    """
    logger.warning("Using fallback diet chart generation method")
    
    # Calculate daily calorie needs based on activity level and goals
    base_calories = calculate_calories(user_data)
    
    # Generate meal plan for 7 days
    meal_plan = []
    
    for day in range(1, 8):
        day_meals = {
            'day': day,
            'breakfast': generate_meal('breakfast', user_data, base_calories * 0.25),
            'lunch': generate_meal('lunch', user_data, base_calories * 0.35),
            'dinner': generate_meal('dinner', user_data, base_calories * 0.30),
            'snack': generate_meal('snack', user_data, base_calories * 0.10)
        }
        meal_plan.append(day_meals)
    
    return {
        'user_name': user_data['name'],
        'email': user_data['email'],
        'meal_preference': user_data['mealPreference'],
        'goals': user_data.get('goals', []),
        'daily_calories': base_calories,
        'meal_plan': meal_plan,
        'nutrition_tips': get_nutrition_tips(user_data),
        'generated_at': datetime.utcnow().isoformat()
    }

def calculate_calories(user_data):
    """
    Calculate daily calorie needs based on user data
    """
    # Base BMR calculation (simplified)
    # This would be more sophisticated in a real application
    base_bmr = 1500  # Simplified base
    
    # Adjust based on activity level
    activity_multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'very-active': 1.725,
        'extra-active': 1.9
    }
    
    activity_level = user_data.get('activityLevel', 'moderate')
    multiplier = activity_multipliers.get(activity_level, 1.55)
    
    # Adjust based on goals
    goal_adjustments = {
        'weight-loss': -500,
        'weight-gain': +500,
        'muscle-building': +300
    }
    
    goal_adjustment = 0
    goals = user_data.get('goals', [])
    for goal in goals:
        if goal in goal_adjustments:
            goal_adjustment += goal_adjustments[goal]
    
    return int((base_bmr * multiplier) + goal_adjustment)

def generate_meal(meal_type, user_data, calories):
    """
    Generate a meal based on preferences and calorie requirements
    """
    meal_preference = user_data['mealPreference']
    goals = user_data.get('goals', [])
    
    # Base meal templates
    if meal_type == 'breakfast':
        if meal_preference == 'vegetarian':
            base_meal = {
                'name': 'Healthy Breakfast Bowl',
                'ingredients': ['Oats', 'Milk/Plant milk', 'Fruits', 'Nuts'],
                'calories': 300,
                'protein': 15,
                'carbs': 45,
                'fat': 8
            }
        elif meal_preference == 'vegan':
            base_meal = {
                'name': 'Vegan Power Breakfast',
                'ingredients': ['Quinoa', 'Plant milk', 'Berries', 'Seeds'],
                'calories': 280,
                'protein': 12,
                'carbs': 40,
                'fat': 6
            }
        else:
            base_meal = {
                'name': 'Protein Breakfast',
                'ingredients': ['Eggs', 'Whole grain bread', 'Avocado', 'Fruit'],
                'calories': 350,
                'protein': 25,
                'carbs': 35,
                'fat': 15
            }
    
    elif meal_type == 'lunch':
        if meal_preference == 'vegetarian':
            base_meal = {
                'name': 'Balanced Vegetarian Lunch',
                'ingredients': ['Brown rice', 'Lentils', 'Vegetables', 'Salad'],
                'calories': 500,
                'protein': 20,
                'carbs': 60,
                'fat': 12
            }
        elif meal_preference == 'vegan':
            base_meal = {
                'name': 'Vegan Power Lunch',
                'ingredients': ['Quinoa', 'Chickpeas', 'Vegetables', 'Avocado'],
                'calories': 480,
                'protein': 18,
                'carbs': 55,
                'fat': 14
            }
        else:
            base_meal = {
                'name': 'Protein Power Lunch',
                'ingredients': ['Grilled chicken/fish', 'Brown rice', 'Vegetables', 'Salad'],
                'calories': 550,
                'protein': 35,
                'carbs': 50,
                'fat': 15
            }
    
    elif meal_type == 'dinner':
        if meal_preference == 'vegetarian':
            base_meal = {
                'name': 'Light Vegetarian Dinner',
                'ingredients': ['Roti', 'Dal', 'Vegetables', 'Raita'],
                'calories': 450,
                'protein': 18,
                'carbs': 55,
                'fat': 10
            }
        elif meal_preference == 'vegan':
            base_meal = {
                'name': 'Vegan Dinner',
                'ingredients': ['Quinoa', 'Lentil curry', 'Steamed vegetables'],
                'calories': 420,
                'protein': 16,
                'carbs': 50,
                'fat': 8
            }
        else:
            base_meal = {
                'name': 'Balanced Dinner',
                'ingredients': ['Grilled protein', 'Sweet potato', 'Vegetables', 'Salad'],
                'calories': 500,
                'protein': 30,
                'carbs': 45,
                'fat': 12
            }
    
    else:  # snack
        base_meal = {
            'name': 'Healthy Snack',
            'ingredients': ['Nuts', 'Fruit', 'Yogurt/Plant yogurt'],
            'calories': 200,
            'protein': 8,
            'carbs': 25,
            'fat': 8
        }
    
    # Adjust portion sizes based on calorie needs
    calorie_ratio = calories / base_meal['calories']
    
    adjusted_meal = {
        'name': base_meal['name'],
        'ingredients': base_meal['ingredients'],
        'calories': round(base_meal['calories'] * calorie_ratio),
        'protein': round(base_meal['protein'] * calorie_ratio, 1),
        'carbs': round(base_meal['carbs'] * calorie_ratio, 1),
        'fat': round(base_meal['fat'] * calorie_ratio, 1),
        'preparation_time': '15-30 minutes',
        'difficulty': 'Easy'
    }
    
    return adjusted_meal

def get_nutrition_tips(user_data):
    """
    Generate personalized nutrition tips
    """
    tips = []
    goals = user_data.get('goals', [])
    medical_conditions = user_data.get('medicalConditions', '').lower()
    
    if 'weight-loss' in goals:
        tips.append("• Focus on portion control and avoid sugary drinks")
        tips.append("• Include plenty of fiber-rich vegetables in your meals")
        tips.append("• Stay hydrated and get adequate sleep")
    
    if 'weight-gain' in goals:
        tips.append("• Include healthy fats like nuts, seeds, and avocado")
        tips.append("• Eat frequent, nutrient-dense meals throughout the day")
        tips.append("• Combine strength training with proper nutrition")
    
    if 'lower-blood-sugar' in goals or 'diabetes' in medical_conditions:
        tips.append("• Choose complex carbohydrates over simple sugars")
        tips.append("• Monitor portion sizes and eat regular meals")
        tips.append("• Include protein and healthy fats with each meal")
    
    if 'lower-blood-pressure' in goals or 'hypertension' in medical_conditions:
        tips.append("• Reduce sodium intake and avoid processed foods")
        tips.append("• Include potassium-rich foods like bananas and leafy greens")
        tips.append("• Limit alcohol and maintain a healthy weight")
    
    if 'muscle-building' in goals:
        tips.append("• Ensure adequate protein intake throughout the day")
        tips.append("• Time your meals around your workout sessions")
        tips.append("• Stay consistent with both training and nutrition")
    
    if not tips:
        tips.append("• Eat a balanced diet with variety of nutrients")
        tips.append("• Stay hydrated and listen to your body's hunger cues")
        tips.append("• Maintain regular meal times and avoid skipping meals")
    
    return tips

def generate_pdf(chart_id, diet_chart_content, name, email):
    """
    Generate PDF from diet chart content
    This would typically call another Lambda function or service
    """
    # In a real implementation, this would:
    # 1. Call a PDF generation service
    # 2. Upload the PDF to S3
    # 3. Return the S3 URL
    
    # For now, return a placeholder URL
    return f"https://example.com/diet-charts/{chart_id}.pdf"

def send_diet_chart_email(email, name, pdf_url):
    """
    Send email notification with diet chart
    """
    try:
        subject = f"Your Personalized Diet Chart - {name}"
        
        body_text = f"""
Hello {name},

Your personalized 1-week diet chart has been generated successfully!

You can download your diet chart from: {pdf_url}

The chart includes:
• 7-day personalized meal plan
• Detailed nutrition information
• Easy-to-follow recipes
• Calorie and macro tracking

If you need more weeks or want to continue with our premium service ($5.99/week), 
please visit our website or contact us.

Best regards,
Maharaja Chef Services Team
        """
        
        body_html = f"""
        <html>
        <head></head>
        <body>
            <h2>Hello {name},</h2>
            <p>Your personalized 1-week diet chart has been generated successfully!</p>
            
            <p><a href="{pdf_url}" style="background-color: #1e3a8a; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Download Your Diet Chart</a></p>
            
            <h3>What's included:</h3>
            <ul>
                <li>✅ 7-day personalized meal plan</li>
                <li>✅ Detailed nutrition information</li>
                <li>✅ Easy-to-follow recipes</li>
                <li>✅ Calorie and macro tracking</li>
            </ul>
            
            <p>If you need more weeks or want to continue with our premium service ($5.99/week), 
            please visit our <a href="https://maharajachef.com">website</a> or contact us.</p>
            
            <p>Best regards,<br>
            Maharaja Chef Services Team</p>
        </body>
        </html>
        """
        
        response = ses.send_email(
            Source=FROM_EMAIL,
            Destination={
                'ToAddresses': [email]
            },
            Message={
                'Subject': {
                    'Data': subject
                },
                'Body': {
                    'Text': {
                        'Data': body_text
                    },
                    'Html': {
                        'Data': body_html
                    }
                }
            }
        )
        
        logger.info(f"Email sent successfully to {email}")
        return True
        
    except ClientError as e:
        logger.error(f"Error sending email: {e}")
        return False