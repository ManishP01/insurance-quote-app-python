#!/usr/bin/env python3
"""
OCR processor for insurance documents - supports images and PDFs
Combines Tesseract and EasyOCR for better accuracy
"""

import os
import cv2
import numpy as np
from PIL import Image
import pytesseract
import easyocr
import fitz  # PyMuPDF for PDF handling
import re
from typing import Dict, List, Optional

class InsuranceOCR:
    def __init__(self):
        """Initialize OCR engines"""
        self.easyocr_reader = easyocr.Reader(['en'])
        
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for better OCR accuracy"""
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Deskew if needed (basic rotation correction)
        coords = np.column_stack(np.where(thresh > 0))
        if len(coords) > 0:
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            
            if abs(angle) > 0.5:  # Only rotate if significant skew
                (h, w) = thresh.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                thresh = cv2.warpAffine(thresh, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        return thresh
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using both Tesseract and EasyOCR"""
        try:
            # Preprocess image
            processed_img = self.preprocess_image(image_path)
            
            # Method 1: Tesseract with custom config
            tesseract_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:-$()/ '
            tesseract_text = pytesseract.image_to_string(processed_img, config=tesseract_config)
            
            # Method 2: EasyOCR
            easyocr_results = self.easyocr_reader.readtext(processed_img)
            easyocr_text = ' '.join([result[1] for result in easyocr_results if result[2] > 0.5])
            
            # Combine results (prefer EasyOCR for better accuracy, fallback to Tesseract)
            if len(easyocr_text.strip()) > len(tesseract_text.strip()) * 0.8:
                return easyocr_text
            else:
                return tesseract_text
                
        except Exception as e:
            print(f"Error processing image {image_path}: {str(e)}")
            return ""
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF, handling both text and image-based PDFs"""
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # First try to extract text directly
                text = page.get_text()
                
                # If no text or very little text, treat as image-based PDF
                if len(text.strip()) < 50:
                    # Convert page to image
                    mat = fitz.Matrix(2, 2)  # 2x zoom for better OCR
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes("png")
                    
                    # Save temporarily and process with OCR
                    temp_img_path = f"temp_page_{page_num}.png"
                    with open(temp_img_path, "wb") as f:
                        f.write(img_data)
                    
                    # Extract text using OCR
                    ocr_text = self.extract_text_from_image(temp_img_path)
                    full_text += ocr_text + "\n"
                    
                    # Clean up temp file
                    os.remove(temp_img_path)
                else:
                    full_text += text + "\n"
            
            doc.close()
            return full_text
            
        except Exception as e:
            print(f"Error processing PDF {pdf_path}: {str(e)}")
            return ""
    
    def extract_policy_info(self, text: str) -> Dict[str, Optional[str]]:
        """Enhanced policy information extraction with better patterns"""
        
        # More comprehensive regex patterns
        patterns = {
            'policy_number': [
                r'Policy\s*(?:Number|#|No\.?):\s*([A-Z0-9-]{6,20})',
                r'Policy\s*([A-Z0-9-]{8,15})',
                r'(?:Policy|Pol)\s*#?\s*([A-Z]{2,4}[0-9-]{6,15})'
            ],
            'current_premium': [
                r'(?:Annual\s*)?Premium:\s*\$?([0-9,]+\.?\d*)',
                r'Total\s*Premium:\s*\$?([0-9,]+\.?\d*)',
                r'Premium\s*Amount:\s*\$?([0-9,]+\.?\d*)'
            ],
            'coverage_type': [
                r'(Auto|Vehicle|Car|Motor)\s*Insurance',
                r'(Home|Property|Homeowner)\s*Insurance',
                r'(Life|Term|Whole)\s*Insurance',
                r'(Health|Medical)\s*Insurance'
            ],
            'deductible': [
                r'Deductible:\s*\$?([0-9,]+)',
                r'Ded:\s*\$?([0-9,]+)',
                r'Deduct:\s*\$?([0-9,]+)'
            ],
            'vehicle_year': [
                r'(?:Year|Model\s*Year):\s*(\d{4})',
                r'(\d{4})\s+[A-Z][a-z]+\s+[A-Z][a-z]+',  # 2020 Toyota Camry
                r'Vehicle:\s*(\d{4})'
            ],
            'vehicle_make': [
                r'Make:\s*([A-Z][a-z]+)',
                r'(\d{4})\s+([A-Z][a-z]+)\s+[A-Z][a-z]+',  # Extract make from "2020 Toyota Camry"
                r'Vehicle:\s*\d{4}\s+([A-Z][a-z]+)'
            ],
            'vehicle_model': [
                r'Model:\s*([A-Za-z0-9\s-]+)',
                r'\d{4}\s+[A-Z][a-z]+\s+([A-Za-z0-9\s-]+)',  # Extract model
                r'Vehicle:\s*\d{4}\s+[A-Z][a-z]+\s+([A-Za-z0-9\s-]+)'
            ],
            'driver_age': [
                r'(?:Age|DOB):\s*(\d{2})',
                r'Driver\s*Age:\s*(\d{2})',
                r'Primary\s*Driver.*?Age:\s*(\d{2})'
            ],
            'years_experience': [
                r'(?:Experience|Driving\s*Experience):\s*(\d+)\s*years?',
                r'Licensed\s*for:\s*(\d+)\s*years?',
                r'(\d+)\s*years?\s*(?:of\s*)?(?:driving\s*)?experience'
            ]
        }
        
        policy_info = {}
        
        for field, pattern_list in patterns.items():
            policy_info[field] = None
            for pattern in pattern_list:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1 if len(match.groups()) == 1 else 2).strip()
                    # Clean up the value
                    value = re.sub(r'[,\s]+', ' ', value).strip()
                    policy_info[field] = value
                    break
        
        return policy_info
    
    def process_document(self, file_path: str) -> Dict:
        """Process any document type (PDF or image) and extract policy information"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.pdf':
                text = self.extract_text_from_pdf(file_path)
            elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.heic']:
                text = self.extract_text_from_image(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            if not text.strip():
                raise ValueError("No text could be extracted from the document")
            
            policy_info = self.extract_policy_info(text)
            
            return {
                'success': True,
                'extracted_text': text,
                'policy_info': policy_info,
                'message': 'Document processed successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to process document'
            }

# Example usage
if __name__ == "__main__":
    ocr = InsuranceOCR()
    
    # Test with sample PDF
    if os.path.exists("sample-auto-policy.pdf"):
        result = ocr.process_document("sample-auto-policy.pdf")
        print("PDF Processing Result:")
        print(f"Success: {result['success']}")
        if result['success']:
            print("Extracted Policy Info:")
            for key, value in result['policy_info'].items():
                if value:
                    print(f"  {key}: {value}")
        else:
            print(f"Error: {result['error']}")
