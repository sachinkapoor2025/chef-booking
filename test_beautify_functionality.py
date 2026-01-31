#!/usr/bin/env python3
"""
Test script to verify the beautify functionality works correctly.
This simulates the beautify process without requiring AWS deployment.
"""

import json
import sys
import os

# Add the backend/src directory to the path so we can import the beautify_chef module
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

def test_beautify_functionality():
    """Test the beautify chef functionality with mock data"""

    print("🧪 Testing Beautify Chef Functionality")
    print("=" * 50)

    # Mock environment variables
    os.environ['CHEF_TABLE'] = 'test-chefs-table'
    os.environ['OPENAI_API_KEY'] = 'test-api-key'  # This will trigger the fallback behavior

    try:
        # Import the beautify_chef module
        import beautify_chef

        # Test data - this simulates what would be sent from the chef.html form
        test_chef_data = {
            "name": "Test Chef",
            "location": "New York",
            "cuisine": "Italian",
            "description": "Great chef with experience",
            "specialties": ["Pasta", "Pizza", "Risotto"],
            "dietaryTags": ["Vegetarian", "Vegan"],
            "rating": 4.5,
            "reviewCount": 10,
            "pricing": [
                {"type": "Dinner Service", "price": "$75/hour", "note": "Min 2 hours"},
                {"type": "Event Catering", "price": "$175/hour", "note": "For parties"}
            ],
            "menuOptions": {
                "Dinner": ["Spaghetti Carbonara", "Lasagna"],
                "Events": ["Wedding Package", "Birthday Buffet"]
            },
            "reviews": [
                {"reviewer": "John D.", "stars": "★★★★★", "text": "Great food!"},
                {"reviewer": "Sarah M.", "stars": "★★★★☆", "text": "Very good"}
            ]
        }

        # Create a mock event object like what AWS Lambda would receive
        mock_event = {
            'httpMethod': 'POST',
            'resource': '/admin/beautify-chef',
            'body': json.dumps({'chefData': test_chef_data})
        }

        # Mock context object
        mock_context = {}

        print("📋 Input Chef Data:")
        print(json.dumps(test_chef_data, indent=2))
        print()

        # Call the beautify function
        result = beautify_chef.handler(mock_event, mock_context)

        print("📊 Beautification Result:")
        print(f"Status Code: {result['statusCode']}")

        if result['statusCode'] == 200:
            response_data = json.loads(result['body'])
            print("✅ Success! Chef data beautified successfully")

            beautified_data = response_data['beautifiedChefData']
            print("\n🎨 Beautified Data:")
            print(f"Description: {beautified_data['description']}")
            print(f"Specialties: {beautified_data['specialties']}")

            # Show pricing notes beautification
            if beautified_data['pricing']:
                print(f"\n💰 Beautified Pricing Notes:")
                for price in beautified_data['pricing']:
                    print(f"  {price['type']}: {price['note']}")

            # Show menu options beautification
            if beautified_data['menuOptions']:
                print(f"\n🍽️ Beautified Menu Options:")
                for category, items in beautified_data['menuOptions'].items():
                    print(f"  {category}:")
                    for item in items:
                        print(f"    - {item}")

            # Show reviews beautification
            if beautified_data['reviews']:
                print(f"\n📝 Beautified Reviews:")
                for review in beautified_data['reviews']:
                    print(f"  {review['reviewer']} ({review['stars']}): {review['text']}")

            return True
        else:
            print("❌ Error:")
            response_data = json.loads(result['body'])
            print(f"Error: {response_data.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Exception during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_html_integration():
    """Test that the HTML page has the correct beautify button setup"""
    print("\n🔍 Testing HTML Integration")
    print("=" * 50)

    try:
        # Read the chef.html file
        with open('website/admin/chef.html', 'r') as f:
            html_content = f.read()

        # Check for beautify button
        if 'id="beautify-content"' in html_content:
            print("✅ Beautify button found in HTML")
        else:
            print("❌ Beautify button not found in HTML")
            return False

        # Check for beautify event handler
        if 'beautify-content' in html_content and 'addEventListener' in html_content:
            print("✅ Beautify event handler found")
        else:
            print("❌ Beautify event handler not found")
            return False

        # Check for API URL
        if 'API_URL' in html_content and '/admin/beautify-chef' in html_content:
            print("✅ API endpoint configuration found")
        else:
            print("❌ API endpoint configuration not found")
            return False

        print("✅ HTML integration looks good!")
        return True

    except Exception as e:
        print(f"❌ Error testing HTML integration: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Beautify Functionality Tests")
    print("=" * 60)

    # Test the beautify functionality
    beautify_success = test_beautify_functionality()

    # Test HTML integration
    html_success = test_html_integration()

    print("\n" + "=" * 60)
    print("📈 TEST SUMMARY")
    print("=" * 60)
    print(f"Beautify Functionality: {'✅ PASS' if beautify_success else '❌ FAIL'}")
    print(f"HTML Integration: {'✅ PASS' if html_success else '❌ FAIL'}")

    if beautify_success and html_success:
        print("\n🎉 All tests passed! The beautify functionality should work correctly.")
        print("\n💡 Next Steps:")
        print("1. Deploy the updated CloudFormation template")
        print("2. Ensure the OpenAI API key is properly configured in AWS Secrets Manager")
        print("3. Test the beautify button in the admin dashboard")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the issues above.")
        sys.exit(1)
