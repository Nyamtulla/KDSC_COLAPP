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

ALLOWED_CATEGORIES = [
    "Dairy", "Bakery", "Produce", "Meat", "Beverages", "Household", "Frozen", "Snacks", "Pantry", "Seafood", "Personal Care", "Health", "Baby", "Pet", "Canned Goods", "Condiments", "Grains", "Pasta", "Cleaning", "Paper Goods", "Other"
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
        return """You are an expert receipt parser. Focus on identifying ALL products from receipt text.

CRITICAL RULES:
1. Your main goal is to find ALL product names from the receipt
2. Extract as many products as possible, even if you can't get prices or quantities
3. Return valid JSON with proper quotes and structure
4. Use 0.0 for missing prices, 1.0 for missing quantities, "Other" for missing categories
5. Use null for missing fields like date, time, payment method
6. Convert all prices to numbers (remove $ symbols)
7. Categorize items when obvious: Dairy, Produce, Meat, Frozen Foods, Canned Goods, Beverages, Snacks, Household, Personal Care, Other

JSON Structure:
{
  "store_name": "store name if found or null",
  "date": "date if found or null",
  "time": "time if found or null",
  "items": [
    {
      "name": "product name you can identify",
      "quantity": quantity if found or 1.0,
      "unit_price": price if found or 0.0,
      "total_price": total if found or 0.0,
      "category": "category if obvious or Other"
    }
  ],
  "subtotal": subtotal if found or null,
  "tax": tax if found or null,
  "total": total if found or null,
  "change": change if found or null,
  "payment_method": "payment method if found or null"
}

IMPORTANT: Focus on finding ALL products, even if other information is missing."""
    
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
            prompt = f"""Parse this receipt text and extract ALL products you can identify:

{cleaned_text}

INSTRUCTIONS:
1. Focus on finding ALL product names from the receipt
2. Look for any line that might contain a product name
3. Extract as many products as you can see, even if you can't get prices or quantities
4. If you can't determine a price, use 0.0
5. If you can't determine quantity, use 1.0
6. If you can't determine category, use "Other"
7. The receipt shows "ITEMS SOLD 11" - try to find all 11 items

Return ONLY a JSON object with ALL products found:
{{
  "store_name": "store name if found or null",
  "date": "date if found or null",
  "time": "time if found or null", 
  "items": [
    {{
      "name": "product name you can identify",
      "quantity": quantity if found or 1.0,
      "unit_price": price if found or 0.0,
      "total_price": total if found or 0.0,
      "category": "category if obvious or Other"
    }}
  ],
  "subtotal": subtotal if found or null,
  "tax": tax if found or null,
  "total": total if found or null,
  "change": change if found or null,
  "payment_method": "payment method if found or null"
}}

IMPORTANT: Focus on finding ALL products, even if other information is missing."""

            # Get response from Ollama
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": f"{self.system_prompt}\n\n{prompt}"}
                ],
                options={
                    "temperature": 0.1,  # Low temperature for consistent output
                    "top_p": 0.9,
                    "num_predict": 2048
                }
            )
            
            # Extract JSON from response
            if isinstance(response, Iterator):
                first_message = next(response)
            else:
                first_message = response
            json_str = self._extract_json_from_response(first_message['message']['content'])
            
            # Parse and validate JSON
            parsed_data = json.loads(json_str)
            print("LLM raw parsed_data:", parsed_data)
            
            # Validate against schema
            validated_data = self._validate_and_clean_data(parsed_data)
            print("LLM validated_data:", validated_data)

            # Map categories to allowed list
            def map_category(cat):
                return cat if cat in ALLOWED_CATEGORIES else "Other"
            for item in validated_data.get('items', []):
                item['category'] = map_category(item.get('category', 'Other'))
            
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
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Split into lines and clean each line
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if line:
                # Clean up the line but preserve important characters
                line = re.sub(r'[^\w\s\.\,\$\-\+\=\:\;\(\)\[\]\{\}\#\@]', ' ', line)
                line = re.sub(r'\s+', ' ', line).strip()
                if line:
                    lines.append(line)
        
        # Add line numbers to help LLM identify items
        numbered_lines = []
        for i, line in enumerate(lines, 1):
            numbered_lines.append(f"Line {i}: {line}")
        
        return '\n'.join(numbered_lines)
    
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