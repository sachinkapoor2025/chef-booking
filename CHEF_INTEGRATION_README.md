# Chef Integration Implementation

## Overview

This implementation enables dynamic chef listing on the explore chefs page, fetching data from DynamoDB through a backend API. The solution includes backend enhancements, frontend integration, and robust fallback mechanisms.

## Files Modified/Created

### Backend Changes

1. **`backend/src/admin.py`**
   - Added public `/chefs` GET endpoint to fetch chefs for public consumption
   - The endpoint uses the same `get_chefs()` function as the admin endpoint

2. **`backend/template.yaml`**
   - Added API Gateway configuration for the public `/chefs` endpoint
   - Configured to use the same Lambda function as admin endpoints

### Frontend Changes

1. **`website/explore-chefs.html`**
   - Added JavaScript to fetch chef data dynamically from the backend
   - Implemented robust fallback mechanism with multiple API endpoints
   - Maintained all existing filtering functionality
   - Added static fallback data for when APIs are unavailable

### Testing & Development Tools

1. **`test_chef_integration.html`**
   - Comprehensive test suite for API functionality
   - Tests chef fetching, adding, and display functionality
   - Uses mock API for local testing

2. **`mock_api_server.js`**
   - Local Express.js server for testing without AWS dependencies
   - Provides mock chef data and API endpoints
   - Useful for development and debugging

## How It Works

### Data Flow

1. **Chef Addition (Admin)**
   - Admin adds chef via `/admin/chef.html`
   - Data is POSTed to `/admin/chefs` endpoint
   - Chef data is stored in DynamoDB `ChefTable`

2. **Chef Listing (Public)**
   - User visits `/explore-chefs.html`
   - Page fetches chefs from `/chefs` endpoint
   - JavaScript dynamically creates chef cards
   - Users can filter by location, cuisine, and dietary preferences

### Fallback Mechanism

The implementation includes a robust fallback system:

1. **Primary API**: Production AWS endpoint
2. **Secondary API**: Local mock server (for development)
3. **Static Fallback**: Original static chef data

If all APIs fail, the page gracefully falls back to static data.

## Setup Instructions

### For Development/Testing

1. **Install Node.js dependencies** (if not already installed):
   ```bash
   npm install express cors
   ```

2. **Start the mock API server**:
   ```bash
   node mock_api_server.js
   ```
   This will start a server on `http://localhost:3001`

3. **Test the integration**:
   - Open `test_chef_integration.html` in your browser
   - Click the test buttons to verify functionality
   - The test page uses the mock API by default

### For Production

1. **Deploy the backend**:
   - The backend changes are already implemented in `backend/src/admin.py` and `backend/template.yaml`
   - Deploy using AWS SAM:
   ```bash
   cd backend
   sam build
   sam deploy
   ```

2. **Update API URL** (if needed):
   - In `website/explore-chefs.html`, update the `API_URLS` array with your production endpoint
   - The first URL in the array is used as the primary endpoint

## Troubleshooting

### Common Issues

1. **500 Error from Production API**:
   - Check if the backend is properly deployed
   - Verify the API Gateway endpoint is correct
   - Check CloudWatch logs for Lambda errors
   - Ensure DynamoDB table exists and has proper permissions

2. **CORS Issues**:
   - The backend includes CORS headers in all responses
   - If testing locally, use the mock server or configure CORS properly

3. **Fallback Not Working**:
   - Check browser console for errors
   - Verify the fallback data structure matches expected format
   - Ensure the `API_URLS` array has valid endpoints

## API Endpoints

### Public Endpoints

- **GET `/chefs`**: Fetch all chefs (public access)
- **GET `/admin/chefs`**: Fetch all chefs (admin access, same data)

### Admin Endpoints

- **POST `/admin/chefs`**: Add a new chef (requires admin authentication)
- **GET `/admin/chefs`**: Fetch all chefs (admin access)

## Data Structure

### Chef Object

```javascript
{
  chefId: string,
  name: string,
  location: string,
  cuisine: string,
  imageUrl: string,
  description: string,
  specialties: string[],
  dietaryTags: string[],
  rating: number,
  reviewCount: number,
  pricing: Array<{
    type: string,
    price: string,
    note: string
  }>,
  menuOptions: {
    [category: string]: string[]
  },
  reviews: Array<{
    reviewer: string,
    stars: string,
    text: string
  }>
}
```

## Filtering Logic

The filtering works with three criteria:

1. **Location**: Matches against California cities and regions
2. **Cuisine**: Exact match on cuisine type
3. **Dietary**: Checks if dietary tags include the selected option

All filters are applied simultaneously (AND logic).

## Future Enhancements

1. **Pagination**: Add pagination for large chef lists
2. **Advanced Search**: Implement full-text search
3. **Chef Details**: Create dynamic chef profile pages
4. **Caching**: Implement client-side caching for better performance
5. **Real-time Updates**: Add WebSocket support for live updates

## Support

For issues or questions, please refer to the main project documentation or contact the development team.
