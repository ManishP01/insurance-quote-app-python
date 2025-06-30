#!/usr/bin/env python3
"""
Create a test image that looks like an insurance policy document
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_test_policy_image():
    # Create a white background image
    width, height = 800, 1000
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a system font, fallback to default
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        header_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 18)
        body_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 14)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
    
    # Draw the policy content
    y_pos = 50
    
    # Title
    draw.text((50, y_pos), "SAMPLE INSURANCE COMPANY", fill='black', font=title_font)
    y_pos += 40
    draw.text((50, y_pos), "AUTO INSURANCE POLICY", fill='black', font=title_font)
    y_pos += 60
    
    # Policy Information
    draw.text((50, y_pos), "POLICY INFORMATION", fill='black', font=header_font)
    y_pos += 40
    
    policy_info = [
        "Policy Number: AUTO-2024-789012",
        "Coverage Type: Auto Insurance", 
        "Policy Holder: Jane Doe",
        "Effective Date: March 1, 2024",
        "Expiration Date: March 1, 2025",
        "Premium: $1,650",
        "Deductible: $750"
    ]
    
    for info in policy_info:
        draw.text((70, y_pos), info, fill='black', font=body_font)
        y_pos += 25
    
    y_pos += 30
    
    # Vehicle Information
    draw.text((50, y_pos), "VEHICLE INFORMATION", fill='black', font=header_font)
    y_pos += 40
    
    vehicle_info = [
        "Year: 2019",
        "Make: Honda",
        "Model: Civic LX",
        "VIN: 2HGFC2F59KH123456"
    ]
    
    for info in vehicle_info:
        draw.text((70, y_pos), info, fill='black', font=body_font)
        y_pos += 25
    
    y_pos += 30
    
    # Driver Information
    draw.text((50, y_pos), "DRIVER INFORMATION", fill='black', font=header_font)
    y_pos += 40
    
    driver_info = [
        "Primary Driver: Jane Doe",
        "Age: 28",
        "Years of Driving Experience: 12 years",
        "License Number: D987654321"
    ]
    
    for info in driver_info:
        draw.text((70, y_pos), info, fill='black', font=body_font)
        y_pos += 25
    
    y_pos += 30
    
    # Coverage Details
    draw.text((50, y_pos), "COVERAGE DETAILS", fill='black', font=header_font)
    y_pos += 40
    
    coverage_info = [
        "Liability Coverage: $100,000/$300,000",
        "Comprehensive: $750 deductible",
        "Collision: $750 deductible",
        "Uninsured Motorist: $100,000/$300,000"
    ]
    
    for info in coverage_info:
        draw.text((70, y_pos), info, fill='black', font=body_font)
        y_pos += 25
    
    y_pos += 30
    
    # Discounts
    draw.text((50, y_pos), "DISCOUNTS APPLIED", fill='black', font=header_font)
    y_pos += 40
    
    discount_info = [
        "Safe Driver Discount: 12%",
        "Good Student Discount: 5%"
    ]
    
    for info in discount_info:
        draw.text((70, y_pos), info, fill='black', font=body_font)
        y_pos += 25
    
    # Save the image
    filename = "sample-policy-image.jpg"
    image.save(filename, "JPEG", quality=95)
    print(f"✅ Created test policy image: {filename}")
    return filename

if __name__ == "__main__":
    create_test_policy_image()
