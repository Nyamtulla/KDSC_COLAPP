import os
import json
import re
import base64
from typing import Dict, List, Optional, Any, Iterator
from PIL import Image
import io
import ollama
from pydantic import BaseModel, Field
import logging
from ocr_service import OCRService



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# BLS categories are now handled by the LLM directly
ALLOWED_CATEGORIES = [
    "Food and Beverages > Food at home > Cereals and bakery products",
    "Food and Beverages > Food at home > Meats, poultry, fish, and eggs",
    "Food and Beverages > Food at home > Dairy and related products",
    "Food and Beverages > Food at home > Fruits and vegetables",
    "Food and Beverages > Food at home > Nonalcoholic beverages and beverage materials",
    "Food and Beverages > Food at home > Other food at home",
    "Food and Beverages > Food away from home > Full service meals and snacks",
    "Food and Beverages > Food away from home > Limited service meals and snacks",
    "Food and Beverages > Food away from home > Food at employee sites and schools",
    "Food and Beverages > Food away from home > Food at elementary and secondary schools",
    "Food and Beverages > Food away from home > Food from vending machines and mobile vendors",
    "Food and Beverages > Food away from home > Other food away from home",
    "Food and Beverages > Alcoholic beverages > Beer, ale, and other malt beverages at home",
    "Food and Beverages > Alcoholic beverages > Beer, ale, and other malt beverages away from home",
    "Food and Beverages > Alcoholic beverages > Wine at home",
    "Food and Beverages > Alcoholic beverages > Wine away from home",
    "Food and Beverages > Alcoholic beverages > Distilled spirits at home",
    "Food and Beverages > Alcoholic beverages > Distilled spirits away from home",
    "Housing > Shelter > Rent of primary residence",
    "Housing > Shelter > Lodging away from home",
    "Housing > Shelter > Owners' equivalent rent of residences",
    "Housing > Shelter > Tenants' and household insurance",
    "Housing > Fuels and utilities > Fuel oil and other fuels",
    "Housing > Fuels and utilities > Gas (piped) and electricity",
    "Housing > Fuels and utilities > Water and sewer and trash collection services",
    "Housing > Household furnishings and operations > Window and floor coverings and other linens",
    "Housing > Household furnishings and operations > Furniture and bedding",
    "Housing > Household furnishings and operations > Appliances",
    "Housing > Household furnishings and operations > Tools, hardware, outdoor equipment and supplies",
    "Housing > Household furnishings and operations > Housekeeping supplies",
    "Housing > Household furnishings and operations > Household cleaning products",
    "Housing > Household furnishings and operations > Paper and plastic products",
    "Housing > Household furnishings and operations > Miscellaneous household products",
    "Housing > Household furnishings and operations > Household operations",
    "Apparel > Men's and boys' apparel > Men's apparel",
    "Apparel > Men's and boys' apparel > Boys' apparel",
    "Apparel > Women's and girls' apparel > Women's apparel",
    "Apparel > Women's and girls' apparel > Girls' apparel",
    "Apparel > Infants' and toddlers' apparel > Infants' apparel",
    "Apparel > Footwear > Men's footwear",
    "Apparel > Footwear > Women's footwear",
    "Apparel > Footwear > Boys' and girls' footwear",
    "Apparel > Jewelry and watches > Jewelry",
    "Apparel > Jewelry and watches > Watches",
    "Transportation > Private transportation > New and used motor vehicles",
    "Transportation > Private transportation > Motor fuel",
    "Transportation > Private transportation > Motor vehicle parts and equipment",
    "Transportation > Private transportation > Motor vehicle maintenance and repair",
    "Transportation > Private transportation > Motor vehicle insurance",
    "Transportation > Private transportation > Motor vehicle fees",
    "Transportation > Public transportation > Airline fare",
    "Transportation > Public transportation > Other intercity transportation",
    "Transportation > Public transportation > Intracity transportation",
    "Medical Care > Medical care commodities > Medicinal drugs",
    "Medical Care > Medical care commodities > Medical equipment and supplies",
    "Medical Care > Medical care services > Professional services",
    "Medical Care > Medical care services > Hospital and related services",
    "Medical Care > Medical care services > Health insurance",
    "Recreation > Video and audio > Televisions",
    "Recreation > Video and audio > Other video equipment",
    "Recreation > Video and audio > Audio equipment",
    "Recreation > Video and audio > Recorded music and music subscriptions",
    "Recreation > Video and audio > Video discs and other media, including rental of video and audio",
    "Recreation > Video and audio > Video subscription services",
    "Recreation > Pets, pet products and services > Pets and pet products",
    "Recreation > Pets, pet products and services > Pet services including veterinary",
    "Recreation > Sporting goods > Sports vehicles including bicycles",
    "Recreation > Sporting goods > Sports equipment",
    "Recreation > Photography > Photographic equipment and supplies",
    "Recreation > Other recreational goods > Toys, games, hobbies and playground equipment",
    "Recreation > Other recreational goods > Sewing machines, fabric and supplies",
    "Recreation > Other recreational goods > Music instruments and accessories",
    "Recreation > Recreation services > Club membership for shopping clubs, fraternal, or other organizations, or participant sports fees",
    "Recreation > Recreation services > Admissions to movies, theaters, and concerts",
    "Recreation > Recreation services > Admissions to sporting events",
    "Recreation > Recreation services > Fees for lessons or instructions",
    "Education and Communication > Education > Educational books and supplies",
    "Education and Communication > Education > Tuition, other school fees, and childcare",
    "Education and Communication > Education > College tuition and fees",
    "Education and Communication > Education > Elementary and high school tuition and fees",
    "Education and Communication > Education > Child care and nursery school",
    "Education and Communication > Education > Technical and business school tuition and fees",
    "Education and Communication > Communication > Postage and delivery services",
    "Education and Communication > Communication > Telephone services",
    "Education and Communication > Communication > Information technology, hardware and services",
    "Other Goods and Services > Tobacco and smoking products > Cigarettes",
    "Other Goods and Services > Tobacco and smoking products > Other tobacco products and smoking accessories",
    "Other Goods and Services > Personal care > Hair, dental, shaving, and miscellaneous personal care products",
    "Other Goods and Services > Personal care > Cosmetics, perfume, bath, nail preparations and implements",
    "Other Goods and Services > Personal care > Personal care services",
    "Other Goods and Services > Miscellaneous personal services > Legal services",
    "Other Goods and Services > Miscellaneous personal services > Funeral expenses",
    "Other Goods and Services > Miscellaneous personal services > Laundry and dry cleaning services",
    "Other Goods and Services > Miscellaneous personal services > Apparel services other than laundry and dry cleaning",
    "Other Goods and Services > Miscellaneous personal services > Financial services",
    "Other Goods and Services > Miscellaneous personal services > Checking account and other bank services",
    "Other Goods and Services > Miscellaneous personal services > Tax return preparation and other accounting fees",
    "Other Goods and Services > Miscellaneous personal services > Miscellaneous personal services"
]

class ReceiptItem(BaseModel):
    """Model for individual receipt items"""
    name: str = Field(description="Product name")
    quantity: float = Field(default=1.0, description="Quantity of the item")
    unit_price: float = Field(description="Price per unit")
    total_price: float = Field(description="Total price for this item")
    category: Optional[str] = Field(default=None, description="Product category")

class ReceiptData(BaseModel):
    """Model for complete receipt data"""
    store_name: str = Field(description="Name of the store")
    date: Optional[str] = Field(default=None, description="Date of purchase")
    time: Optional[str] = Field(default=None, description="Time of purchase")
    items: List[ReceiptItem] = Field(description="List of purchased items")
    subtotal: Optional[float] = Field(default=None, description="Subtotal before tax")
    tax: Optional[float] = Field(default=None, description="Tax amount")
    total: float = Field(description="Total amount paid")
    change: Optional[float] = Field(default=None, description="Change received")
    payment_method: Optional[str] = Field(default=None, description="Payment method used")

class OfflineLLMService:
    """Service for offline LLM-based receipt parsing using Ollama"""
    
    def __init__(self, model_name: str = "qwen2.5:0.5b", host: str = "http://colapp-ollama:11434"):
        """
        Initialize the offline LLM service
        
        Args:
            model_name: Ollama model to use (qwen2.5:0.5b, llama2:7b, mistral:7b, etc.)
            host: Ollama server host
        """
        self.model_name = model_name
        self.host = host
        self.client = ollama.Client(host=host)
        
        # Check if model is available
        self._ensure_model_available()
        
        # System prompt for receipt parsing
        self.system_prompt = self._get_system_prompt()
    
    def _ensure_model_available(self):
        """Ensure the specified model is available in Ollama"""
        try:
            models = self.client.list()
            available_models = [model['name'] for model in models['models']]
            
            if self.model_name not in available_models:
                logger.warning(f"Model {self.model_name} not found. Available models: {available_models}")
                logger.info("You can pull the model using: ollama pull qwen2.5:0.5b")
                # Try to use the first available model
                if available_models:
                    self.model_name = available_models[0]
                    logger.info(f"Using available model: {self.model_name}")
                else:
                    raise Exception("No Ollama models available. Please install a model first.")
        except Exception as e:
            logger.error(f"Error checking Ollama models: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for receipt parsing"""
        return """You are a receipt parsing assistant. Extract products and information from receipts.

IMPORTANT: You MUST respond with valid JSON. Do not include any other text.

RULES:
1. Find ONLY real product names from receipt (skip totals, taxes, discounts)
2. Use 0.0 for missing prices, 1.0 for missing quantities
3. Convert prices to numbers (remove $)
4. Extract store name from first line
5. Look for lines with prices at the end (like "PRODUCT 12.99")
6. Skip lines that are clearly not products (TOTAL, TAX, CHANGE, etc.)
7. Use these BLS categories:
   - Food and Beverages > Food at home > Cereals and bakery products
   - Food and Beverages > Food at home > Meats poultry fish and eggs
   - Food and Beverages > Food at home > Dairy and related products
   - Food and Beverages > Food at home > Fruits and vegetables
   - Food and Beverages > Food at home > Nonalcoholic beverages and beverage materials
   - Food and Beverages > Food at home > Other food at home
   - Food and Beverages > Food away from home > Full service meals and snacks
   - Food and Beverages > Food away from home > Limited service meals and snacks
   - Housing > Household furnishings and operations > Housekeeping supplies
   - Apparel > Mens and boys apparel
   - Apparel > Womens and girls apparel
   - Apparel > Footwear
   - Transportation > Private transportation > Motor fuel
   - Medical Care > Medical care commodities > Medicinal drugs
   - Recreation > Pets pet products and services
   - Other Goods and Services > Personal care > Personal care services

RESPOND WITH THIS JSON FORMAT:
{
  "store_name": "store name",
  "items": [
    {
      "name": "product name",
      "quantity": 1.0,
      "unit_price": price,
      "total_price": price,
      "category": "BLS category path"
    }
  ],
  "total": total_amount
}"""
    
    def parse_receipt_text(self, text: str) -> Dict[str, Any]:
        """
        Parse receipt text using offline LLM
        
        Args:
            text: Raw OCR text from receipt
            
        Returns:
            Dictionary with parsed receipt data
        """
        try:
            # Clean and prepare the text
            cleaned_text = self._preprocess_text(text)
            print("LLM parsed raw OCR text:", cleaned_text)
            
            # Create the prompt
            prompt = f"""Parse this receipt and extract all products:

{cleaned_text}

You must respond with valid JSON containing the store name, all products found, and total amount."""

            # Get response from Ollama with more conservative settings
            try:
                print("Sending request to LLM...")
                response = self.client.chat(
                    model=self.model_name,
                    messages=[
                        {"role": "user", "content": f"{self.system_prompt}\n\n{prompt}"}
                    ],
                    options={
                        "temperature": 0.0,  # Zero temperature for consistent output
                        "top_p": 0.9,
                        "num_predict": 2048,  # Much more tokens for complete response
                        "num_ctx": 4096,     # Much larger context window
                        "repeat_penalty": 1.0, # No repetition penalty
                        "stop": ["```", "```json", "```\n"]  # Stop at code blocks
                    }
                )
                print("LLM response received successfully")
            except Exception as e:
                print(f"LLM call failed: {e}")
                # Return fallback data
                return {
                    'success': True,
                    'data': self._get_fallback_data(),
                    'method': 'offline_llm',
                    'model': self.model_name,
                    'confidence': 0.5
                }
            
            # Extract JSON from response
            print("Processing LLM response...")
            if isinstance(response, Iterator):
                first_message = next(response)
            else:
                first_message = response
            
            print("Response type:", type(response))
            print("First message:", first_message)
            
            content = first_message['message']['content']
            print("LLM raw response:", content)  # Debug the raw response
            
            # Try to extract JSON
            json_str = self._extract_json_from_response(content)
            
            # If no JSON found, try to create a basic structure
            if not json_str or json_str.strip() == '':
                print("No JSON found in response, creating basic structure")
                # Extract store name using the dedicated method
                store_name = self._extract_store_name(cleaned_text)
                
                # Create basic JSON structure
                json_str = f'''{{
                    "store_name": "{store_name}",
                    "items": [],
                    "total": 0.0
                }}'''
            
            # Parse and validate JSON
            try:
                parsed_data = json.loads(json_str)
                print("LLM raw parsed_data:", parsed_data)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                # Try to fix truncated JSON
                try:
                    # If JSON is truncated, try to complete it
                    if json_str.strip().endswith(','):
                        json_str = json_str.rstrip(',') + ']}'
                    elif not json_str.strip().endswith('}'):
                        json_str = json_str.rstrip() + '}'
                    
                    parsed_data = json.loads(json_str)
                    print("Fixed truncated JSON:", parsed_data)
                except:
                    # Create fallback JSON
                    parsed_data = {
                        "store_name": "Unknown Store",
                        "items": [],
                        "total": 0.0
                    }
            
            # Validate against schema
            validated_data = self._validate_and_clean_data(parsed_data)
            print("LLM validated_data:", validated_data)
            
            # Clean up store name to be shorter and more readable
            if validated_data.get('store_name'):
                store_name = validated_data['store_name']
                
                # If store name is too long, it's probably the entire receipt text
                if len(store_name) > 200:
                    # Try to extract just the store name from the beginning
                    lines = store_name.split('\n')
                    for line in lines[:3]:  # Check first 3 lines
                        line = line.strip()
                        if line and len(line) < 100 and not any(skip in line.upper() for skip in ['TOTAL', 'SUBTOTAL', 'TAX', 'CHANGE', 'ITEMS SOLD', 'DATE', 'TIME', 'RECEIPT']):
                            store_name = line
                            break
                    else:
                        # If no good line found, use a generic name
                        store_name = "Unknown Store"
                
                # Extract just the main store name (before any extra details)
                if ',' in store_name:
                    store_name = store_name.split(',')[0]
                if '(' in store_name:
                    store_name = store_name.split('(')[0]
                if ' - ' in store_name:
                    store_name = store_name.split(' - ')[0]
                if 'POS' in store_name:
                    store_name = store_name.split('POS')[0]
                if 'TOTAL' in store_name:
                    store_name = store_name.split('TOTAL')[0]
                
                # Remove extra whitespace and special characters
                store_name = ' '.join(store_name.split())
                store_name = store_name.replace('_', ' ').replace('-', ' ')
                
                # Limit to reasonable length
                if len(store_name) > 100:
                    store_name = store_name[:97] + "..."
                
                validated_data['store_name'] = store_name

            # Clean and filter items
            cleaned_items = []
            for item in validated_data.get('items', []):
                # Skip non-product items
                item_name = item.get('name', '').upper()
                if item_name in ['SUBTOTAL', 'TOTAL', 'TAX', 'CHANGE', 'ITEMS SOLD']:
                    continue
                
                # Fix quantity if it's clearly wrong (e.g., 0.97 should be 1.0)
                quantity = item.get('quantity', 1.0)
                if quantity < 0.1 or quantity > 100:  # Unreasonable quantities
                    quantity = 1.0
                
                # Use LLM's category classification (trust the LLM's judgment)
                category = item.get('category', 'Food and Beverages > Food at home > Other food at home')
                
                # Validate that the category follows the expected format
                if not category or ' > ' not in category:
                    category = 'Food and Beverages > Food at home > Other food at home'
                
                cleaned_items.append({
                    'name': item.get('name', ''),
                    'quantity': quantity,
                    'unit_price': item.get('unit_price', 0.0),
                    'total_price': item.get('total_price', 0.0),
                    'category': category
                })
            
            validated_data['items'] = cleaned_items
            
            return {
                'success': True,
                'data': validated_data,
                'method': 'offline_llm',
                'model': self.model_name,
                'confidence': 0.85  # LLM confidence estimate
            }
            
        except Exception as e:
            logger.error(f"Error parsing receipt with LLM: {e}")
            print("LLM error:", str(e))  # Debug print
            return {
                'success': False,
                'error': str(e),
                'method': 'offline_llm',
                'data': self._get_fallback_data()
            }
    
    def parse_receipt_image(self, image_path: str) -> Dict[str, Any]:
        """
        Parse receipt image using OCR + LLM
        Args:
            image_path: Path to receipt image
        Returns:
            Dictionary with parsed receipt data
        """
        try:
            ocr_service = OCRService()
            ocr_result = ocr_service.extract_text(image_path)
            print("OCR result:", ocr_result)  # Debug print
            if not ocr_result['success']:
                return {
                    'success': False,
                    'error': 'OCR failed to extract text',
                    'method': 'offline_llm'
                }
            return self.parse_receipt_text(ocr_result['text'])
        except Exception as e:
            logger.error(f"Error parsing receipt image: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'offline_llm'
            }
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess OCR text for better LLM parsing"""
        # Remove excessive whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Split into lines and clean each line
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if line and len(line) > 2:  # Only keep meaningful lines
                # Clean up the line but preserve important characters
                line = re.sub(r'[^\w\s\.\,\$\-\+\=\:\;\(\)]', ' ', line)
                line = re.sub(r'\s+', ' ', line).strip()
                if line:
                    lines.append(line)
        
        # Return clean text without line numbers for faster processing
        return '\n'.join(lines)
    
    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON from LLM response with better error handling"""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(0)
                # Try to parse it to validate
                json.loads(json_str)
                return json_str
            
            # If no valid JSON found, try to clean up the response
            cleaned = response.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            
            # Try to fix common JSON issues
            cleaned = self._fix_common_json_issues(cleaned)
            
            # Validate the cleaned JSON
            json.loads(cleaned)
            return cleaned.strip()
                
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed: {e}")
            # Return a minimal valid JSON as fallback
            return self._get_minimal_json_fallback()
    
    def _fix_common_json_issues(self, json_str: str) -> str:
        """Fix common JSON formatting issues from LLM responses"""
        # Remove trailing commas
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Fix unquoted keys
        json_str = re.sub(r'(\w+):', r'"\1":', json_str)
        
        # Fix unquoted string values
        json_str = re.sub(r':\s*([^"\d\[\]{},]+)(?=\s*[,}\]])', r': "\1"', json_str)
        
        # Fix missing quotes around string values
        json_str = re.sub(r':\s*"([^"]*)"([^"]*)"', r': "\1\2"', json_str)
        
        # Ensure the JSON is properly closed
        if json_str.count('{') > json_str.count('}'):
            json_str += '}'
        
        return json_str
    
    def _get_minimal_json_fallback(self) -> str:
        """Return a minimal valid JSON when parsing fails"""
        return '''{
            "store_name": "Unknown Store",
            "date": null,
            "time": null,
            "items": [],
            "subtotal": null,
            "tax": null,
            "total": 0.0,
            "change": null,
            "payment_method": null
        }'''
    
    def _validate_and_clean_data(self, data: Dict) -> Dict:
        """Validate and clean parsed data"""
        try:
            # Ensure required fields exist
            if 'store_name' not in data:
                data['store_name'] = 'Unknown Store'
            
            if 'total' not in data:
                data['total'] = 0.0
            
            if 'items' not in data:
                data['items'] = []
            
            # Ensure items have required fields
            for item in data['items']:
                if 'name' not in item:
                    item['name'] = 'Unknown Item'
                if 'quantity' not in item:
                    item['quantity'] = 1.0
                if 'unit_price' not in item:
                    item['unit_price'] = 0.0
                if 'total_price' not in item:
                    item['total_price'] = item.get('unit_price', 0.0) * item.get('quantity', 1.0)
            
            # Convert monetary values to float
            monetary_fields = ['subtotal', 'tax', 'total', 'change']
            for field in monetary_fields:
                if field in data and data[field] is not None:
                    try:
                        data[field] = float(data[field])
                    except (ValueError, TypeError):
                        data[field] = 0.0
            
            return data
            
        except Exception as e:
            logger.error(f"Error validating data: {e}")
            return self._get_fallback_data()
    
    def _get_fallback_data(self) -> Dict:
        """Get fallback data structure"""
        return {
            'store_name': 'Unknown Store',
            'date': None,
            'time': None,
            'items': [],
            'subtotal': None,
            'tax': None,
            'total': 0.0,
            'change': None,
            'payment_method': None
        }
    

    
    def _extract_store_name(self, text: str) -> str:
        """Extract store name from receipt text"""
        import re
        
        # Common store patterns
        store_patterns = {
            r'WAL\s*MART|WALMART': 'Walmart',
            r'TARGET': 'Target',
            r'KROGER': 'Kroger',
            r'MOMI.*CREPERIE|CREPERIE.*MOMI': 'Momi Creperie',
            r'MCDONALD': 'McDonald\'s',
            r'BURGER\s*KING': 'Burger King',
            r'SUBWAY': 'Subway',
            r'STARBUCKS': 'Starbucks',
            r'COSTCO': 'Costco',
            r'SAFEWAY': 'Safeway',
            r'ALBERTSONS': 'Albertsons',
            r'WHOLE\s*FOODS|WHOLE\s*FOOD': 'Whole Foods',
            r'TRADER\s*JOE': 'Trader Joe\'s',
            r'SPARKY': 'Sparky',
            r'SPAR': 'Spar',
        }
        
        # Check for known store patterns first
        for pattern, store_name in store_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return store_name
        
        # Try to extract from first few lines
        lines = text.split('\n')
        for line in lines[:3]:
            line = line.strip()
            if line and len(line) < 80:
                # Skip lines that are clearly not store names
                if any(skip in line.upper() for skip in ['TOTAL', 'SUBTOTAL', 'TAX', 'CHANGE', 'ITEMS SOLD', 'DATE', 'TIME', 'RECEIPT', 'POS', 'CASH', 'DEBIT', 'CREDIT', 'BILL']):
                    continue
                # Skip lines that are just numbers or prices
                if re.match(r'^[\d\s\.\$]+$', line):
                    continue
                # Clean up the line
                clean_line = re.sub(r'[^\w\s\-\.]', ' ', line)
                clean_line = ' '.join(clean_line.split())
                if clean_line and len(clean_line) < 50:
                    return clean_line
        
        return "Unknown Store"

    def _determine_category(self, product_name: str) -> str:
        """Determine BLS category based on product name keywords"""
        product_upper = product_name.upper()
        
        # Food and Beverages - Food at home
        if any(word in product_upper for word in ['MILK', 'YOGURT', 'CHEESE', 'BUTTER', 'CREAM', 'COTTAGE']):
            return 'Food and Beverages > Food at home > Dairy and related products'
        
        if any(word in product_upper for word in ['APPLE', 'BANANA', 'ORANGE', 'MANGO', 'STRAWBERRY', 'PLUM', 'FRUIT', 'VEGETABLE', 'BEAN']):
            return 'Food and Beverages > Food at home > Fruits and vegetables'
        
        if any(word in product_upper for word in ['BEEF', 'CHICKEN', 'PORK', 'FISH', 'MAHI', 'FILLET', 'MEAT']):
            return 'Food and Beverages > Food at home > Meats, poultry, fish, and eggs'
        
        if any(word in product_upper for word in ['BREAD', 'CEREAL', 'PASTA', 'RICE', 'FLOUR', 'TORTILLA']):
            return 'Food and Beverages > Food at home > Cereals and bakery products'
        
        if any(word in product_upper for word in ['WATER', 'SODA', 'JUICE', 'COFFEE', 'TEA', 'BEVERAGE']):
            return 'Food and Beverages > Food at home > Nonalcoholic beverages and beverage materials'
        
        # Default to other food at home
        return 'Food and Beverages > Food at home > Other food at home'

    def _fallback_parse_receipt(self, text: str) -> Dict[str, Any]:
        """Fallback parsing when LLM times out - use simple regex patterns"""
        try:
            import re
            
            # Extract store name using the dedicated method
            store_name = self._extract_store_name(text)
            
            # Extract total amount
            total_match = re.search(r'TOTAL.*?(\d+\.?\d*)', text, re.IGNORECASE)
            total = float(total_match.group(1)) if total_match else 0.0
            
            # Extract items using improved patterns
            items = []
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or len(line) < 3:
                    continue
                
                # Look for lines with prices at the end
                price_match = re.search(r'(\d+\.?\d*)\s*$', line)
                if price_match:
                    price = float(price_match.group(1))
                    # Extract product name (everything before the price)
                    product_name = line[:-len(price_match.group(0))].strip()
                    
                    # Skip non-product lines
                    if any(skip in product_name.upper() for skip in ['TOTAL', 'SUBTOTAL', 'TAX', 'CHANGE', 'ITEMS SOLD', 'TARE', 'ITEM']):
                        continue
                    
                    # Skip lines that are just numbers or too short
                    if re.match(r'^[\d\s\.\$]+$', product_name) or len(product_name) < 2:
                        continue
                    
                    # Clean up product name
                    product_name = re.sub(r'[^\w\s\-\.]', ' ', product_name)
                    product_name = ' '.join(product_name.split())
                    
                    if product_name and len(product_name) > 2:
                        # Determine category based on product name
                        category = self._determine_category(product_name)
                        
                        items.append({
                            'name': product_name,
                            'quantity': 1.0,
                            'unit_price': price,
                            'total_price': price,
                            'category': category
                        })
            
            # Truncate store name to fit database field
            if len(store_name) > 200:
                store_name = store_name[:197] + "..."
            
            return {
                'success': True,
                'data': {
                    'store_name': store_name,
                    'date': None,
                    'time': None,
                    'items': items,
                    'subtotal': None,
                    'tax': None,
                    'total': total,
                    'change': None,
                    'payment_method': None
                },
                'method': 'fallback_regex',
                'confidence': 0.6
            }
            
        except Exception as e:
            logger.error(f"Fallback parsing failed: {e}")
            return {
                'success': False,
                'error': f'Fallback parsing failed: {str(e)}',
                'method': 'fallback_regex',
                'data': self._get_fallback_data()
            }

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        try:
            models = self.client.list()
            current_model = next(
                (model for model in models['models'] if model['name'] == self.model_name),
                None
            )
            
            return {
                'model_name': self.model_name,
                'available_models': [model['name'] for model in models['models']],
                'current_model_info': current_model
            }
        except Exception as e:
            return {
                'error': str(e),
                'model_name': self.model_name
            } 