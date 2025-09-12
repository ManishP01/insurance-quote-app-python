# 🏢 Professional Insurance Platform with AI Assistant

A comprehensive insurance platform featuring document analysis, competitive quoting, and an intelligent AI chatbot.

## 🚀 Features

### 📄 Document Analysis & Quoting
- **OCR Document Processing**: Upload PDF, JPG, PNG, HEIC insurance documents
- **Intelligent Text Extraction**: Extracts policy details, premiums, carriers
- **Competitive Quote Generation**: Provides side-by-side coverage comparison
- **Enhanced Carrier Detection**: Supports 20+ major insurance carriers
- **Professional Results Display**: Travelers.com branded styling

### 🤖 AI Insurance Assistant
- **Decisive Answers**: Clear YES/NO responses to coverage questions
- **Personalized Responses**: Uses real customer data and policy information
- **Coverage Scenarios**: "Will I be covered if..." questions with specific answers
- **Policy Information**: Bill due dates, payment methods, premium explanations
- **Supporting Documentation**: References specific policy sections
- **Smart Escalation**: Connects to live agent only when truly needed

### 👥 Customer Profiles
- **John Smith**: Auto Insurance policy with comprehensive coverage
- **Sarah Johnson**: Home Insurance policy with dwelling coverage
- **Real Policy Data**: Actual coverage limits, deductibles, payment schedules

### 🎨 Professional Design
- **Travelers.com Branding**: Authentic color scheme and styling
- **Mobile Responsive**: Works seamlessly on all devices
- **Professional Typography**: Segoe UI font matching corporate standards
- **Smooth Animations**: Enhanced user experience with hover effects

## 🛠️ Technical Stack

- **Backend**: Python Flask
- **OCR**: Tesseract with image preprocessing
- **AI Bot**: Rule-based with customer data integration
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom Travelers.com theme
- **File Processing**: PIL, OpenCV for image enhancement

## 📋 Setup Instructions

1. **Clone Repository**:
   ```bash
   git clone <repository-url>
   cd insurance-quote-app-python
   ```

2. **Install Dependencies**:
   ```bash
   pip install flask pillow pytesseract opencv-python
   ```

3. **Install Tesseract OCR**:
   - **macOS**: `brew install tesseract`
   - **Ubuntu**: `sudo apt-get install tesseract-ocr`
   - **Windows**: Download from GitHub releases

4. **Run Application**:
   ```bash
   python3 app.py
   ```

5. **Access Platform**: http://localhost:5000

## 🧪 Testing the Platform

### Document Upload Testing
1. Upload `sample-auto-policy.pdf` or `sample-policy-image.jpg`
2. View detailed coverage comparison table
3. Test "Upload Another Document" functionality

### AI Assistant Testing
1. Click AI Assistant button or chat widget
2. Select customer: "Sarah Johnson (Home)" or "John Smith (Auto)"
3. Try these questions:
   - "Will I be covered if a tree falls on my house?"
   - "Will I be covered if I hit a deer?"
   - "When is my bill due?"
   - "What does my liability coverage include?"

## 📊 Sample Responses

### Coverage Scenario (Home Insurance)
**Question**: "Will I be covered if a tree falls on my house?"
**Response**: 
> **✅ YES, Sarah Johnson, you ARE covered!**
> 
> 🏠 **Your Dwelling Coverage**: $350,000
> 💰 **Your Deductible**: $1000
> 
> **What happens:**
> • Insurance pays for house repairs after your $1000 deductible
> • Tree removal from structure is covered
> • Temporary living expenses if house is uninhabitable

### Policy Information
**Question**: "When is my bill due?"
**Response**:
> 💳 **Your Next Payment Information:**
> 
> 📅 **Due Date**: August 15, 2024
> 💰 **Amount Due**: $104.00
> ⏰ **Days Until Due**: 12 days

## 🔧 Configuration

### Customer Data
Edit `customer_data.json` to add more customer profiles with:
- Personal information
- Policy details and coverage
- Payment schedules
- Claims history

### Insurance Knowledge
Modify `insurance_knowledge.json` to update:
- Coverage explanations
- Policy terms and definitions
- Coverage scenarios
- Premium factors

### Styling
Customize `static/css/travelers-theme.css` for:
- Brand colors and fonts
- Layout and spacing
- Animation effects
- Mobile responsiveness

## 🎯 Key Components

### AI Insurance Bot (`ai_insurance_bot.py`)
- Intent detection and classification
- Customer data integration
- Scenario-based responses
- Supporting document references

### Document Processing (`app.py`)
- OCR text extraction
- Policy analysis and parsing
- Competitive quote calculation
- Coverage comparison generation

### Frontend (`templates/index.html`)
- Professional insurance styling
- Interactive chat widget
- Document upload interface
- Results display with comparisons

## 🚀 Production Deployment

1. **Environment Variables**: Set up production configurations
2. **Database Integration**: Replace JSON files with database
3. **Security**: Add authentication and authorization
4. **Scaling**: Implement load balancing and caching
5. **Monitoring**: Add logging and analytics

## 📞 Support

For technical support or feature requests, contact the development team.

---

**Built with ❤️ for professional insurance operations**
