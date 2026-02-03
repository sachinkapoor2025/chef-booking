# Chef Application Feature

This feature allows chefs to apply to join Maharaja Chef Services through a dedicated application page with a backend Lambda function for processing submissions.

## Overview

The chef application feature consists of:

1. **Frontend**: A dedicated application page (`chef-application.html`) with a comprehensive form
2. **Backend**: A Lambda function (`chef_application.py`) for processing applications
3. **Infrastructure**: Updated SAM template with required AWS resources

## Features

### Application Form
- **Personal Information**: Name, email, phone, location
- **Professional Details**: Experience level, culinary specialty, certifications
- **Additional Information**: Culinary philosophy, availability preferences
- **Document Upload**: Resume and optional culinary photos
- **Terms Agreement**: Checkbox for terms and conditions
- **Optional Fields**: Website/portfolio, newsletter signup, background check consent

### Backend Processing
- **Form Validation**: Server-side validation of all required fields
- **File Upload**: Automatic upload of resume and photos to S3
- **Database Storage**: Application data stored in DynamoDB
- **Email Notifications**: Confirmation email to applicant and notification to admin
- **Application Tracking**: Unique application ID generation for tracking

### Application Process
1. Submit Application
2. Document Verification
3. Interview & Assessment
4. Background Check
5. Profile Setup
6. Start Accepting Bookings

## Files Created/Modified

### New Files
- `website/chef-application.html` - Dedicated application page
- `backend/chef_application.py` - Lambda function for processing applications

### Modified Files
- `backend/template.yaml` - Updated with chef application resources

## Technical Implementation

### Frontend Features
- **Modern Design**: Clean, professional interface with responsive design
- **Form Validation**: Client-side validation with clear error messages
- **File Upload**: Drag-and-drop file upload with visual feedback
- **Progress Indicators**: Clear application process visualization
- **Success/Error Handling**: User-friendly feedback for submission results

### Backend Architecture
- **Lambda Function**: Serverless function for processing applications
- **DynamoDB**: Application data storage with proper indexing
- **S3**: File storage for resumes and photos with encryption
- **SES**: Email notifications for applicants and administrators
- **API Gateway**: REST API endpoint for form submission

### Security Features
- **Input Validation**: Comprehensive validation of all form fields
- **File Type Restrictions**: Only allows specific file types and sizes
- **Email Verification**: Validates email format before processing
- **Secure Storage**: Encrypted file storage in S3
- **Access Control**: Proper IAM policies for resource access

## Usage

### For Chefs
1. Visit `chef-application.html` page
2. Fill out the application form completely
3. Upload required documents (resume)
4. Submit the application
5. Receive confirmation email with application ID
6. Wait for review (3-5 business days)

### For Administrators
1. Monitor new applications via email notifications
2. Review applications in the admin panel
3. Contact qualified candidates for interviews
4. Update application status in the database

## API Endpoints

### Submit Application
- **Method**: POST
- **Path**: `/chef-application`
- **Content-Type**: multipart/form-data
- **Response**: JSON with application ID and success message

### Health Check
- **Method**: GET
- **Path**: `/chef-application/health`
- **Response**: JSON with service status

## Environment Variables

The Lambda function requires the following environment variables:
- `CHEF_APPLICATION_TABLE`: DynamoDB table name for applications
- `CHEF_APPLICATION_BUCKET`: S3 bucket name for file uploads
- `FROM_EMAIL`: Email address for sending notifications

## AWS Resources

### DynamoDB Table
- **Table Name**: `{stack-name}-chef-applications`
- **Primary Key**: `applicationId` (String)
- **Indexes**: 
  - `email-index` for email-based lookups
  - `submittedAt-index` for date-based queries

### S3 Bucket
- **Bucket Name**: `maharaja-chef-applications`
- **Structure**: `applications/{applicationId}/resume.pdf` and `applications/{applicationId}/photos/`

### IAM Permissions
- DynamoDB read/write access
- S3 object operations
- SES email sending
- Secrets Manager access (for email configuration)

## Future Enhancements

Potential improvements for the chef application feature:

1. **Application Status Tracking**: Real-time status updates for applicants
2. **Admin Dashboard**: Web interface for managing applications
3. **Document Verification**: Integration with third-party verification services
4. **Interview Scheduling**: Calendar integration for scheduling interviews
5. **Background Check Integration**: Automated background check services
6. **Multi-language Support**: Support for applications in multiple languages
7. **Mobile App**: Dedicated mobile application for chefs

## Testing

To test the chef application feature:

1. **Frontend Testing**:
   - Test form validation with various inputs
   - Verify file upload functionality
   - Check responsive design on different devices
   - Test error handling scenarios

2. **Backend Testing**:
   - Test Lambda function with sample form data
   - Verify DynamoDB storage and retrieval
   - Test S3 file upload and retrieval
   - Check email notification delivery

3. **Integration Testing**:
   - End-to-end application submission
   - Database consistency checks
   - File storage verification
   - Email delivery confirmation

## Deployment

1. Deploy the updated SAM template
2. Configure environment variables in the Lambda function
3. Set up S3 bucket with appropriate permissions
4. Configure SES for email sending
5. Update the frontend API endpoint URL
6. Test the complete application flow

## Support

For issues or questions about the chef application feature:

1. Check the application logs in CloudWatch
2. Verify AWS resource permissions
3. Test individual components (Lambda, DynamoDB, S3, SES)
4. Review frontend console for JavaScript errors
5. Check network connectivity and CORS settings