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
    
    def __init__(self, model_name: str = "llama2:7b", host: str = "http://host.docker.internal:11434"):
        """
        Initialize the offline LLM service
        
        Args:
            model_name: Ollama model to use (llama2:7b, mistral:7b, etc.)
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
                logger.info("You can pull the model using: ollama pull llama2:7b")
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
        return """You are an expert receipt parser. Your task is to extract structured information from receipt text and return it as valid JSON.

IMPORTANT RULES:
1. Always return valid JSON that matches the ReceiptData schema
2. Extract store name from the header/top of receipt
3. Parse each line that contains product information into items
4. Identify quantities, unit prices, and total prices for each item
5. Extract subtotal, tax, and total amounts
6. Look for date/time information
7. Handle missing information gracefully (use null for missing fields)
8. Ensure all monetary values are numeric (no currency symbols)
9. Categorize items when possible (Dairy, Produce, Meat, etc.)

ReceiptData Schema:
{
  "store_name": "string",
  "date": "string (YYYY-MM-DD format)",
  "time": "string (HH:MM format)",
  "items": [
    {
      "name": "string",
      "quantity": "number",
      "unit_price": "number",
      "total_price": "number",
      "category": "string (optional)"
    }
  ],
  "subtotal": "number (optional)",
  "tax": "number (optional)",
  "total": "number",
  "change": "number (optional)",
  "payment_method": "string (optional)"
}

Example output:
{
  "store_name": "Walmart Supercenter",
  "date": "2024-01-15",
  "time": "14:30",
  "items": [
    {
      "name": "Milk 2% 1 Gallon",
      "quantity": 1,
      "unit_price": 3.99,
      "total_price": 3.99,
      "category": "Dairy"
    }
  ],
  "subtotal": 15.97,
  "tax": 1.28,
  "total": 17.25,
  "change": 2.75,
  "payment_method": "CASH"
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
            prompt = f"""Please parse the following receipt text and return the structured data as JSON:

Allowed categories: {', '.join(ALLOWED_CATEGORIES)}

For each item, assign a category from the allowed list only. If unsure, use 'Other'.

{cleaned_text}

Return only the JSON object, no additional text or explanations."""

            # Get response from Ollama
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
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
        
        # Remove common OCR artifacts
        text = re.sub(r'[^\w\s\.\,\$\-\+\=\:\;\(\)\[\]\{\}]', '', text)
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        return '\n'.join(lines)
    
    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON from LLM response"""
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        
        if json_match:
            return json_match.group(0)
        
        # If no JSON found, try to clean up the response
        cleaned = response.strip()
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        
        return cleaned.strip()
    
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