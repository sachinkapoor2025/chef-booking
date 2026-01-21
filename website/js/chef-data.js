/**
 * Unified Chef Data Management
 * Combines static chef profiles with dynamic DynamoDB data
 */

// Static chef data extracted from profile pages
const STATIC_CHEFS = [
    {
        chefId: 'static-rajesh',
        name: 'Rajesh Kumar',
        location: 'San Jose, California',
        cuisine: 'Indian',
        imageUrl: 'images/chef1.jpg',
        profileUrl: 'chef-profile-rajesh.html',
        description: 'With over 12 years of experience in professional kitchens, Rajesh brings authentic Indian flavors to your home. He specializes in traditional and fusion Indian cuisine, ensuring every dish is prepared with the freshest ingredients and authentic spices.',
        specialties: ['Traditional Indian Cuisine', 'Fusion Indian-American', 'Vegetarian and Vegan Indian', 'Regional Indian specialties'],
        dietaryTags: ['Vegetarian', 'Vegan', 'Gluten-Free', 'Dairy-Free'],
        rating: 4.8,
        reviewCount: 127,
        pricing: [
            {type: 'Dinner Service', price: '$75/hour', note: 'Minimum 2 hours'},
            {type: 'Event Catering', price: '$150/hour', note: 'For parties and gatherings'},
            {type: 'Weekly Meal Prep', price: '$50/hour', note: 'Plus ingredient costs'}
        ],
        menuOptions: {
            'Dinner': ['Butter Chicken with Naan', 'Lamb Rogan Josh', 'Paneer Tikka Masala', 'Biryani Feast'],
            'Events': ['Wedding Reception Package', 'Birthday Party Buffet', 'Holiday Dinner Special', 'Corporate Lunch']
        },
        reviews: [
            {reviewer: 'Sarah M.', stars: '★★★★★', text: 'Rajesh made our Diwali dinner unforgettable! The flavors were authentic and the presentation was beautiful.'},
            {reviewer: 'Mike R.', stars: '★★★★★', text: 'Amazing chef! The butter chicken was the best Ive ever had. Will definitely book again.'},
            {reviewer: 'Jennifer L.', stars: '★★★★☆', text: 'Great service and delicious food. The spices were perfectly balanced for our taste.'}
        ]
    },
    {
        chefId: 'static-maria',
        name: 'Maria Rodriguez',
        location: 'Los Angeles, California',
        cuisine: 'Italian',
        imageUrl: 'images/chef2.jpg',
        profileUrl: 'chef-profile-maria.html',
        description: 'Maria brings 15 years of culinary expertise from top restaurants in California and Italy. Her passion for fresh, seasonal ingredients and traditional cooking techniques creates unforgettable Mediterranean and Italian dining experiences.',
        specialties: ['Authentic Italian Cuisine', 'Mediterranean Fusion', 'California Coastal Cuisine', 'Wood-fired specialties'],
        dietaryTags: ['Gluten-Free', 'Keto', 'Dairy-Free', 'Low-Carb'],
        rating: 4.9,
        reviewCount: 89,
        pricing: [
            {type: 'Dinner Service', price: '$85/hour', note: 'Minimum 2 hours'},
            {type: 'Event Catering', price: '$175/hour', note: 'For parties and gatherings'},
            {type: 'Weekly Meal Prep', price: '$60/hour', note: 'Plus ingredient costs'}
        ],
        menuOptions: {
            'Dinner': ['Osso Buco alla Milanese', 'Grilled Branzino with Herbs', 'Homemade Pasta Carbonara', 'Lamb Tagine'],
            'Events': ['Italian Wedding Feast', 'Mediterranean Buffet', 'Holiday Antipasto Spread', 'Corporate Italian Lunch']
        },
        reviews: [
            {reviewer: 'David K.', stars: '★★★★★', text: 'Marias Italian cooking is absolutely authentic! Felt like I was back in Tuscany. Incredible flavors!'},
            {reviewer: 'Lisa P.', stars: '★★★★★', text: 'Perfect for our anniversary dinner. The presentation was beautiful and every bite was delicious.'},
            {reviewer: 'Robert M.', stars: '★★★★☆', text: 'Outstanding chef! The pasta was made fresh and the seafood was perfectly cooked.'}
        ]
    },
    {
        chefId: 'static-james',
        name: 'James Chen',
        location: 'San Francisco, California',
        cuisine: 'Asian',
        imageUrl: 'images/chef3.jpg',
        profileUrl: 'chef-profile-james.html',
        description: 'James brings 10 years of experience from Michelin-starred restaurants in San Francisco and Tokyo. His innovative approach to Asian fusion cuisine combines traditional techniques with modern presentation, creating visually stunning and delicious dishes.',
        specialties: ['Japanese Cuisine', 'Asian Fusion', 'Sushi Mastery', 'Wok Cooking'],
        dietaryTags: ['Vegetarian', 'Vegan', 'Gluten-Free', 'Keto'],
        rating: 4.7,
        reviewCount: 67,
        pricing: [
            {type: 'Dinner Service', price: '$90/hour', note: 'Minimum 2 hours'},
            {type: 'Event Catering', price: '$180/hour', note: 'For parties and gatherings'},
            {type: 'Sushi Party', price: '$250', note: 'For 8+ people, includes sushi rolling demonstration'}
        ],
        menuOptions: {
            'Dinner': ['Miso-Glazed Black Cod', 'Thai Green Curry', 'Szechuan Beef', 'Vegetable Tempura'],
            'Events': ['Sushi & Sashimi Platter', 'Asian Fusion Buffet', 'Dim Sum Banquet', 'Ramen Bar']
        },
        reviews: [
            {reviewer: 'Emily T.', stars: '★★★★★', text: 'The sushi was incredible! James not only prepared amazing food but also taught us how to make our own rolls.'},
            {reviewer: 'Michael S.', stars: '★★★★★', text: 'Best Asian food Ive had outside of Japan. The presentation was like a work of art.'},
            {reviewer: 'Sophia L.', stars: '★★★★☆', text: 'Delicious and creative dishes. The green curry was perfectly balanced.'}
        ]
    }
];

/**
 * Fetch chefs from DynamoDB via API
 */
async function fetchDynamicChefs() {
    const API_URLS = [
        'https://fated6vcp8.execute-api.us-east-1.amazonaws.com/prod',
        'http://localhost:3001'
    ];

    for (const url of API_URLS) {
        try {
            const response = await fetch(`${url}/chefs`);
            if (response.ok) {
                const chefs = await response.json();
                console.log(`Successfully fetched ${chefs.length} dynamic chefs from ${url}`);
                return chefs;
            }
        } catch (error) {
            console.log(`Failed to fetch from ${url}, trying next:`, error.message);
        }
    }

    console.warn('All API endpoints failed, no dynamic chefs loaded');
    return [];
}

/**
 * Combine static and dynamic chef data
 */
async function getAllChefs() {
    // Start with static chefs
    let allChefs = [...STATIC_CHEFS];

    // Fetch and add dynamic chefs
    const dynamicChefs = await fetchDynamicChefs();

    // Add dynamic chefs to the list
    if (dynamicChefs.length > 0) {
        allChefs = allChefs.concat(dynamicChefs);
        console.log(`Combined ${STATIC_CHEFS.length} static chefs with ${dynamicChefs.length} dynamic chefs`);
    } else {
        console.log(`Using ${STATIC_CHEFS.length} static chefs (no dynamic chefs available)`);
    }

    return allChefs;
}

/**
 * Convert chef data to card format for explore page
 */
function createChefCard(chef) {
    const chefCard = document.createElement('div');
    chefCard.className = 'chef-card';

    // Set data attributes for filtering
    chefCard.setAttribute('data-location', chef.location.toLowerCase());
    chefCard.setAttribute('data-cuisine', chef.cuisine.toLowerCase());

    // Extract dietary tags for filtering
    const dietaryTags = chef.dietaryTags ? chef.dietaryTags.map(tag =>
        tag.toLowerCase().replace(/\s+/g, '-')
    ) : [];
    chefCard.setAttribute('data-diet', dietaryTags.join(','));

    // Create card HTML
    chefCard.innerHTML = `
        <img src="${chef.imageUrl || 'images/chef1.jpg'}" alt="${chef.name}">
        <h3>${chef.name}</h3>
        <p class="chef-location">${chef.location}</p>
        <div class="chef-rating">
            <span class="stars">★★★★★</span>
            <span class="rating-text">${chef.rating || 4.5} (${chef.reviewCount || 'New'})</span>
        </div>
        <a href="${chef.profileUrl || 'book-a-chef.html'}" class="btn">View Profile</a>
        <a href="book-a-chef.html" class="btn btn-secondary">Book Now</a>
    `;

    return chefCard;
}

/**
 * Display chefs on the explore page
 */
async function displayChefsOnExplorePage() {
    const chefs = await getAllChefs();
    const chefCardsContainer = document.querySelector('.chef-cards');
    const noResults = document.getElementById('no-results');

    if (!chefCardsContainer) {
        console.error('Chef cards container not found');
        return;
    }

    // Clear existing chef cards
    chefCardsContainer.innerHTML = '';

    if (chefs.length === 0) {
        noResults.style.display = 'block';
        chefCardsContainer.style.display = 'none';
        return;
    }

    // Add each chef to the container
    chefs.forEach(chef => {
        const chefCard = createChefCard(chef);
        chefCardsContainer.appendChild(chefCard);
    });

    noResults.style.display = 'none';
    chefCardsContainer.style.display = 'grid';

    return chefs;
}

/**
 * Filter chefs based on search criteria
 */
function filterChefs(allChefs, criteria) {
    return allChefs.filter(chef => {
        let matches = true;

        // Location filter
        if (criteria.location && criteria.location !== '') {
            const chefLocation = chef.location.toLowerCase();
            const validLocations = ['california', 'ca', 'san jose', 'san francisco', 'los angeles', 'la', 'sacramento', 'fresno', 'bakersfield'];
            if (!validLocations.some(loc => loc.includes(criteria.location) || criteria.location.includes(loc))) {
                matches = false;
            }
        }

        // Cuisine filter
        if (criteria.cuisine && criteria.cuisine !== '') {
            if (chef.cuisine.toLowerCase() !== criteria.cuisine.toLowerCase()) {
                matches = false;
            }
        }

        // Dietary filter
        if (criteria.dietary && criteria.dietary !== '') {
            const chefDiet = chef.dietaryTags ? chef.dietaryTags.join(',').toLowerCase() : '';
            if (!chefDiet.includes(criteria.dietary.toLowerCase())) {
                matches = false;
            }
        }

        return matches;
    });
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        STATIC_CHEFS,
        fetchDynamicChefs,
        getAllChefs,
        createChefCard,
        displayChefsOnExplorePage,
        filterChefs
    };
}
