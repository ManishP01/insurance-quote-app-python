#!/usr/bin/env python3
"""
Test the fixes for PDF upload and camera issues
"""

import requests
import os
import time

def test_fixes():
    print("🔧 Testing Upload Fixes")
    print("=" * 30)
    
    base_url = "http://localhost:5000"
    
    # Test server
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server issue: {response.status_code}")
            return
    except:
        print("❌ Server not accessible")
        return
    
    # Test PDF upload
    pdf_file = "sample-auto-policy.pdf"
    if os.path.exists(pdf_file):
        print(f"\n📄 Testing PDF Upload: {pdf_file}")
        try:
            with open(pdf_file, 'rb') as f:
                files = {'policy_document': f}
                response = requests.post(f'{base_url}/upload', files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('error'):
                    print(f"❌ PDF upload error: {result['error']}")
                else:
                    print("✅ PDF upload successful!")
                    policy_info = result.get('policy_info', {})
                    extracted_fields = sum(1 for v in policy_info.values() if v)
                    print(f"📋 Extracted {extracted_fields} fields")
            else:
                print(f"❌ PDF upload failed: {response.status_code}")
                print(f"Response: {response.text[:200]}")
        except Exception as e:
            print(f"❌ PDF upload exception: {e}")
    else:
        print(f"⚠️  {pdf_file} not found")
    
    # Test image upload
    image_file = "sample-policy-image.jpg"
    if os.path.exists(image_file):
        print(f"\n🖼️  Testing Image Upload: {image_file}")
        try:
            with open(image_file, 'rb') as f:
                files = {'policy_document': f}
                response = requests.post(f'{base_url}/upload', files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('error'):
                    print(f"❌ Image upload error: {result['error']}")
                else:
                    print("✅ Image upload successful!")
                    policy_info = result.get('policy_info', {})
                    extracted_fields = sum(1 for v in policy_info.values() if v)
                    print(f"📋 Extracted {extracted_fields} fields")
            else:
                print(f"❌ Image upload failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Image upload exception: {e}")
    else:
        print(f"⚠️  {image_file} not found")
    
    print(f"\n🌐 Manual Testing:")
    print(f"  1. Open http://localhost:5000")
    print(f"  2. Try uploading {pdf_file} - should work now!")
    print(f"  3. Try uploading {image_file} - camera shouldn't open")
    print(f"  4. Try 'Take Photo' button - camera should open only then")
    print(f"  5. Test cancel button during processing")

if __name__ == "__main__":
    test_fixes()
