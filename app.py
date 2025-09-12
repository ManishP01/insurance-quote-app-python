from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import PyPDF2
import re
import os
import json
from werkzeug.utils import secure_filename
import tempfile
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import OCR processor
try:
    from ocr_processor_simple import InsuranceOCRSimple
    OCR_AVAILABLE = True
    print("✅ OCR processor loaded successfully")
except ImportError as e:
    print(f"⚠️  OCR not available: {e}")
    print("📝 Install OCR dependencies: pip install easyocr opencv-python PyMuPDF")
    OCR_AVAILABLE = False

# Import multilingual chatbot with smart fallback
CHATBOT_AVAILABLE = False
CHATBOT_TYPE = None
chatbot = None

try:
    # Try GPT version first if API key is available
    if os.getenv('OPENAI_API_KEY'):
        from multilingual_chatbot_gpt import GPTMultilingualInsuranceChatbot
        chatbot = GPTMultilingualInsuranceChatbot()
        CHATBOT_AVAILABLE = True
        CHATBOT_TYPE = "GPT"
        print("✅ GPT-powered multilingual chatbot loaded successfully")
    else:
        raise Exception("No OpenAI API key found, falling back to keyword-based")
except Exception as e:
    print(f"⚠️  GPT chatbot not available: {e}")
    try:
        from multilingual_chatbot import MultilingualInsuranceChatbot
        chatbot = MultilingualInsuranceChatbot()
        CHATBOT_AVAILABLE = True
        CHATBOT_TYPE = "Keyword"
        print("✅ Keyword-based multilingual chatbot loaded as fallback")
    except ImportError as e2:
        print(f"⚠️  No chatbot available: {e2}")
        CHATBOT_AVAILABLE = False
        CHATBOT_TYPE = None

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

# Insurance rates and calculations
INSURANCE_RATES = {
    'auto': {
        'base': 1200,
        'factors': {
            'age': {'18-25': 1.5, '26-35': 1.2, '36-50': 1.0, '51+': 0.9},
            'experience': {'0-2': 1.3, '3-5': 1.1, '6-10': 1.0, '10+': 0.8},
            'location': {'urban': 1.2, 'suburban': 1.0, 'rural': 0.8},
            'vehicle_age': {'0-3': 1.1, '4-7': 1.0, '8-15': 0.9, '15+': 0.8}
        }
    },
    'home': {
        'base': 800,
        'factors': {
            'home_age': {'0-10': 1.0, '11-25': 1.1, '26-50': 1.2, '50+': 1.4},
            'location': {'urban': 1.1, 'suburban': 1.0, 'rural': 0.9},
            'security': {'high': 0.9, 'medium': 1.0, 'low': 1.1}
        }
    }
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""

def analyze_policy_document(text):
    """Analyze policy document and extract key information"""
    analysis = {
        'policy_type': 'Unknown',
        'current_premium': 0,
        'coverage_limits': {},
        'deductible': 0,
        'policy_number': '',
        'expiration_date': '',
        'carrier': '',
        'confidence': 0.0
    }
    
    text_lower = text.lower()
    
    # Detect policy type
    if any(word in text_lower for word in ['auto', 'vehicle', 'car', 'automobile']):
        analysis['policy_type'] = 'Auto'
        analysis['confidence'] += 0.2
    elif any(word in text_lower for word in ['home', 'homeowner', 'property', 'dwelling']):
        analysis['policy_type'] = 'Home'
        analysis['confidence'] += 0.2
    
    # Extract premium
    premium_patterns = [
        r'premium[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        r'annual premium[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        r'total premium[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
    ]
    
    for pattern in premium_patterns:
        match = re.search(pattern, text_lower)
        if match:
            analysis['current_premium'] = float(match.group(1).replace(',', ''))
            analysis['confidence'] += 0.3
            break
    
    # Extract policy number
    policy_patterns = [
        r'policy\s*(?:number|#)[:\s]*([A-Z0-9\-]+)',
        r'policy[:\s]*([A-Z0-9\-]{6,})'
    ]
    
    for pattern in policy_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            analysis['policy_number'] = match.group(1)
            analysis['confidence'] += 0.2
            break
    
    # Extract carrier - expanded list
    carriers = [
        'state farm', 'geico', 'progressive', 'allstate', 'farmers', 'usaa', 'liberty mutual',
        'travelers', 'nationwide', 'american family', 'auto-owners', 'country financial',
        'erie', 'amica', 'csaa', 'mercury', 'safeco', 'the general', 'esurance',
        'metlife', 'hartford', 'chubb', 'aig', 'zurich', 'aaa', 'mutual'
    ]
    for carrier in carriers:
        if carrier in text_lower:
            analysis['carrier'] = carrier.title()
            analysis['confidence'] += 0.1
            break
    
    # Also check for common insurance company patterns
    carrier_patterns = [
        r'insurance\s+company[:\s]*([A-Za-z\s]+)',
        r'carrier[:\s]*([A-Za-z\s]+)',
        r'insurer[:\s]*([A-Za-z\s]+)',
        r'underwritten\s+by[:\s]*([A-Za-z\s]+)'
    ]
    
    for pattern in carrier_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match and not analysis['carrier']:
            carrier_name = match.group(1).strip()
            if len(carrier_name) > 2 and len(carrier_name) < 50:
                analysis['carrier'] = carrier_name
                analysis['confidence'] += 0.1
                break
    
    return analysis

def calculate_competitive_quote(analysis):
    """Calculate competitive quote with detailed coverage comparison"""
    if analysis['policy_type'] == 'Unknown':
        return None
    
    policy_type = analysis['policy_type'].lower()
    if policy_type not in INSURANCE_RATES:
        return None
    
    base_rate = INSURANCE_RATES[policy_type]['base']
    current_premium = analysis['current_premium']
    
    # Apply competitive factors
    competitive_factor = random.uniform(0.85, 0.95)  # 5-15% savings
    new_quote = base_rate * competitive_factor
    
    savings = max(0, current_premium - new_quote)
    savings_percent = (savings / current_premium * 100) if current_premium > 0 else 0
    
    # Generate detailed coverage comparison
    if policy_type == 'auto':
        current_coverage = {
            'liability': {'limit': '$50,000', 'premium': round(current_premium * 0.4, 2)},
            'collision': {'limit': '$25,000', 'premium': round(current_premium * 0.3, 2)},
            'comprehensive': {'limit': '$15,000', 'premium': round(current_premium * 0.2, 2)},
            'uninsured_motorist': {'limit': '$25,000', 'premium': round(current_premium * 0.1, 2)}
        }
        
        our_coverage = {
            'liability': {'limit': '$100,000', 'premium': round(new_quote * 0.4, 2)},
            'collision': {'limit': '$50,000', 'premium': round(new_quote * 0.3, 2)},
            'comprehensive': {'limit': '$25,000', 'premium': round(new_quote * 0.2, 2)},
            'uninsured_motorist': {'limit': '$50,000', 'premium': round(new_quote * 0.1, 2)}
        }
    else:  # home insurance
        current_coverage = {
            'dwelling': {'limit': '$200,000', 'premium': round(current_premium * 0.5, 2)},
            'personal_property': {'limit': '$100,000', 'premium': round(current_premium * 0.25, 2)},
            'liability': {'limit': '$100,000', 'premium': round(current_premium * 0.15, 2)},
            'medical_payments': {'limit': '$5,000', 'premium': round(current_premium * 0.1, 2)}
        }
        
        our_coverage = {
            'dwelling': {'limit': '$250,000', 'premium': round(new_quote * 0.5, 2)},
            'personal_property': {'limit': '$125,000', 'premium': round(new_quote * 0.25, 2)},
            'liability': {'limit': '$300,000', 'premium': round(new_quote * 0.15, 2)},
            'medical_payments': {'limit': '$10,000', 'premium': round(new_quote * 0.1, 2)}
        }
    
    return {
        'new_quote': round(new_quote, 2),
        'current_premium': current_premium,
        'savings': round(savings, 2),
        'savings_percent': round(savings_percent, 1),
        'policy_type': analysis['policy_type'],
        'current_coverage': current_coverage,
        'our_coverage': our_coverage,
        'coverage_improvements': calculate_coverage_improvements(current_coverage, our_coverage)
    }

def calculate_coverage_improvements(current, our):
    """Calculate coverage improvements"""
    improvements = []
    
    for coverage_type in current.keys():
        if coverage_type in our:
            current_limit = int(current[coverage_type]['limit'].replace('$', '').replace(',', ''))
            our_limit = int(our[coverage_type]['limit'].replace('$', '').replace(',', ''))
            
            if our_limit > current_limit:
                increase = our_limit - current_limit
                improvements.append({
                    'type': coverage_type.replace('_', ' ').title(),
                    'current': current[coverage_type]['limit'],
                    'our': our[coverage_type]['limit'],
                    'increase': f'${increase:,}',
                    'improvement': True
                })
            else:
                improvements.append({
                    'type': coverage_type.replace('_', ' ').title(),
                    'current': current[coverage_type]['limit'],
                    'our': our[coverage_type]['limit'],
                    'increase': 'Same',
                    'improvement': False
                })
    
    return improvements

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'File type not allowed'})
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(temp_path)
        
        try:
            # Process the file
            if filename.lower().endswith('.pdf'):
                # PDF processing
                text = extract_text_from_pdf(temp_path)
                if not text.strip():
                    return jsonify({'success': False, 'error': 'Could not extract text from PDF'})
            else:
                # Image processing with OCR
                if not OCR_AVAILABLE:
                    return jsonify({'success': False, 'error': 'OCR not available for image processing'})
                
                result = ocr_processor.process_document(temp_path)
                if not result['success']:
                    return jsonify({'success': False, 'error': result['error']})
                
                text = result['extracted_text']
            
            # Analyze the document
            analysis = analyze_policy_document(text)
            
            # Calculate competitive quote
            quote = calculate_competitive_quote(analysis)
            
            response = {
                'success': True,
                'analysis': analysis,
                'quote': quote,
                'extracted_text': text[:500] + '...' if len(text) > 500 else text
            }
            
            return jsonify(response)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'success': False, 'error': f'Processing error: {str(e)}'})

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
        
        # Generate a mock claim number
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

@app.route('/chatbot')
def chatbot_page():
    """Multilingual chatbot interface"""
    return render_template('chatbot.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Enhanced API endpoint with AI insurance bot"""
    try:
        data = request.json
        message = data.get('message', '')
        customer_id = data.get('customer_id', '12345')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'No message provided'
            }), 400
        
        # Try AI bot first for insurance-specific queries
        try:
            # Use Smart OpenAI approach if available
            if os.getenv('OPENAI_API_KEY'):
                from ai_insurance_bot_smart import SmartAIInsuranceBot
                ai_bot = SmartAIInsuranceBot()
            else:
                from ai_insurance_bot import AIInsuranceBot
                ai_bot = AIInsuranceBot()
            
            bot_response = ai_bot.handle_query(message, customer_id)
            
            if bot_response['intent'] != 'unknown':
                return jsonify({
                    'success': True,
                    'response': bot_response['response'],
                    'detected_language': bot_response.get('detected_language', 'en'),
                    'intent': bot_response['intent'],
                    'supporting_document': bot_response['supporting_document'],
                    'connect_to_agent': bot_response['connect_to_agent'],
                    'translation_method': bot_response.get('translation_method', 'smart_openai')
                })
        except Exception as e:
            print(f"AI bot error: {e}")
        
        # Fall back to multilingual chatbot
        if not CHATBOT_AVAILABLE:
            return jsonify({
                'success': True,
                'response': 'Hello! I can help you with basic questions. For detailed insurance information, please contact our customer service.',
                'detected_language': 'en',
                'intent': 'general',
                'translation_method': 'fallback'
            })
        
        # Process through multilingual chatbot
        response = chatbot.process_message(message, customer_id)
        last_conversation = chatbot.conversation_history[-1] if chatbot.conversation_history else {}
        
        return jsonify({
            'success': True,
            'response': response,
            'detected_language': last_conversation.get('detected_language', 'en'),
            'intent': last_conversation.get('intent', 'general_inquiry'),
            'translation_method': CHATBOT_TYPE.lower() if CHATBOT_TYPE else 'multilingual'
        })
        
    except Exception as e:
        print(f"❌ Chat API error: {str(e)}")
        return jsonify({
            'success': True,
            'response': 'I apologize, but I\'m having technical difficulties. Please contact customer service for assistance.',
            'detected_language': 'en',
            'intent': 'error',
            'translation_method': 'fallback'
        })

@app.route('/api/chat/history', methods=['GET'])
def chat_history():
    """Get conversation history and analytics"""
    try:
        if not CHATBOT_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Chatbot not available'
            }), 500
        
        view_type = request.args.get('view', 'customer')  # 'customer', 'agent', or 'summary'
        
        if view_type == 'agent':
            history = chatbot.get_agent_view()
            return jsonify({
                'success': True,
                'view_type': 'agent',
                'description': 'English version for agent handoff',
                'history': history
            })
        elif view_type == 'customer':
            history = chatbot.get_customer_view()
            return jsonify({
                'success': True,
                'view_type': 'customer',
                'description': 'Customer view in their original language',
                'history': history
            })
        else:  # summary
            summary = chatbot.get_conversation_summary()
            return jsonify({
                'success': True,
                'view_type': 'summary',
                'summary': summary
            })
        
    except Exception as e:
        print(f"❌ Chat history error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get chat history',
            'message': str(e)
        }), 500

@app.route('/agent-dashboard')
def agent_dashboard():
    """Agent dashboard for viewing conversations in English"""
    return render_template('agent_dashboard.html')

if __name__ == '__main__':
    print(f"🚀 Starting InsureQuote Pro with {CHATBOT_TYPE or 'No'} chatbot...")
    app.run(debug=True, host='0.0.0.0', port=5000)
