"""
AI Insurance Bot with Customer Data and Knowledge Base
Handles customer queries with accuracy and provides supporting documentation
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class AIInsuranceBot:
    def __init__(self):
        self.customer_data = self.load_customer_data()
        self.knowledge_base = self.load_knowledge_base()
        
    def load_customer_data(self) -> Dict:
        """Load customer data from JSON file"""
        try:
            with open('customer_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def load_knowledge_base(self) -> Dict:
        """Load insurance knowledge base from JSON file"""
        try:
            with open('insurance_knowledge.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def get_customer_info(self, customer_id: str) -> Optional[Dict]:
        """Get customer information by ID"""
        return self.customer_data.get(f"customer_{customer_id}")
    
    def detect_intent(self, message: str) -> Tuple[str, Dict]:
        """Detect user intent and extract relevant information"""
        message_lower = message.lower()
        
        # Scenario-based questions (check FIRST before coverage explanations)
        if any(phrase in message_lower for phrase in ['will i be covered', 'am i covered', 'does my insurance cover', 'what if', 'if i', 'would i be covered']):
            return 'coverage_scenario', {'scenario': message}
        
        # Coverage explanation intents
        if any(word in message_lower for word in ['coverage', 'cover', 'covered', 'protection']):
            if any(word in message_lower for word in ['liability', 'liable']):
                return 'explain_coverage', {'coverage_type': 'liability'}
            elif any(word in message_lower for word in ['collision', 'hit', 'crash']):
                return 'explain_coverage', {'coverage_type': 'collision'}
            elif any(word in message_lower for word in ['comprehensive', 'theft', 'steal', 'weather', 'hail']):
                return 'explain_coverage', {'coverage_type': 'comprehensive'}
            elif any(word in message_lower for word in ['uninsured', 'underinsured']):
                return 'explain_coverage', {'coverage_type': 'uninsured_motorist'}
            elif any(word in message_lower for word in ['dwelling', 'house', 'home structure']):
                return 'explain_coverage', {'coverage_type': 'dwelling'}
            elif any(word in message_lower for word in ['personal property', 'belongings', 'stuff']):
                return 'explain_coverage', {'coverage_type': 'personal_property'}
            else:
                return 'explain_coverage', {'coverage_type': 'general'}
        
        # Bill and payment intents
        if any(word in message_lower for word in ['bill', 'payment', 'due', 'pay', 'amount owed']):
            if any(word in message_lower for word in ['when', 'due date', 'next']):
                return 'bill_due_date', {}
            elif any(word in message_lower for word in ['how much', 'amount', 'cost']):
                return 'bill_amount', {}
            elif any(word in message_lower for word in ['method', 'how to pay', 'payment options']):
                return 'payment_methods', {}
            else:
                return 'bill_general', {}
        
        # Premium and rate questions
        if any(phrase in message_lower for phrase in ['premium went up', 'rate increase', 'why did my premium', 'cost more']):
            return 'premium_increase', {}
        
        # Policy terms
        if any(word in message_lower for word in ['deductible', 'policy period', 'exclusion', 'term']):
            if 'deductible' in message_lower:
                return 'explain_term', {'term': 'deductible'}
            elif any(word in message_lower for word in ['period', 'length', 'duration']):
                return 'explain_term', {'term': 'policy_period'}
            elif 'exclusion' in message_lower:
                return 'explain_term', {'term': 'exclusions'}
            else:
                return 'explain_term', {'term': 'premium'}
        
        # Coverage changes
        if any(phrase in message_lower for phrase in ['change coverage', 'modify policy', 'add coverage', 'remove coverage']):
            return 'coverage_change', {}
        
        # Claims
        if any(word in message_lower for word in ['claim', 'accident', 'damage']):
            return 'claims_info', {}
        
        return 'unknown', {}
    
    def handle_query(self, message: str, customer_id: str = "12345") -> Dict:
        """Main function to handle customer queries with personalization"""
        intent, params = self.detect_intent(message)
        customer = self.get_customer_info(customer_id)
        
        if not customer:
            return {
                'response': "I'm sorry, I couldn't find your account information. Please contact customer service at (555) 123-4567.",
                'intent': 'no_customer_data',
                'supporting_document': None,
                'connect_to_agent': True
            }
        
        # Add personalized greeting for first interaction
        customer_name = customer['personal_info']['name']
        policy_type = customer['policy_details']['policy_type']
        
        # Route to appropriate handler with customer context
        handlers = {
            'explain_coverage': self.handle_coverage_explanation,
            'coverage_scenario': self.handle_coverage_scenario,
            'bill_due_date': self.handle_bill_due_date,
            'bill_amount': self.handle_bill_amount,
            'payment_methods': self.handle_payment_methods,
            'bill_general': self.handle_bill_general,
            'premium_increase': self.handle_premium_increase,
            'explain_term': self.handle_term_explanation,
            'coverage_change': self.handle_coverage_change,
            'claims_info': self.handle_claims_info
        }
        
        if intent in handlers:
            result = handlers[intent](customer, params)
            # Add customer context to response
            if not result['response'].startswith('**'):
                result['response'] = f"Hi {customer_name}! " + result['response']
            return result
        else:
            return {
                'response': f"Hi {customer_name}, I don't have specific information about that question. Let me connect you with one of our licensed agents who can provide accurate, personalized assistance for your {policy_type} policy.",
                'intent': 'unknown',
                'supporting_document': None,
                'connect_to_agent': True
            }
    
    def handle_coverage_explanation(self, customer: Dict, params: Dict) -> Dict:
        """Explain insurance coverage types"""
        coverage_type = params.get('coverage_type', 'general')
        
        if coverage_type == 'general':
            # Show all customer's coverages
            coverages = customer['coverage_details']
            response = f"**Your Current Coverage Summary:**\n\n"
            
            for coverage, details in coverages.items():
                if coverage == 'liability':
                    response += f"🛡️ **Liability Coverage**: {details['bodily_injury']} bodily injury, {details['property_damage']} property damage\n"
                elif coverage == 'collision':
                    response += f"🚗 **Collision Coverage**: {details['coverage_limit']} limit with ${details['deductible']} deductible\n"
                elif coverage == 'comprehensive':
                    response += f"🌟 **Comprehensive Coverage**: {details['coverage_limit']} limit with ${details['deductible']} deductible\n"
                elif coverage == 'dwelling':
                    response += f"🏠 **Dwelling Coverage**: {details['coverage_limit']} to rebuild your home\n"
                elif coverage == 'personal_property':
                    response += f"📦 **Personal Property**: {details['coverage_limit']} for your belongings\n"
            
            return {
                'response': response,
                'intent': 'coverage_explanation',
                'supporting_document': 'Policy Declarations Page',
                'connect_to_agent': False
            }
        
        # Specific coverage explanation
        if coverage_type in self.knowledge_base['coverage_explanations']:
            coverage_info = self.knowledge_base['coverage_explanations'][coverage_type]
            
            response = f"**{coverage_type.replace('_', ' ').title()} Coverage Explanation:**\n\n"
            response += f"📋 **What it is**: {coverage_info['description']}\n\n"
            response += f"✅ **What it covers**:\n"
            for item in coverage_info['what_it_covers']:
                response += f"• {item}\n"
            response += f"\n❌ **What it doesn't cover**:\n"
            for item in coverage_info['what_it_doesnt_cover']:
                response += f"• {item}\n"
            
            # Add customer's specific coverage if available
            if coverage_type in customer['coverage_details']:
                customer_coverage = customer['coverage_details'][coverage_type]
                response += f"\n**Your Current {coverage_type.title()} Coverage:**\n"
                for key, value in customer_coverage.items():
                    if key != 'premium_portion':
                        response += f"• {key.replace('_', ' ').title()}: {value}\n"
            
            return {
                'response': response,
                'intent': 'coverage_explanation',
                'supporting_document': coverage_info['document_reference'],
                'connect_to_agent': False
            }
        
        return self.handle_unknown_query(f"coverage explanation for {coverage_type}")
    
    def handle_coverage_scenario(self, customer: Dict, params: Dict) -> Dict:
        """Handle scenario-based coverage questions with decisive answers"""
        scenario = params['scenario'].lower()
        customer_name = customer['personal_info']['name']
        
        # Tree falls on house scenario
        if any(keyword in scenario for keyword in ['tree falls', 'tree fall', 'tree on house', 'tree damage']):
            if customer['policy_details']['policy_type'] == 'Home Insurance':
                dwelling_coverage = customer['coverage_details']['dwelling']
                response = f"**✅ YES, {customer_name}, you ARE covered!**\n\n"
                response += f"🏠 **Your Dwelling Coverage**: {dwelling_coverage['coverage_limit']}\n"
                response += f"💰 **Your Deductible**: ${customer['policy_details']['deductible']}\n\n"
                response += f"**What happens:**\n"
                response += f"• Insurance pays for house repairs after your ${customer['policy_details']['deductible']} deductible\n"
                response += f"• Tree removal from structure is covered\n"
                response += f"• Temporary living expenses if house is uninhabitable\n\n"
                response += f"**Next steps if this happens:**\n"
                response += f"1. Ensure safety first\n"
                response += f"2. Call claims: (555) CLAIMS-1\n"
                response += f"3. Document damage with photos\n"
                
                return {
                    'response': response,
                    'intent': 'coverage_scenario',
                    'supporting_document': 'Policy Section 1: Dwelling Coverage',
                    'connect_to_agent': False
                }
            else:
                response = f"**❌ NO, {customer_name}, this isn't covered by your Auto Insurance policy.**\n\n"
                response += f"🚗 You have Auto Insurance, but tree damage to a house requires Home Insurance.\n\n"
                response += f"💡 **You need**: Home Insurance with Dwelling Coverage"
                
                return {
                    'response': response,
                    'intent': 'coverage_scenario',
                    'supporting_document': None,
                    'connect_to_agent': True
                }
        
        # Deer collision scenario
        if any(keyword in scenario for keyword in ['deer', 'animal', 'hit deer', 'hit animal']):
            if 'comprehensive' in customer['coverage_details']:
                comp_coverage = customer['coverage_details']['comprehensive']
                response = f"**✅ YES, {customer_name}, you ARE covered!**\n\n"
                response += f"🦌 **Animal collisions are covered by Comprehensive Coverage**\n"
                response += f"🚗 **Your Coverage**: {comp_coverage['coverage_limit']}\n"
                response += f"💰 **Your Deductible**: {comp_coverage['deductible']}\n\n"
                response += f"**What you pay**: {comp_coverage['deductible']} deductible\n"
                response += f"**Insurance pays**: Repair costs above your deductible\n"
            else:
                response = f"**❌ NO, {customer_name}, you are NOT covered.**\n\n"
                response += f"🦌 Animal collisions require Comprehensive Coverage\n"
                response += f"📋 **You currently have**: {', '.join(customer['coverage_details'].keys())}\n"
                response += f"💡 **To be covered**: Add Comprehensive Coverage to your policy"
            
            return {
                'response': response,
                'intent': 'coverage_scenario',
                'supporting_document': 'Policy Section 3: Comprehensive Coverage',
                'connect_to_agent': False
            }
        
        # Rear-ended by uninsured driver
        if any(phrase in scenario for phrase in ['uninsured driver', 'no insurance', 'hit by uninsured']):
            if 'uninsured_motorist' in customer['coverage_details']:
                um_coverage = customer['coverage_details']['uninsured_motorist']
                response = f"**✅ YES, {customer_name}, you ARE protected!**\n\n"
                response += f"🛡️ **Your Uninsured Motorist Coverage**: {um_coverage['bodily_injury']}\n"
                response += f"💰 **What you pay**: Usually no deductible for UM coverage\n"
                response += f"**Insurance covers**: Your medical bills, lost wages, pain & suffering\n"
            else:
                response = f"**❌ NO, {customer_name}, you are NOT protected.**\n\n"
                response += f"⚠️ Without Uninsured Motorist coverage, you'd pay out-of-pocket\n"
                response += f"💡 **Recommendation**: Add Uninsured Motorist coverage immediately"
            
            return {
                'response': response,
                'intent': 'coverage_scenario',
                'supporting_document': 'Policy Section 4: Uninsured Motorist Coverage',
                'connect_to_agent': False
            }
        
        # If no specific scenario matched, connect to agent
        return {
            'response': f"Hi {customer_name}, I need more details about your specific scenario to give you a definitive answer. Let me connect you with a licensed agent who can review your exact policy terms.",
            'intent': 'unknown_scenario',
            'supporting_document': None,
            'connect_to_agent': True
        }
    
    def handle_bill_due_date(self, customer: Dict, params: Dict) -> Dict:
        """Handle bill due date questions"""
        due_date = customer['policy_details']['next_due_date']
        amount = customer['policy_details']['monthly_payment']
        
        # Calculate days until due
        due_datetime = datetime.strptime(due_date, '%Y-%m-%d')
        days_until_due = (due_datetime - datetime.now()).days
        
        response = f"💳 **Your Next Payment Information:**\n\n"
        response += f"📅 **Due Date**: {due_datetime.strftime('%B %d, %Y')}\n"
        response += f"💰 **Amount Due**: ${amount:.2f}\n"
        
        if days_until_due > 0:
            response += f"⏰ **Days Until Due**: {days_until_due} days\n\n"
        elif days_until_due == 0:
            response += f"🚨 **Due Today!**\n\n"
        else:
            response += f"⚠️ **Overdue by {abs(days_until_due)} days**\n\n"
        
        response += f"💡 **Payment Methods**: {', '.join(customer['policy_details']['payment_methods'])}"
        
        return {
            'response': response,
            'intent': 'bill_due_date',
            'supporting_document': 'Policy Declarations Page - Payment Schedule',
            'connect_to_agent': False
        }
    
    def handle_bill_amount(self, customer: Dict, params: Dict) -> Dict:
        """Handle bill amount questions"""
        policy = customer['policy_details']
        
        response = f"💰 **Your Payment Information:**\n\n"
        response += f"📋 **Annual Premium**: ${policy['premium_amount']:.2f}\n"
        response += f"💳 **Monthly Payment**: ${policy['monthly_payment']:.2f}\n"
        response += f"📅 **Payment Frequency**: {policy['payment_frequency'].title()}\n\n"
        
        response += f"**Premium Breakdown by Coverage:**\n"
        for coverage, details in customer['coverage_details'].items():
            if 'premium_portion' in details:
                response += f"• {coverage.replace('_', ' ').title()}: ${details['premium_portion']:.2f}\n"
        
        return {
            'response': response,
            'intent': 'bill_amount',
            'supporting_document': 'Policy Declarations Page - Premium Breakdown',
            'connect_to_agent': False
        }
    
    def handle_payment_methods(self, customer: Dict, params: Dict) -> Dict:
        """Handle payment method questions"""
        methods = customer['policy_details']['payment_methods']
        
        response = f"💳 **Available Payment Methods:**\n\n"
        for i, method in enumerate(methods, 1):
            response += f"{i}. {method}\n"
        
        response += f"\n💡 **Quick Payment Options:**\n"
        response += f"• Online: Visit our website or mobile app\n"
        response += f"• Phone: Call (555) 123-4567\n"
        response += f"• Auto-pay: Set up automatic payments to never miss a due date\n"
        
        return {
            'response': response,
            'intent': 'payment_methods',
            'supporting_document': 'Policy Terms - Payment Options',
            'connect_to_agent': False
        }
    
    def handle_bill_general(self, customer: Dict, params: Dict) -> Dict:
        """Handle general billing questions"""
        return self.handle_bill_due_date(customer, params)
    
    def handle_premium_increase(self, customer: Dict, params: Dict) -> Dict:
        """Explain premium increases"""
        history = customer['premium_history']
        
        if len(history) >= 2:
            current = history[0]
            previous = history[1]
            increase = current['amount'] - previous['amount']
            
            response = f"📈 **Premium Change Analysis:**\n\n"
            response += f"📊 **Previous Premium**: ${previous['amount']:.2f}\n"
            response += f"📊 **Current Premium**: ${current['amount']:.2f}\n"
            response += f"📈 **Increase**: ${increase:.2f}\n\n"
            response += f"📋 **Reason for Change**: {current['change_reason']}\n\n"
            
            response += f"**Common factors that affect premiums:**\n"
            if customer['policy_details']['policy_type'] == 'Auto Insurance':
                for factor in self.knowledge_base['premium_factors']['auto_factors']:
                    response += f"• {factor['factor']}: {factor['impact']}\n"
            else:
                for factor in self.knowledge_base['premium_factors']['home_factors']:
                    response += f"• {factor['factor']}: {factor['impact']}\n"
        else:
            response = "I don't see any premium change history. Let me connect you with an agent to discuss your premium."
            return {
                'response': response,
                'intent': 'premium_increase',
                'supporting_document': None,
                'connect_to_agent': True
            }
        
        return {
            'response': response,
            'intent': 'premium_increase',
            'supporting_document': 'Policy Terms - Premium Calculation',
            'connect_to_agent': False
        }
    
    def handle_term_explanation(self, customer: Dict, params: Dict) -> Dict:
        """Explain policy terms"""
        term = params.get('term', 'premium')
        
        if term in self.knowledge_base['policy_terms']:
            term_info = self.knowledge_base['policy_terms'][term]
            
            response = f"📚 **{term.replace('_', ' ').title()} Explanation:**\n\n"
            response += f"📋 **Definition**: {term_info['definition']}\n\n"
            response += f"💡 **How it works**: {term_info['how_it_works']}\n\n"
            
            if 'example' in term_info:
                response += f"📝 **Example**: {term_info['example']}\n\n"
            
            # Add customer-specific information
            if term == 'deductible':
                response += f"**Your Current Deductible**: ${customer['policy_details']['deductible']}\n"
            elif term == 'premium':
                response += f"**Your Current Premium**: ${customer['policy_details']['premium_amount']:.2f} annually\n"
            
            return {
                'response': response,
                'intent': 'term_explanation',
                'supporting_document': term_info['document_reference'],
                'connect_to_agent': False
            }
        
        return self.handle_unknown_query(f"term explanation for {term}")
    
    def handle_coverage_change(self, customer: Dict, params: Dict) -> Dict:
        """Handle coverage change questions"""
        response = f"🔄 **Making Coverage Changes:**\n\n"
        response += f"To modify your policy coverage, you have several options:\n\n"
        response += f"📞 **Call us**: (555) 123-4567 to speak with an agent\n"
        response += f"💻 **Online**: Log into your account portal\n"
        response += f"📱 **Mobile App**: Use our mobile app for quick changes\n\n"
        response += f"**Important Notes:**\n"
        response += f"• Coverage changes may affect your premium\n"
        response += f"• Changes typically take effect at your next renewal\n"
        response += f"• Some changes may require underwriting review\n\n"
        response += f"Would you like me to connect you with an agent to discuss specific changes?"
        
        return {
            'response': response,
            'intent': 'coverage_change',
            'supporting_document': 'Policy Terms - Coverage Modifications',
            'connect_to_agent': True
        }
    
    def handle_claims_info(self, customer: Dict, params: Dict) -> Dict:
        """Handle claims-related questions"""
        claims = customer.get('claims_history', [])
        
        if claims:
            response = f"📋 **Your Claims History:**\n\n"
            for claim in claims:
                response += f"🔍 **Claim ID**: {claim['claim_id']}\n"
                response += f"📅 **Date**: {claim['date']}\n"
                response += f"📝 **Type**: {claim['type']}\n"
                response += f"📊 **Status**: {claim['status']}\n"
                response += f"💰 **Amount Paid**: ${claim['amount_paid']:.2f}\n"
                response += f"📄 **Description**: {claim['description']}\n\n"
        else:
            response = f"✅ **Great news!** You have no claims on record.\n\n"
        
        response += f"**To file a new claim:**\n"
        response += f"📞 **24/7 Claims Hotline**: (555) CLAIMS-1\n"
        response += f"💻 **Online**: File through your account portal\n"
        response += f"📱 **Mobile App**: Quick claim filing available\n"
        
        return {
            'response': response,
            'intent': 'claims_info',
            'supporting_document': 'Policy Section: Claims Process',
            'connect_to_agent': False
        }
    
    def handle_unknown_query(self, message: str) -> Dict:
        """Handle queries that don't match any intent"""
        return {
            'response': "I don't have specific information about that question. Let me connect you with one of our licensed agents who can provide accurate, personalized assistance.",
            'intent': 'unknown',
            'supporting_document': None,
            'connect_to_agent': True
        }

# Test the bot
if __name__ == "__main__":
    bot = AIInsuranceBot()
    
    # Test queries
    test_queries = [
        "What does my liability coverage include?",
        "When is my next bill due?",
        "Will I be covered if I hit a deer?",
        "Why did my premium go up?",
        "What is a deductible?",
        "How do I change my coverage?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = bot.handle_query(query)
        print(f"Response: {result['response'][:100]}...")
        print(f"Document: {result['supporting_document']}")
        print(f"Connect to agent: {result['connect_to_agent']}")
