#!/bin/bash

# Deployment script for the fixed backend

echo "🚀 Starting backend deployment..."

# Change to backend directory
cd backend || { echo "❌ Failed to change to backend directory"; exit 1; }

echo "📁 Changed to backend directory"

# Build the backend
echo "🔨 Building backend..."
sam build || { echo "❌ Build failed"; exit 1; }

echo "✅ Build completed successfully"

# Deploy the backend
echo "🌐 Deploying backend..."
sam deploy --guided || { echo "❌ Deployment failed"; exit 1; }

echo "✅ Deployment completed successfully"

# Return to root directory
cd ..

echo "🎉 Backend deployment completed!"
echo ""
echo "The Decimal serialization issue has been fixed."
echo "The /chefs endpoint should now work correctly and return both static and dynamic chefs."
echo ""
echo "You can test it by:"
echo "1. Opening website/explore-chefs.html"
echo "2. The page will show static chefs immediately"
echo "3. It will fetch dynamic chefs from the API"
echo "4. Both will be displayed together"
