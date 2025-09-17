"""
OpenAI Vision-based Document Processor - No OCR Required
"""

import base64
import json
import os
from typing import Dict, Optional
from PIL import Image
import io

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class VisionDocumentProcessor:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        
        # Setup SSL bypass first
        try:
            from ssl_bypass import setup_ssl_bypass
            setup_ssl_bypass()
        except ImportError:
            pass
        
        api_key = os.getenv('OPENAI_API_KEY')
        self.openai_available = OPENAI_AVAILABLE and api_key and api_key.startswith('sk-')
        
        if self.openai_available:
            openai.api_key = api_key
            print("✅ OpenAI Vision processor enabled")
        else:
            print("⚠️ OpenAI Vision not available")
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 for OpenAI Vision"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_policy_image(self, image_path: str) -> Dict:
        """Analyze policy document using OpenAI Vision"""
        if not self.openai_available:
            return {
                'success': False,
                'error': 'OpenAI Vision not available',
                'extracted_data': {}
            }
        
        try:
            # Encode image
            base64_image = self.encode_image(image_path)
            
            # Analyze with OpenAI Vision
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this insurance policy document and extract key information. Return JSON format:
{
  "policy_type": "Auto Insurance|Home Insurance|Life Insurance",
  "policy_number": "extracted policy number",
  "customer_name": "customer name",
  "premium_amount": "annual premium amount",
  "coverage_details": ["list of coverages found"],
  "deductible": "deductible amount",
  "effective_dates": "policy period",
  "confidence": 0.9
}"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            # Parse response
            content = response.choices[0].message.content
            print(f"🔍 Vision API raw response: {content}")
            
            try:
                result = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                # Try to extract JSON from the response if it's wrapped in text
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group())
                        print("✅ Extracted JSON from wrapped response")
                    except json.JSONDecodeError:
                        return {
                            'success': False,
                            'error': f'Could not parse Vision API response as JSON: {e}'
                        }
                else:
                    return {
                        'success': False,
                        'error': f'No JSON found in Vision API response: {content}'
                    }
            
            return {
                'success': True,
                'extracted_data': result,
                'processing_method': 'openai_vision'
            }
            
        except Exception as e:
            print(f"❌ Vision analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'extracted_data': {}
            }
    
    def process_uploaded_file(self, file_path: str) -> Dict:
        """Process uploaded policy file (image or PDF)"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            # Direct image analysis
            return self.analyze_policy_image(file_path)
        
        elif file_ext == '.pdf':
            # Convert PDF first page to image, then analyze
            return self.process_pdf_with_vision(file_path)
        
        else:
            return {
                'success': False,
                'error': f'Unsupported file type: {file_ext}',
                'extracted_data': {}
            }
    
    def process_pdf_with_vision(self, pdf_path: str) -> Dict:
        """Convert PDF to image and analyze with Vision"""
        try:
            try:
                import fitz  # PyMuPDF
            except ImportError:
                return {
                    'success': False,
                    'error': 'PyMuPDF not available for PDF processing. Install with: pip install PyMuPDF',
                    'extracted_data': {}
                }
            
            # Open PDF and convert first page to image
            doc = fitz.open(pdf_path)
            page = doc[0]
            pix = page.get_pixmap()
            
            # Save as temporary image
            temp_image_path = pdf_path.replace('.pdf', '_temp.png')
            pix.save(temp_image_path)
            
            # Analyze with Vision
            result = self.analyze_policy_image(temp_image_path)
            
            # Clean up temp file
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'PDF processing failed: {e}',
                'extracted_data': {}
            }

# Test the vision processor
if __name__ == "__main__":
    processor = VisionDocumentProcessor()
    
    # Test with a sample image
    test_file = "sample_policy.jpg"
    if os.path.exists(test_file):
        result = processor.process_uploaded_file(test_file)
        print(f"Analysis result: {result}")
    else:
        print("No test file found")
