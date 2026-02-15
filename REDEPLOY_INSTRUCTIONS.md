# Backend Redeployment Instructions

## Problem
The diet plan form is still showing the error:
```
Failed to start diet plan generation: An error occurred (AccessDeniedException) when calling the Invoke operation: User: arn:aws:sts::985539754737:assumed-role/demo-chef-services-backend-DietPlanFunctionRole-IYbVKrVaeQNV/demo-chef-services-backend-diet-plan is not authorized to perform: lambda:InvokeFunction on resource: arn:aws:lambda:us-east-1:985539754737:function:chef-services-backend-diet-plan-worker because no identity-based policy allows the lambda:InvokeFunction action
```

## Solution
The IAM permissions have been fixed in the CloudFormation template, but the changes need to be deployed to your AWS environment.

## Steps to Redeploy

### 1. Navigate to the Backend Directory
```bash
cd backend
```

### 2. Redeploy the Backend
Run the following command to redeploy your backend with the updated IAM permissions:

```bash
sam deploy --guided
```

### 3. Follow the SAM Deployment Prompts
When you run the command, SAM will prompt you for several configuration options:

1. **Stack Name**: Press Enter to use the default `chef-services-backend`
2. **AWS Region**: Press Enter to use your default region (should be `us-east-1`)
3. **Confirm changes before deploy**: Type `Y` and press Enter
4. **Allow SAM CLI IAM role creation**: Type `Y` and press Enter
5. **Save arguments to configuration file**: Type `Y` and press Enter

### 4. Wait for Deployment
The deployment will take 2-5 minutes. You'll see output similar to:
```
Deploying with following values
===============================
Stack name                 : chef-services-backend
Region                     : us-east-1
Confirm changeset          : True
Disable rollback           : False
Deployment s3 bucket       : aws-sam-cli-managed-default-samclisourcebucket-xxxxxx
Capabilities               : ["CAPABILITY_IAM"]
Parameter overrides        : {}

Initiating deployment
=====================
Uploading to chef-services-backend/2026/02/06/12/34/56/xxxxxxxxxx.zip
...
CloudFormation events from stack operations
...
Successfully created/updated stack - chef-services-backend
```

### 5. Verify Deployment
After deployment completes, you should see:
```
Successfully created/updated stack - chef-services-backend
```

## Alternative: Quick Deploy (if you've deployed before)
If you've deployed this stack before and just want to update it quickly:

```bash
sam deploy
```

This will use your previous deployment configuration and just update the stack.

## After Redeployment
Once the deployment is complete:

1. **Wait 2-3 minutes** for AWS to fully apply the IAM role changes
2. **Test the diet plan form** again at `website/diet-plan.html`
3. The form should now work without the permission error

## Verification
You can verify the deployment was successful by:

1. **Check CloudFormation Console**: Go to AWS CloudFormation console and verify the stack status is `UPDATE_COMPLETE`
2. **Check Lambda Console**: Verify the `chef-services-backend-diet-plan` function has the updated IAM role with `lambda:InvokeFunction` permissions
3. **Test the form**: Try submitting the diet plan form again

## Troubleshooting
If you encounter issues:

1. **Check AWS CLI credentials**: Ensure your AWS CLI is configured with the correct credentials
2. **Check permissions**: Ensure your AWS user has permissions to deploy CloudFormation stacks
3. **Check SAM CLI**: Ensure SAM CLI is installed and working
4. **Check internet connection**: Ensure stable internet connection during deployment

## Contact
If you continue to experience issues after redeployment, please provide:
- The exact error message from the SAM deployment
- Your AWS region
- Whether this is your first deployment or an update to an existing stack