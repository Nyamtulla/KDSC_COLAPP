import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedReceiptParser:
    """Enhanced receipt parser combining OCR and offline LLM for robust parsing"""
    
    def __init__(self, use_llm: bool = True):
        """
        Initialize the enhanced receipt parser
        
        Args:
            use_llm: Whether to use offline LLM for parsing
        """
        self.llm_service = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all available services"""
        try:
            from offline_llm_service import OfflineLLMService
            self.llm_service = OfflineLLMService()
            logger.info("✓ Offline LLM service initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize LLM service: {e}")
            logger.info("⚠️  Falling back to OCR-only parsing (no LLM)")
            self.llm_service = None # Ensure it's None if initialization fails
    
    def parse_receipt(self, file_path: str, method: str = 'auto') -> Dict[str, Any]:
        """
        Parse receipt using the best available method
        
        Args:
            file_path: Path to receipt file (image or PDF)
            method: Parsing method ('auto', 'llm', 'custom_nlp', 'ocr_only')
            
        Returns:
            Dictionary with parsed receipt data
        """
        try:
            # Validate file exists
            norm_path = os.path.normpath(file_path)
            if not os.path.exists(norm_path):
                return {
                    'success': False,
                    'error': f'File not found: {norm_path}',
                    'method': 'none'
                }
            
            # Only use LLM method
            return self._parse_with_llm(norm_path)
            
        except Exception as e:
            logger.error(f"Error parsing receipt {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'none',
                'data': self._get_fallback_data()
            }
    
    def _parse_with_llm(self, file_path: str) -> Dict[str, Any]:
        """Parse receipt using offline LLM (image → OCR → LLM) or fallback to OCR-only"""
        norm_path = os.path.normpath(file_path)
        try:
            if not self.llm_service:
                logger.info("LLM not available, using OCR-only parsing")
                return self._parse_with_ocr_only(norm_path)
            
            result = self.llm_service.parse_receipt_image(norm_path)
            return result
        except Exception as e:
            logger.error(f"LLM parsing failed: {e}")
            logger.info("Falling back to OCR-only parsing")
            return self._parse_with_ocr_only(norm_path)
    
    def _parse_with_ocr_only(self, file_path: str) -> Dict[str, Any]:
        """Parse receipt using OCR-only with heuristic rules"""
        try:
            from ocr_service import OCRService
            ocr_service = OCRService()
            
            # Extract text using OCR
            ocr_text = ocr_service.extract_text(file_path)
            
            # Apply heuristic parsing
            result = self._apply_heuristic_parsing(ocr_text)
            
            return {
                'success': True,
                'method': 'ocr_only',
                'data': result
            }
        except Exception as e:
            logger.error(f"OCR-only parsing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'ocr_only',
                'data': self._get_fallback_data()
            }
    
    def _map_items_for_ui(self, items):
        mapped = []
        for item in items:
            mapped.append({
                "product_name": item.get("name", ""),
                "price": item.get("total_price", 0.0),
                "category": item.get("category", "Other"),
                "quantity": item.get("quantity", 1.0),
                "unit_price": item.get("unit_price", 0.0),
                "total_price": item.get("total_price", 0.0),
            })
        return mapped
    
    def _apply_heuristic_parsing(self, text: str) -> Dict[str, Any]:
        """Apply heuristic rules to parse receipt text"""
        try:
            lines = text.split('\n')
            
            # Extract store name (first few lines)
            store_name = self._extract_store_name_heuristic(lines)
            
            # Extract total amount
            total_amount = self._extract_total_amount_heuristic(lines)
            
            # Extract items
            items = self._extract_items_heuristic(lines)
            
            # Extract date/time
            date_time = self._extract_date_time_heuristic(lines)
            
            return {
                'store_name': store_name,
                'date': date_time.get('date'),
                'time': date_time.get('time'),
                'items': items,
                'total': total_amount,
                'subtotal': None,
                'tax': None,
                'change': None,
                'payment_method': None
            }
            
        except Exception as e:
            logger.error(f"Heuristic parsing failed: {e}")
            return self._get_fallback_data()
    
    def _extract_store_name_heuristic(self, lines: List[str]) -> str:
        """Extract store name using heuristic rules"""
        # Look for store name in first few lines
        for i in range(min(5, len(lines))):
            line = lines[i].strip()
            if len(line) > 3 and not any(char.isdigit() for char in line):
                # Remove common receipt prefixes
                line = line.replace('RECEIPT', '').replace('INVOICE', '').strip()
                if line:
                    return line
        
        return 'Unknown Store'
    
    def _extract_total_amount_heuristic(self, lines: List[str]) -> float:
        """Extract total amount using heuristic rules"""
        import re
        
        # Look for total patterns
        total_patterns = [
            r'total[\s:]*\$?(\d+\.\d{2})',
            r'amount[\s:]*\$?(\d+\.\d{2})',
            r'grand total[\s:]*\$?(\d+\.\d{2})',
            r'\$?(\d+\.\d{2})$'
        ]
        
        # Search from bottom up (total is usually at bottom)
        for line in reversed(lines):
            line = line.lower().strip()
            for pattern in total_patterns:
                match = re.search(pattern, line)
                if match:
                    try:
                        return float(match.group(1))
                    except:
                        continue
        
        return 0.0
    
    def _extract_items_heuristic(self, lines: List[str]) -> List[Dict]:
        """Extract items using heuristic rules"""
        import re
        
        items = []
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue
            
            # Skip header/footer lines
            if any(keyword in line.lower() for keyword in ['receipt', 'total', 'tax', 'change', 'cash', 'card']):
                continue
            
            # Look for price patterns
            price_match = re.search(r'\$?(\d+\.\d{2})', line)
            if price_match:
                try:
                    price = float(price_match.group(1))
                    
                    # Extract product name (everything before the price)
                    product_name = line[:price_match.start()].strip()
                    if product_name:
                        items.append({
                            'name': product_name,
                            'quantity': 1.0,
                            'unit_price': price,
                            'total_price': price,
                            'category': self._categorize_item_heuristic(product_name)
                        })
                except:
                    continue
        
        return items
    
    def _extract_date_time_heuristic(self, lines: List[str]) -> Dict[str, str]:
        """Extract date and time using heuristic rules"""
        import re
        
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
            r'(\d{4})-(\d{1,2})-(\d{1,2})'
        ]
        
        time_patterns = [
            r'(\d{1,2}):(\d{2})(?::\d{2})?\s*(am|pm)?',
            r'(\d{1,2})\.(\d{2})\s*(am|pm)?'
        ]
        
        date = None
        time = None
        
        for line in lines:
            line = line.strip()
            
            # Look for date
            for pattern in date_patterns:
                match = re.search(pattern, line)
                if match:
                    try:
                        if len(match.groups()) == 3:
                            if len(match.group(3)) == 4:  # YYYY-MM-DD
                                date = f"{match.group(1)}-{match.group(2).zfill(2)}-{match.group(3).zfill(2)}"
                            else:  # MM/DD/YY
                                year = match.group(3)
                                if len(year) == 2:
                                    year = f"20{year}"
                                date = f"{year}-{match.group(1).zfill(2)}-{match.group(2).zfill(2)}"
                        break
                    except:
                        continue
            
            # Look for time
            for pattern in time_patterns:
                match = re.search(pattern, line.lower())
                if match:
                    try:
                        hour = int(match.group(1))
                        minute = match.group(2)
                        ampm = match.group(3) if len(match.groups()) > 2 else None
                        
                        if ampm:
                            if ampm == 'pm' and hour != 12:
                                hour += 12
                            elif ampm == 'am' and hour == 12:
                                hour = 0
                        
                        time = f"{hour:02d}:{minute}"
                        break
                    except:
                        continue
        
        # At the end, ensure no None values in the returned dict
        result = { 'date': '', 'time': '' }
        if date:
            result['date'] = date
        if time:
            result['time'] = time
        return { 'date': result.get('date', '') or '', 'time': result.get('time', '') or '' }
    
    def _categorize_item_heuristic(self, product_name: str) -> str:
        """Categorize item using heuristic rules"""
        product_lower = product_name.lower()
        
        # Dairy products
        if any(word in product_lower for word in ['milk', 'cheese', 'yogurt', 'cream', 'butter']):
            return 'Dairy'
        
        # Produce
        if any(word in product_lower for word in ['apple', 'banana', 'orange', 'lettuce', 'tomato', 'carrot']):
            return 'Produce'
        
        # Meat
        if any(word in product_lower for word in ['chicken', 'beef', 'pork', 'fish', 'meat']):
            return 'Meat'
        
        # Bread/Bakery
        if any(word in product_lower for word in ['bread', 'bun', 'cake', 'cookie', 'pastry']):
            return 'Bakery'
        
        # Beverages
        if any(word in product_lower for word in ['soda', 'water', 'juice', 'coffee', 'tea']):
            return 'Beverages'
        
        return 'Other'
    
    def _get_fallback_data(self) -> Dict[str, Any]:
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
    
    def get_available_methods(self) -> Dict[str, Any]:
        """Get information about available parsing methods"""
        methods = {
            'llm': {
                'available': self.llm_service is not None,
                'description': 'Offline LLM parsing (highest accuracy)'
            }
        }
        
        return methods
    
    def test_services(self) -> Dict[str, Any]:
        """Test status of available services (LLM only)"""
        return {
            'llm': self.llm_service is not None
        } 