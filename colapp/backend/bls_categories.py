"""
BLS Consumer Price Index Categories for Expenditure Tracking
Based on Bureau of Labor Statistics CPI categories
"""

BLS_CATEGORIES = {
    "Food and Beverages": {
        "Food at home": [
            "Cereals and bakery products",
            "Meats, poultry, fish, and eggs",
            "Dairy and related products",
            "Fruits and vegetables",
            "Nonalcoholic beverages and beverage materials",
            "Other food at home"
        ],
        "Food away from home": [
            "Full service meals and snacks",
            "Limited service meals and snacks",
            "Food at employee sites and schools",
            "Food at elementary and secondary schools",
            "Food from vending machines and mobile vendors",
            "Other food away from home"
        ],
        "Alcoholic beverages": [
            "Beer, ale, and other malt beverages at home",
            "Beer, ale, and other malt beverages away from home",
            "Wine at home",
            "Wine away from home",
            "Distilled spirits at home",
            "Distilled spirits away from home"
        ]
    },
    "Housing": {
        "Shelter": [
            "Rent of primary residence",
            "Lodging away from home",
            "Owners' equivalent rent of residences",
            "Tenants' and household insurance"
        ],
        "Fuels and utilities": [
            "Fuel oil and other fuels",
            "Gas (piped) and electricity",
            "Water and sewer and trash collection services"
        ],
        "Household furnishings and operations": [
            "Window and floor coverings and other linens",
            "Furniture and bedding",
            "Appliances",
            "Tools, hardware, outdoor equipment and supplies",
            "Housekeeping supplies",
            "Household cleaning products",
            "Paper and plastic products",
            "Miscellaneous household products",
            "Household operations"
        ]
    },
    "Apparel": {
        "Men's and boys' apparel": [
            "Men's apparel",
            "Boys' apparel"
        ],
        "Women's and girls' apparel": [
            "Women's apparel",
            "Girls' apparel"
        ],
        "Infants' and toddlers' apparel": [
            "Infants' apparel"
        ],
        "Footwear": [
            "Men's footwear",
            "Women's footwear",
            "Boys' and girls' footwear"
        ],
        "Jewelry and watches": [
            "Jewelry",
            "Watches"
        ]
    },
    "Transportation": {
        "Private transportation": [
            "New and used motor vehicles",
            "Motor fuel",
            "Motor vehicle parts and equipment",
            "Motor vehicle maintenance and repair",
            "Motor vehicle insurance",
            "Motor vehicle fees"
        ],
        "Public transportation": [
            "Airline fare",
            "Other intercity transportation",
            "Intracity transportation"
        ]
    },
    "Medical Care": {
        "Medical care commodities": [
            "Medicinal drugs",
            "Medical equipment and supplies"
        ],
        "Medical care services": [
            "Professional services",
            "Hospital and related services",
            "Health insurance"
        ]
    },
    "Recreation": {
        "Video and audio": [
            "Televisions",
            "Other video equipment",
            "Audio equipment",
            "Recorded music and music subscriptions",
            "Video discs and other media, including rental of video and audio",
            "Video subscription services"
        ],
        "Pets, pet products and services": [
            "Pets and pet products",
            "Pet services including veterinary"
        ],
        "Sporting goods": [
            "Sports vehicles including bicycles",
            "Sports equipment"
        ],
        "Photography": [
            "Photographic equipment and supplies"
        ],
        "Other recreational goods": [
            "Toys, games, hobbies and playground equipment",
            "Sewing machines, fabric and supplies",
            "Music instruments and accessories"
        ],
        "Recreation services": [
            "Club membership for shopping clubs, fraternal, or other organizations, or participant sports fees",
            "Admissions to movies, theaters, and concerts",
            "Admissions to sporting events",
            "Fees for lessons or instructions"
        ]
    },
    "Education and Communication": {
        "Education": [
            "Educational books and supplies",
            "Tuition, other school fees, and childcare",
            "College tuition and fees",
            "Elementary and high school tuition and fees",
            "Child care and nursery school",
            "Technical and business school tuition and fees"
        ],
        "Communication": [
            "Postage and delivery services",
            "Telephone services",
            "Information technology, hardware and services"
        ]
    },
    "Other Goods and Services": {
        "Tobacco and smoking products": [
            "Cigarettes",
            "Other tobacco products and smoking accessories"
        ],
        "Personal care": [
            "Hair, dental, shaving, and miscellaneous personal care products",
            "Cosmetics, perfume, bath, nail preparations and implements",
            "Personal care services"
        ],
        "Miscellaneous personal services": [
            "Legal services",
            "Funeral expenses",
            "Laundry and dry cleaning services",
            "Apparel services other than laundry and dry cleaning",
            "Financial services",
            "Checking account and other bank services",
            "Tax return preparation and other accounting fees",
            "Miscellaneous personal services"
        ]
    }
}

def get_all_categories():
    """Get all categories in a flat list for easy selection"""
    categories = []
    for main_category, subcategories in BLS_CATEGORIES.items():
        for subcategory, items in subcategories.items():
            for item in items:
                categories.append({
                    'main_category': main_category,
                    'subcategory': subcategory,
                    'item': item,
                    'full_path': f"{main_category} > {subcategory} > {item}"
                })
    return categories

def find_category_by_keywords(product_name):
    """Find the most appropriate category based on product name keywords"""
    product_upper = product_name.upper()
    
    # Food and Beverages
    if any(word in product_upper for word in ['MILK', 'YOGURT', 'CHEESE', 'BUTTER', 'CREAM', 'DAN']):
        return "Food and Beverages", "Food at home", "Dairy and related products"
    
    if any(word in product_upper for word in ['MANGO', 'ONION', 'TOMATO', 'WATERMELON', 'CANTALOUPE', 'GUAVA', 'APPLE', 'BANANA']):
        return "Food and Beverages", "Food at home", "Fruits and vegetables"
    
    if any(word in product_upper for word in ['BEEF', 'CHICKEN', 'PORK', 'FISH', 'MEAT', 'HAM', 'BACON']):
        return "Food and Beverages", "Food at home", "Meats, poultry, fish, and eggs"
    
    if any(word in product_upper for word in ['BREAD', 'CEREAL', 'PASTA', 'RICE', 'FLOUR']):
        return "Food and Beverages", "Food at home", "Cereals and bakery products"
    
    if any(word in product_upper for word in ['WATER', 'SODA', 'JUICE', 'COFFEE', 'TEA']):
        return "Food and Beverages", "Food at home", "Nonalcoholic beverages and beverage materials"
    
    if any(word in product_upper for word in ['BEER', 'WINE', 'ALCOHOL']):
        return "Food and Beverages", "Alcoholic beverages", "Beer, ale, and other malt beverages at home"
    
    # Personal Care
    if any(word in product_upper for word in ['LAVENDER', 'SHAMPOO', 'SOAP', 'TOOTHPASTE', 'DEODORANT']):
        return "Other Goods and Services", "Personal care", "Hair, dental, shaving, and miscellaneous personal care products"
    
    # Household
    if any(word in product_upper for word in ['DETERGENT', 'CLEANER', 'PAPER', 'TOWEL', 'TISSUE']):
        return "Housing", "Household furnishings and operations", "Housekeeping supplies"
    
    # Default
    return "Food and Beverages", "Food at home", "Other food at home"

def get_category_hierarchy():
    """Get the full category hierarchy for frontend display"""
    return BLS_CATEGORIES 