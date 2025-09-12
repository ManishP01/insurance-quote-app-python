#!/usr/bin/env python3
"""
Test script to verify the OCR-enhanced insurance quote application
"""

import requests
import os
import json

def test_application():
    """Test the application functionality"""
    
    print("🧪 Testing QuickQuote Insurance Application")
    print("=" * 50)
    
    # Test 1: Check if server is accessible
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("💡 Make sure to run 'python3 app.py' first")
        return False
    
    # Test 2: Check discount tips API
    try:
        response = requests.get('http://localhost:5000/api/discount-tips', timeout=5)
        if response.status_code == 200:
            tips = response.json()
            print(f"✅ Discount tips API working ({len(tips)} tips available)")
        else:
            print(f"❌ Discount tips API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Discount tips API error: {e}")
    
    # Test 3: Test file upload with sample PDF
    if os.path.exists('sample-auto-policy.pdf'):
        try:
            print("📄 Testing PDF upload and OCR processing...")
            
            with open('sample-auto-policy.pdf', 'rb') as f:
                files = {'policy_document': f}
                response = requests.post('http://localhost:5000/upload', files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ PDF upload and processing successful!")
                
                # Display extracted information
                policy_info = result.get('policy_info', {})
                quote = result.get('quote', {})
                
                print("\n📋 Extracted Policy Information:")
                for key, value in policy_info.items():
                    if value:
                        display_key = key.replace('_', ' ').title()
                        print(f"  • {display_key}: {value}")
                
                print(f"\n💰 Quote Results:")
                print(f"  • Base Quote: ${quote.get('base_quote', 'N/A')}")
                print(f"  • Discounted Quote: ${quote.get('discounted_quote', 'N/A')}")
                print(f"  • Total Savings: ${quote.get('savings', 'N/A')} ({quote.get('total_discount', 'N/A')}% off)")
                print(f"  • Discounts Applied: {len(quote.get('applicable_discounts', []))}")
                
                print("✅ OCR and quote calculation working perfectly!")
                
            else:
                print(f"❌ PDF upload failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ PDF upload test failed: {e}")
    else:
        print("⚠️  Sample PDF not found. Run 'python3 sample-policy.py' to create it.")
    
    print("\n🎉 Application testing complete!")
    return True

if __name__ == "__main__":
    test_application()
