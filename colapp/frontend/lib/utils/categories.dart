// BLS Consumer Price Index (CPI) Categories - Static Data
// This file contains the complete BLS CPI category hierarchy
// Used by both frontend category picker and LLM parsing

class BLSCategories {
  static const Map<String, dynamic> hierarchy = {
    'Food and Beverages': {
      'Food at home': [
        'Cereals and bakery products',
        'Meats, poultry, fish, and eggs',
        'Dairy and related products',
        'Fruits and vegetables',
        'Nonalcoholic beverages and beverage materials',
        'Other food at home'
      ],
      'Food away from home': [
        'Full service meals and snacks',
        'Limited service meals and snacks',
        'Food at employee sites and schools',
        'Food at elementary and secondary schools',
        'Food from vending machines and mobile vendors',
        'Other food away from home'
      ],
      'Alcoholic beverages': [
        'Beer, ale, and other malt beverages at home',
        'Beer, ale, and other malt beverages away from home',
        'Wine at home',
        'Wine away from home',
        'Distilled spirits at home',
        'Distilled spirits away from home'
      ]
    },
    'Housing': {
      'Shelter': [
        'Rent of primary residence',
        'Lodging away from home',
        'Owners equivalent rent of residences',
        'Tenants and household insurance'
      ],
      'Fuels and utilities': [
        'Fuel oil and other fuels',
        'Gas (piped) and electricity',
        'Water and sewer and trash collection services'
      ],
      'Household furnishings and operations': [
        'Window and floor coverings and other linens',
        'Furniture and bedding',
        'Appliances',
        'Tools, hardware, outdoor equipment and supplies',
        'Housekeeping supplies',
        'Household cleaning products',
        'Paper and plastic products',
        'Miscellaneous household products',
        'Household operations'
      ]
    },
    'Apparel': {
      'Apparel': [
        'Men\'s and boys\' apparel',
        'Women\'s and girls\' apparel',
        'Infants\' and toddlers\' apparel',
        'Footwear',
        'Jewelry and watches'
      ]
    },
    'Transportation': {
      'Private transportation': [
        'New and used motor vehicles',
        'Motor fuel',
        'Motor vehicle parts and equipment',
        'Motor vehicle maintenance and repair',
        'Motor vehicle insurance',
        'Motor vehicle fees'
      ],
      'Public transportation': [
        'Airline fare',
        'Other intercity transportation',
        'Intracity transportation'
      ]
    },
    'Medical Care': {
      'Medical care commodities': [
        'Medicinal drugs',
        'Medical equipment and supplies'
      ],
      'Medical care services': [
        'Professional services',
        'Hospital and related services',
        'Health insurance'
      ]
    },
    'Recreation': {
      'Recreation': [
        'Video and audio',
        'Pets, pet products and services',
        'Sporting goods',
        'Photography',
        'Other recreational goods',
        'Recreation services'
      ]
    },
    'Education and Communication': {
      'Education': [
        'Educational books and supplies',
        'Tuition, other school fees, and childcare',
        'College tuition and fees',
        'Elementary and high school tuition and fees',
        'Child care and nursery school',
        'Technical and business school tuition and fees'
      ],
      'Communication': [
        'Postage and delivery services',
        'Telephone services',
        'Information technology hardware and services'
      ]
    },
    'Other Goods and Services': {
      'Tobacco and smoking products': [
        'Cigarettes',
        'Other tobacco products and smoking accessories'
      ],
      'Personal care': [
        'Hair, dental, shaving and miscellaneous personal care products',
        'Cosmetics, perfume, bath, nail preparations and implements',
        'Personal care services'
      ],
      'Miscellaneous personal services': [
        'Legal services',
        'Funeral expenses',
        'Laundry and dry cleaning services',
        'Apparel services other than laundry and dry cleaning',
        'Financial services',
        'Checking account and other bank services',
        'Tax return preparation and other accounting fees',
        'Miscellaneous personal services'
      ]
    }
  };

  // Get all categories as a flat list for LLM parsing
  static List<String> getAllCategories() {
    List<String> categories = [];
    
    hierarchy.forEach((level1, level2Map) {
      level2Map.forEach((level2, level3List) {
        level3List.forEach((level3) {
          categories.add('$level1 > $level2 > $level3');
        });
      });
    });
    
    return categories;
  }

  // Get category hierarchy for frontend
  static Map<String, dynamic> getHierarchy() {
    return hierarchy;
  }


} 