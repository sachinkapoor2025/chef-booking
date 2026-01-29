# Diet Plan Feature Implementation

This document provides a comprehensive overview of the diet plan feature implementation for Maharaja Chef Services.

## Overview

The diet plan feature allows users to create personalized weekly diet plans using AI-powered nutrition analysis. The feature includes user registration, plan generation, and premium upgrade options.

## Features

### Core Functionality
- **Personalized Diet Plan Generation**: AI-powered meal planning based on user preferences and health goals
- **User Registration & Authentication**: Secure user accounts with email/password authentication
- **Plan Management**: Users can view, download, and manage their diet plans
- **PDF Generation**: Downloadable PDF versions of diet plans
- **Premium Upgrades**: Extended plans and premium features available for purchase

### User Interface
- **Diet Plan Form** (`diet-plan.html`): Comprehensive form for collecting user information
- **User Registration** (`user-signup.html`): User account creation
- **User Login** (`user-login.html`): User authentication
- **User Profile** (`user-profile.html`): Dashboard for managing diet plans
- **Plan View** (`diet-plan-view.html`): Detailed view of generated diet plans
- **Payment Page** (`payment.html`): Premium plan upgrades

## Technical Architecture

### Backend (AWS Lambda + API Gateway)

#### Lambda Functions
1. **Diet Plan Function** (`backend/src/diet_plan.py`)
   - Handles all diet plan operations
   - Integrates with OpenAI API for plan generation
   - Manages user authentication and plan storage
   - PDF generation and S3 upload functionality

2. **API Endpoints**
   - `POST /prod/diet-plan/generate` - Generate new diet plan
   - `POST /prod/diet-plan/signup` - User registration
   - `POST /prod/diet-plan/login` - User login
   - `GET /prod/diet-plan/user/{userId}/plans` - Get user's plans
   - `GET /prod/diet-plan/{planId}` - Get specific plan
   - `GET /prod/diet-plan/{planId}/download` - Download PDF

#### Database Schema (DynamoDB)
1. **DietPlanUsersTable**
   - `userId` (string) - Primary key
   - `email` (string) - Global secondary index
   - `fullName` (string)
   - `passwordHash` (string)
   - `createdAt` (string)
   - `lastLogin` (string)

2. **DietPlansTable**
   - `planId` (string) - Primary key
   - `userId` (string) - Foreign key to users
   - `email` (string) - User's email
   - `title` (string) - Plan title
   - `createdAt` (string)
   - `status` (string) - pending/active
   - `mealPreference` (string)
   - `primaryGoal` (string)
   - `targetWeight` (number)
   - `currentWeight` (number)
   - `height` (number)
   - `age` (number)
   - `bmi` (number)
   - `dailyCalories` (number)
   - `planDetails` (map) - Structured plan data
   - `form_data` (map) - Original form data

#### AWS Resources
- **API Gateway**: REST API with CORS enabled
- **DynamoDB**: Two tables for users and plans
- **S3**: PDF storage (bucket: `maharaja-chef-diet-plans`)
- **Secrets Manager**: OpenAI API key storage
- **Lambda**: Python 3.12 runtime

### Frontend (Static HTML/CSS/JavaScript)

#### Key Components
1. **Form Validation**: Client-side validation for all form fields
2. **State Management**: localStorage for temporary data storage
3. **API Integration**: Fetch API for backend communication
4. **Responsive Design**: Mobile-friendly layouts
5. **Security**: Secure password handling and API authentication

#### Styling
- **CSS Grid/Flexbox**: Modern layout techniques
- **CSS Variables**: Consistent color scheme
- **Responsive Design**: Mobile-first approach
- **Accessibility**: Semantic HTML and ARIA labels

## Data Flow

### 1. Plan Generation Flow
```
User fills form → Frontend validation → API call to generate endpoint → 
OpenAI API call → Plan parsing → Database storage → Response to frontend
```

### 2. User Authentication Flow
```
User registration/login → Password hashing → Database lookup → 
JWT/session creation → Frontend storage → Protected access
```

### 3. Plan Viewing Flow
```
User selects plan → API call to get plan → Data parsing → 
Frontend rendering → PDF generation option
```

## OpenAI Integration

### Prompt Engineering
The system uses carefully crafted prompts to generate structured diet plans:

```python
prompt = f"""Create a comprehensive 1-week personalized diet plan based on:
- Meal Preference: {meal_preference}
- Daily Calorie Target: {daily_calories} calories
- BMI: {bmi}
- Exercise Frequency: {exercise_freq}
- Primary Goal: {primary_goal}

Requirements:
1. 7-day meal plan with Breakfast, Lunch, Dinner
2. Each meal includes: ingredients, instructions, calories, macros
3. Nutritionally balanced and practical
4. JSON format with specific structure"""
```

### Response Parsing
The system parses OpenAI responses and extracts structured data for:
- Daily meal plans
- Ingredient lists
- Preparation instructions
- Nutritional information
- Shopping lists
- Preparation tips

## Security Considerations

### Data Protection
- **Password Hashing**: SHA-256 hashing for passwords
- **API Security**: CORS configuration and request validation
- **Secrets Management**: OpenAI API key stored in AWS Secrets Manager
- **Input Validation**: Server-side validation for all inputs

### Privacy
- **No Sensitive Data**: No storage of medical records or sensitive health data
- **User Control**: Users can delete their accounts and data
- **Secure Transmission**: HTTPS for all API communications

## Deployment

### Prerequisites
1. AWS CLI configured with appropriate permissions
2. OpenAI API key stored in AWS Secrets Manager
3. S3 bucket created for PDF storage
4. Domain configured for API Gateway (optional)

### Deployment Steps

1. **Deploy Backend Infrastructure**:
   ```bash
   cd backend
   sam build
   sam deploy --guided
   ```

2. **Configure Environment**:
   - Set up OpenAI API key in Secrets Manager
   - Create S3 bucket for PDF storage
   - Configure API Gateway custom domain (optional)

3. **Update Frontend**:
   - Update API endpoints in JavaScript files
   - Configure CORS settings in API Gateway
   - Test all functionality

### Environment Variables
- `DIET_PLAN_USERS_TABLE`: DynamoDB table name for users
- `DIET_PLANS_TABLE`: DynamoDB table name for plans
- `OPENAI_API_KEY`: OpenAI API key from Secrets Manager
- `S3_BUCKET`: S3 bucket name for PDF storage

## Testing

### Manual Testing
1. **Form Validation**: Test all form fields and validation rules
2. **API Endpoints**: Test all API endpoints with various inputs
3. **User Flow**: Complete user registration and plan generation flow
4. **PDF Generation**: Test PDF download functionality
5. **Error Handling**: Test error scenarios and edge cases

### Automated Testing
- Unit tests for Lambda functions
- Integration tests for API endpoints
- Frontend component testing
- Performance testing for OpenAI API calls

## Monitoring & Maintenance

### Logging
- **CloudWatch Logs**: Lambda function logging
- **API Gateway Logs**: API request/response logging
- **Error Tracking**: Exception handling and error reporting

### Performance
- **OpenAI API Limits**: Monitor API usage and rate limits
- **Database Performance**: Monitor DynamoDB read/write capacity
- **PDF Generation**: Monitor S3 upload/download performance

### Maintenance
- **OpenAI API Updates**: Keep up with API changes
- **Security Updates**: Regular security patching
- **User Feedback**: Collect and implement user suggestions

## Future Enhancements

### Planned Features
1. **Mobile App**: Native mobile application
2. **Integration**: Integration with fitness trackers
3. **Community**: User community and recipe sharing
4. **Advanced Analytics**: Progress tracking and analytics
5. **Multi-language**: Support for multiple languages

### Technical Improvements
1. **Caching**: Implement Redis caching for better performance
2. **CDN**: Use CloudFront for faster content delivery
3. **Database Optimization**: Consider Aurora Serverless for complex queries
4. **AI Models**: Experiment with different AI models for better results

## Troubleshooting

### Common Issues
1. **OpenAI API Errors**: Check API key and rate limits
2. **CORS Errors**: Verify API Gateway CORS configuration
3. **PDF Generation**: Check S3 permissions and bucket configuration
4. **Database Errors**: Verify DynamoDB table permissions and structure

### Debugging
- Check CloudWatch logs for Lambda errors
- Use browser developer tools for frontend issues
- Test API endpoints with Postman or curl
- Monitor AWS service health dashboard

## Support

For technical support or questions about this implementation:
- Check the AWS documentation for service-specific issues
- Review OpenAI API documentation for integration questions
- Contact the development team for implementation-specific issues

## License

This implementation is part of the Maharaja Chef Services project. Please refer to the main project license for usage terms.