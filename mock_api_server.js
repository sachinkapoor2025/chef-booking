const express = require('express');
const cors = require('cors');
const app = express();
const PORT = 3001;

// Enable CORS
app.use(cors());

// Mock chef data
const mockChefs = [
    {
        chefId: '1',
        name: 'Rajesh Kumar',
        location: 'California',
        cuisine: 'Indian',
        imageUrl: 'images/chef1.jpg',
        description: 'Master of Indian cuisine with 15 years of experience',
        specialties: ['Curry', 'Tandoori', 'Biryani'],
        dietaryTags: ['Vegetarian', 'Vegan', 'Gluten-Free'],
        rating: 4.8,
        reviewCount: 45,
        pricing: [
            {type: 'Dinner Service', price: '$85/hour', note: 'Minimum 2 hours'},
            {type: 'Event Catering', price: '$190/hour', note: 'For parties and gatherings'}
        ],
        menuOptions: {
            'Dinner': ['Butter Chicken with Naan', 'Lamb Rogan Josh', 'Vegetable Biryani'],
            'Events': ['Wedding Reception Package', 'Birthday Party Buffet']
        },
        reviews: [
            {reviewer: 'Sarah M.', stars: '★★★★★', text: 'Amazing chef!'},
            {reviewer: 'Mike R.', stars: '★★★★★', text: 'Perfect for our dinner party'}
        ]
    },
    {
        chefId: '2',
        name: 'Maria Rodriguez',
        location: 'California',
        cuisine: 'Mexican',
        imageUrl: 'images/chef2.jpg',
        description: 'Authentic Mexican cuisine specialist',
        specialties: ['Tacos', 'Enchiladas', 'Guacamole'],
        dietaryTags: ['Vegetarian', 'Gluten-Free'],
        rating: 4.7,
        reviewCount: 38,
        pricing: [
            {type: 'Dinner Service', price: '$75/hour', note: 'Minimum 2 hours'},
            {type: 'Taco Bar Setup', price: '$250', note: 'For 10+ people'}
        ],
        menuOptions: {
            'Dinner': ['Chicken Tacos', 'Beef Enchiladas', 'Vegetarian Fajitas'],
            'Events': ['Mexican Fiesta Package', 'Taco Tuesday Special']
        },
        reviews: [
            {reviewer: 'Anna S.', stars: '★★★★☆', text: 'Innovative and delicious!'},
            {reviewer: 'John D.', stars: '★★★★★', text: 'Best Mexican food Ive had outside Mexico'}
        ]
    },
    {
        chefId: '3',
        name: 'James Chen',
        location: 'California',
        cuisine: 'Asian',
        imageUrl: 'images/chef3.jpg',
        description: 'Fusion Asian cuisine expert',
        specialties: ['Sushi', 'Stir Fry', 'Dim Sum'],
        dietaryTags: ['Vegetarian', 'Vegan', 'Keto'],
        rating: 4.6,
        reviewCount: 27,
        pricing: [
            {type: 'Dinner Service', price: '$90/hour', note: 'Minimum 2 hours'},
            {type: 'Sushi Party', price: '$300', note: 'For 8+ people'}
        ],
        menuOptions: {
            'Dinner': ['Teriyaki Chicken', 'Vegetable Stir Fry', 'Miso Soup'],
            'Events': ['Sushi Rolling Workshop', 'Asian Fusion Buffet']
        },
        reviews: [
            {reviewer: 'Lisa K.', stars: '★★★★★', text: 'The sushi was incredible!'},
            {reviewer: 'Mark T.', stars: '★★★★☆', text: 'Great presentation and taste'}
        ]
    }
];

// GET /chefs - Public endpoint to get all chefs
app.get('/chefs', (req, res) => {
    try {
        res.json(mockChefs);
    } catch (error) {
        console.error('Error fetching chefs:', error);
        res.status(500).json({error: 'Internal server error'});
    }
});

// GET /admin/chefs - Admin endpoint (same as public for now)
app.get('/admin/chefs', (req, res) => {
    try {
        res.json(mockChefs);
    } catch (error) {
        console.error('Error fetching chefs:', error);
        res.status(500).json({error: 'Internal server error'});
    }
});

// POST /admin/chefs - Add a new chef
app.post('/admin/chefs', express.json(), (req, res) => {
    try {
        const {chefData} = req.body;

        if (!chefData) {
            return res.status(400).json({error: 'Missing chef data'});
        }

        // Generate a simple ID
        const chefId = Date.now().toString();
        const newChef = {...chefData, chefId};

        mockChefs.push(newChef);

        res.json({message: 'Chef added successfully'});
    } catch (error) {
        console.error('Error adding chef:', error);
        res.status(500).json({error: 'Internal server error'});
    }
});

app.listen(PORT, () => {
    console.log(`Mock API server running on http://localhost:${PORT}`);
    console.log('Available endpoints:');
    console.log(`  GET  http://localhost:${PORT}/chefs`);
    console.log(`  GET  http://localhost:${PORT}/admin/chefs`);
    console.log(`  POST http://localhost:${PORT}/admin/chefs`);
});
