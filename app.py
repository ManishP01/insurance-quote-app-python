from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import PyPDF2
import re
import os
import json
from werkzeug.utils import secure_filename
import tempfile
import random

# Import OCR processor
try:
    from ocr_processor_simple import InsuranceOCRSimple
    OCR_AVAILABLE = True
    print("✅ OCR processor loaded successfully")
except ImportError as e:
    print(f"⚠️  OCR not available: {e}")
    print("📝 Install OCR dependencies: pip install easyocr opencv-python PyMuPDF")
    OCR_AVAILABLE = False

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'bmp', 'tiff', 'heic'}

# Initialize OCR processor if available
if OCR_AVAILABLE:
    ocr_processor = InsuranceOCRSimple()

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Mock insurance data and discount rules
INSURANCE_RATES = {
    'auto': {
        'base': 1200,
        'factors': {
            'age': {'18-25': 1.5, '26-35': 1.2, '36-50': 1.0, '51+': 0.9},
            'experience': {'0-2': 1.3, '3-5': 1.1, '6-10': 1.0, '10+': 0.8},
            'vehicle_age': {'new': 1.2, '1-5': 1.0, '6-10': 0.9, '10+': 0.8}
        }
    },
    'home': {
        'base': 800,
        'factors': {
            'home_age': {'new': 0.9, '1-10': 1.0, '11-20': 1.1, '20+': 1.2},
            'security': {'high': 0.8, 'medium': 0.9, 'low': 1.0}
        }
    }
}

DISCOUNT_RULES = [
    {'name': 'Multi-Policy Discount', 'description': 'Bundle auto and home insurance', 'discount': 0.15},
    {'name': 'Safe Driver Discount', 'description': 'No accidents in 5 years', 'discount': 0.10},
    {'name': 'Security System Discount', 'description': 'Home security system installed', 'discount': 0.08},
    {'name': 'Good Student Discount', 'description': 'Maintain good grades (under 25)', 'discount': 0.05},
    {'name': 'Low Mileage Discount', 'description': 'Drive less than 10,000 miles/year', 'discount': 0.12}
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

def extract_pattern(text, pattern):
    """Extract information using regex pattern"""
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None

def extract_policy_info(text):
    """Extract policy information from PDF text"""
    policy_info = {
        'policy_number': extract_pattern(text, r'Policy\s*(?:Number|#):\s*([A-Z0-9-]+)'),
        'current_premium': extract_pattern(text, r'Premium:\s*\$?([0-9,]+\.?\d*)'),
        'coverage_type': extract_pattern(text, r'(Auto|Home|Life|Health)\s*Insurance'),
        'deductible': extract_pattern(text, r'Deductible:\s*\$?([0-9,]+)'),
        'vehicle_year': extract_pattern(text, r'Year:\s*(\d{4})'),
        'vehicle_make': extract_pattern(text, r'Make:\s*([A-Za-z]+)'),
        'vehicle_model': extract_pattern(text, r'Model:\s*([A-Za-z0-9\s]+)'),
        'driver_age': extract_pattern(text, r'Age:\s*(\d{2})'),
        'years_experience': extract_pattern(text, r'Experience:\s*(\d+)\s*years?')
    }
    
    # Clean up extracted data
    for key, value in policy_info.items():
        if value:
            policy_info[key] = value.replace(',', '').strip()
    
    return policy_info

def calculate_quote(policy_info):
    """Calculate insurance quote based on extracted information"""
    coverage_type = policy_info.get('coverage_type', '').lower()
    
    if not coverage_type or coverage_type not in INSURANCE_RATES:
        return {'error': 'Unsupported coverage type'}
    
    base_rate = INSURANCE_RATES[coverage_type]['base']
    multiplier = 1.0
    
    # Apply factors based on extracted information
    if coverage_type == 'auto':
        # Age factor
        if policy_info.get('driver_age'):
            try:
                age = int(policy_info['driver_age'])
                if 18 <= age <= 25:
                    multiplier *= INSURANCE_RATES['auto']['factors']['age']['18-25']
                elif 26 <= age <= 35:
                    multiplier *= INSURANCE_RATES['auto']['factors']['age']['26-35']
                elif 36 <= age <= 50:
                    multiplier *= INSURANCE_RATES['auto']['factors']['age']['36-50']
                elif age >= 51:
                    multiplier *= INSURANCE_RATES['auto']['factors']['age']['51+']
            except ValueError:
                pass
        
        # Experience factor
        if policy_info.get('years_experience'):
            try:
                exp = int(policy_info['years_experience'])
                if exp <= 2:
                    multiplier *= INSURANCE_RATES['auto']['factors']['experience']['0-2']
                elif exp <= 5:
                    multiplier *= INSURANCE_RATES['auto']['factors']['experience']['3-5']
                elif exp <= 10:
                    multiplier *= INSURANCE_RATES['auto']['factors']['experience']['6-10']
                else:
                    multiplier *= INSURANCE_RATES['auto']['factors']['experience']['10+']
            except ValueError:
                pass
    
    base_quote = round(base_rate * multiplier)
    
    # Calculate applicable discounts (simplified logic for demo)
    applicable_discounts = []
    for discount in DISCOUNT_RULES:
        if random.random() > 0.4:  # 60% chance of applying each discount
            applicable_discounts.append(discount)
    
    total_discount = sum(discount['discount'] for discount in applicable_discounts)
    discounted_quote = round(base_quote * (1 - total_discount))
    
    return {
        'base_quote': base_quote,
        'discounted_quote': discounted_quote,
        'total_discount': round(total_discount * 100),
        'applicable_discounts': applicable_discounts,
        'savings': base_quote - discounted_quote
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'policy_document' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['policy_document']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not supported. Please upload PDF, JPG, PNG, or other image files.'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(temp_path)
        
        try:
            print(f"🚀 Processing uploaded file: {filename}")
            
            # Use OCR processor if available, otherwise fallback to basic PDF processing
            if OCR_AVAILABLE:
                print("📊 Using OCR processor for enhanced document analysis...")
                result = ocr_processor.process_document(temp_path)
                
                if not result['success']:
                    return jsonify({'error': result['error']}), 500
                
                policy_info = result['policy_info']
                print(f"✅ Successfully extracted policy information")
                
            else:
                print("📄 Using basic PDF processing (OCR not available)...")
                # Fallback to basic PDF processing
                if not filename.lower().endswith('.pdf'):
                    return jsonify({'error': 'OCR not available. Please upload PDF files only or install OCR dependencies.'}), 400
                
                text = extract_text_from_pdf(temp_path)
                policy_info = extract_policy_info(text)
            
            print("💰 Calculating insurance quote...")
            # Calculate quote
            quote = calculate_quote(policy_info)
            
            # Clean up temporary file
            os.remove(temp_path)
            print(f"🎉 Processing complete for {filename}")
            
            return jsonify({
                'policy_info': policy_info,
                'quote': quote,
                'message': 'Document processed successfully',
                'ocr_enabled': OCR_AVAILABLE,
                'processing_time': 'Completed in seconds'
            })
            
        except Exception as e:
            # Clean up temporary file on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            print(f"❌ Error processing {filename}: {str(e)}")
            return jsonify({'error': f'Processing failed: {str(e)}'}), 500
            
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/discount-tips')
def get_discount_tips():
    tips = [
        {
            'category': 'Multi-Policy',
            'tip': 'Bundle your auto and home insurance for up to 15% savings',
            'potential_savings': '$200-400/year'
        },
        {
            'category': 'Safety',
            'tip': 'Install a security system in your home for additional discounts',
            'potential_savings': '$50-150/year'
        },
        {
            'category': 'Driving',
            'tip': 'Consider usage-based insurance if you drive less than 10,000 miles/year',
            'potential_savings': '$100-300/year'
        },
        {
            'category': 'Maintenance',
            'tip': 'Keep a clean driving record - no accidents or violations',
            'potential_savings': '$150-500/year'
        }
    ]
    return jsonify(tips)

@app.route('/api/processing-tips')
def get_processing_tips():
    """Get random tips to show during processing"""
    tips = [
        "💡 Did you know? Bundling policies can save you up to 25% on premiums!",
        "🚗 Safe drivers with no accidents save an average of $300 per year.",
        "🏠 Installing a security system can reduce your home insurance by 8-15%.",
        "📱 Usage-based insurance can save low-mileage drivers up to $500 annually.",
        "🎓 Students with good grades often qualify for additional discounts.",
        "💳 Paying annually instead of monthly can save you processing fees.",
        "🔒 Higher deductibles mean lower monthly premiums - but ensure you can afford them.",
        "📊 Your credit score can affect your insurance rates in most states."
    ]
    return jsonify({'tip': random.choice(tips)})

@app.route('/debug')
def debug_page():
    return render_template('debug.html')

@app.route('/fnol-accurate')
def fnol_accurate():
    return render_template('fnol_accurate.html')

@app.route('/fnol-enhanced')
def fnol_enhanced():
    return render_template('fnol_enhanced.html')

@app.route('/fnol-working')
def fnol_working():
    return render_template('fnol_working.html')

@app.route('/speech-test')
def speech_test():
    return render_template('speech_test.html')

@app.route('/fnol-simple')
def fnol_simple():
    return render_template('fnol_simple.html')

@app.route('/fnol-debug')
def fnol_debug():
    return render_template('fnol_debug.html')

@app.route('/fnol')
def fnol_page():
    return render_template('fnol.html')

@app.route('/api/submit-fnol', methods=['POST'])
def submit_fnol():
    try:
        fnol_data = request.json
        
        # Log the FNOL submission
        print("🚨 FNOL Claim Submitted:")
        print(f"📅 Timestamp: {fnol_data.get('timestamp')}")
        print(f"📋 Claim Type: {fnol_data.get('claimData', {}).get('incidentType', 'Unknown')}")
        print(f"💬 Conversation Length: {len(fnol_data.get('conversation', []))} messages")
        
        # In production, this would:
        # 1. Save to database
        # 2. Generate claim number
        # 3. Send to processing team
        # 4. Send confirmation email
        # 5. Create case in CRM system
        
        # Generate a mock claim number
        import random
        claim_number = f"CLM-{random.randint(100000, 999999)}"
        
        # Simulate processing
        response_data = {
            'success': True,
            'claim_number': claim_number,
            'message': 'FNOL claim submitted successfully',
            'next_steps': [
                'An adjuster will contact you within 24 hours',
                'You will receive a confirmation email shortly',
                'Please keep your claim number for reference: ' + claim_number
            ]
        }
        
        print(f"✅ Claim Number Generated: {claim_number}")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ FNOL submission error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to submit FNOL claim',
            'message': str(e)
        }), 500

@app.route('/claim-confirmation')
def claim_confirmation():
    return render_template('claim_confirmation.html')

@app.route('/quote')
def quote_results():
    return render_template('quote.html')

@app.route('/tips')
def discount_tips():
    return render_template('tips.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
