#!/usr/bin/env python3
"""
Test script for async diet plan generation
This script tests the complete async flow from form submission to plan generation
"""

import json
import requests
import time
import uuid

# Configuration
API_BASE_URL = "https://mygfyqg69g.execute-api.us-east-1.amazonaws.com/prod"
TEST_EMAIL = f"test+{uuid.uuid4().hex[:8]}@example.com"

def test_async_diet_plan_flow():
    """Test the complete async diet plan generation flow"""
    
    print("🧪 Testing Async Diet Plan Generation Flow")
    print("=" * 50)
    
    # Test data
    test_form_data = {
        "fullName": "Test User",
        "email": TEST_EMAIL,
        "age": 30,
        "weight": 70.5,
        "height": 175,
        "mealPreference": "vegetarian",
        "exerciseFrequency": "3-4-times-week",
        "jobType": "moderate-activity",
        "primaryGoal": "weight-loss",
        "targetWeight": 65.0,
        "gender": "male",
        "cuisinePreferences": ["indian", "mediterranean"],
        "allergies": "",
        "medicalConditions": "",
        "cookingTime": "30-minutes",
        "additionalNotes": "Test diet plan generation"
    }
    
    print(f"📝 Test email: {TEST_EMAIL}")
    print(f"📊 Test data: {json.dumps(test_form_data, indent=2)}")
    
    # Step 1: Generate diet plan (async)
    print("\n1️⃣ Generating diet plan (async)...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/diet-plan/generate",
            json=test_form_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            plan_id = result.get('planId')
            status = result.get('status')
            
            print(f"✅ Plan created successfully!")
            print(f"   Plan ID: {plan_id}")
            print(f"   Status: {status}")
            print(f"   Message: {result.get('message')}")
            
            # Step 2: Check plan status
            print(f"\n2️⃣ Checking plan status...")
            for attempt in range(10):  # Check up to 10 times
                time.sleep(5)  # Wait 5 seconds between checks
                
                status_response = requests.get(
                    f"{API_BASE_URL}/diet-plan/{plan_id}",
                    timeout=10
                )
                
                if status_response.status_code == 200:
                    plan_data = status_response.json().get('plan', {})
                    current_status = plan_data.get('status')
                    
                    print(f"   Attempt {attempt + 1}: Status = {current_status}")
                    
                    if current_status == 'ready':
                        print(f"✅ Plan is ready!")
                        print(f"   Daily Calories: {plan_data.get('dailyCalories')}")
                        print(f"   BMI: {plan_data.get('bmi')}")
                        print(f"   Meal Preference: {plan_data.get('mealPreference')}")
                        
                        # Check if plan details exist
                        plan_details = plan_data.get('planDetails', {})
                        if plan_details:
                            daily_plans = plan_details.get('dailyPlans', [])
                            print(f"   Generated {len(daily_plans)} days of meal plans")
                            
                            if daily_plans:
                                first_day = daily_plans[0]
                                meals = first_day.get('meals', [])
                                print(f"   First day has {len(meals)} meals")
                        
                        return True
                    elif current_status == 'failed':
                        print(f"❌ Plan generation failed!")
                        print(f"   Error: {plan_data.get('errorMessage', 'Unknown error')}")
                        return False
                    elif current_status == 'processing':
                        print(f"   Still processing...")
                        continue
                else:
                    print(f"❌ Error checking status: {status_response.status_code}")
                    return False
            
            print(f"⏰ Timeout: Plan still processing after 50 seconds")
            return False
            
        else:
            print(f"❌ Failed to create plan: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_user_signup():
    """Test user signup flow"""
    print("\n3️⃣ Testing user signup...")
    
    test_user_data = {
        "email": TEST_EMAIL,
        "password": "testpassword123",
        "fullName": "Test User",
        "planData": {
            "planId": "test-plan-id"
        }
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/diet-plan/signup",
            json=test_user_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ User signup successful!")
            return True
        else:
            print(f"❌ User signup failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during signup: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Async Diet Plan Tests")
    print("=" * 60)
    
    # Test async flow
    async_success = test_async_diet_plan_flow()
    
    # Test user signup
    signup_success = test_user_signup()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"   Async Diet Plan: {'✅ PASS' if async_success else '❌ FAIL'}")
    print(f"   User Signup: {'✅ PASS' if signup_success else '❌ FAIL'}")
    
    if async_success and signup_success:
        print("\n🎉 All tests passed! Async diet plan generation is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
    
    return async_success and signup_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)