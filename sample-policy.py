#!/usr/bin/env python3
"""
Script to create a sample PDF policy document for testing the insurance quote application.
This creates a realistic-looking insurance policy PDF that can be uploaded to test the system.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def create_sample_policy():
    filename = "sample-auto-policy.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    story = []
    
    # Title
    story.append(Paragraph("SAMPLE INSURANCE COMPANY", title_style))
    story.append(Paragraph("AUTO INSURANCE POLICY", title_style))
    story.append(Spacer(1, 20))
    
    # Policy Information
    story.append(Paragraph("POLICY INFORMATION", header_style))
    
    policy_data = [
        ["Policy Number:", "AUTO-2024-123456"],
        ["Coverage Type:", "Auto Insurance"],
        ["Policy Holder:", "John Smith"],
        ["Effective Date:", "January 1, 2024"],
        ["Expiration Date:", "January 1, 2025"],
        ["Premium:", "$1,450"],
        ["Deductible:", "$500"]
    ]
    
    policy_table = Table(policy_data, colWidths=[2*inch, 3*inch])
    policy_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(policy_table)
    story.append(Spacer(1, 20))
    
    # Vehicle Information
    story.append(Paragraph("VEHICLE INFORMATION", header_style))
    
    vehicle_data = [
        ["Year:", "2020"],
        ["Make:", "Toyota"],
        ["Model:", "Camry LE"],
        ["VIN:", "1234567890ABCDEFG"]
    ]
    
    vehicle_table = Table(vehicle_data, colWidths=[2*inch, 3*inch])
    vehicle_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(vehicle_table)
    story.append(Spacer(1, 20))
    
    # Driver Information
    story.append(Paragraph("DRIVER INFORMATION", header_style))
    
    driver_data = [
        ["Primary Driver:", "John Smith"],
        ["Age:", "32"],
        ["Years of Driving Experience:", "14 years"],
        ["License Number:", "D123456789"]
    ]
    
    driver_table = Table(driver_data, colWidths=[2*inch, 3*inch])
    driver_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(driver_table)
    story.append(Spacer(1, 20))
    
    # Coverage Details
    story.append(Paragraph("COVERAGE DETAILS", header_style))
    
    coverage_data = [
        ["Liability Coverage:", "$100,000/$300,000"],
        ["Comprehensive:", "$500 deductible"],
        ["Collision:", "$500 deductible"],
        ["Uninsured Motorist:", "$100,000/$300,000"]
    ]
    
    coverage_table = Table(coverage_data, colWidths=[2*inch, 3*inch])
    coverage_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(coverage_table)
    story.append(Spacer(1, 20))
    
    # Discounts Applied
    story.append(Paragraph("DISCOUNTS APPLIED", header_style))
    
    discount_data = [
        ["Safe Driver Discount:", "10%"],
        ["Multi-Vehicle Discount:", "5%"]
    ]
    
    discount_table = Table(discount_data, colWidths=[2*inch, 3*inch])
    discount_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(discount_table)
    story.append(Spacer(1, 30))
    
    # Contact Information
    story.append(Paragraph("CONTACT INFORMATION", header_style))
    story.append(Paragraph("Sample Insurance Company<br/>Phone: (555) 123-4567<br/>Agent: Jane Doe", styles['Normal']))
    
    story.append(Spacer(1, 30))
    story.append(Paragraph("This is a sample document for testing the QuickQuote Insurance application.", 
                          styles['Italic']))
    
    # Build PDF
    doc.build(story)
    print(f"Sample policy PDF created: {filename}")
    return filename

if __name__ == "__main__":
    create_sample_policy()
