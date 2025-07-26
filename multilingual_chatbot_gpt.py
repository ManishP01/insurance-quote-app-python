"""
Enhanced Multilingual Insurance Chatbot with OpenAI GPT Translation
Context-aware translation for insurance terminology and professional communication
"""

import re
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import openai
import os

class GPTMultilingualInsuranceChatbot:
    def __init__(self):
        self.conversation_history = []
        self.user_language = None
        self.user_context = {}
        
        # Initialize OpenAI (you'll need to set your API key)
        openai.api_key = os.getenv('OPENAI_API_KEY')  # Set this environment variable
        
        # Translation cache for common phrases (performance optimization)
        self.translation_cache = {}
        
        # Mock customer database
        self.customers = {
            "12345": {
                "name": "John Smith",
                "policy_number": "POL-12345",
                "premium": 1200.00,
                "due_date": "2024-08-15",
                "coverage": {
                    "liability": "$100,000",
                    "collision": "$50,000",
                    "comprehensive": "$25,000"
                },
                "claims": [
                    {
                        "claim_id": "CLM-789123",
                        "status": "Under Review",
                        "date": "2024-07-10",
                        "type": "Auto Collision",
                        "amount": "$3,500"
                    }
                ]
            }
        }
        
        # Language patterns for script detection
        self.language_patterns = {
            'hindi_roman': {
                'patterns': [
                    r'\b(aap|kaise|hain|namaste|dhanyawad|kya|hai|main|hoon)\b',
                    r'\b(theek|accha|bura|paisa|paise|rupee|rupaye)\b',
                    r'\b(mera|meri|mere|aapka|aapki|aapke)\b'
                ],
                'language': 'hi'
            },
            'spanish_roman': {
                'patterns': [
                    r'\b(hola|como|estas|gracias|por|favor|que|es|soy|estoy)\b',
                    r'\b(bueno|malo|dinero|pesos|dolares|cuanto|cuando)\b'
                ],
                'language': 'es'
            },
            'french_roman': {
                'patterns': [
                    r'\b(bonjour|comment|allez|vous|merci|sil|vous|plait|que|est|je|suis)\b',
                    r'\b(bon|mauvais|argent|euros|combien|quand)\b'
                ],
                'language': 'fr'
            }
        }
        
        # Insurance-specific intents
        self.insurance_intents = {
            'bill_payment': [
                'pay bill', 'payment', 'premium', 'due', 'bill', 'pagar', 'pago', 'paisa dena', 'payment karna',
                'factura', 'cuenta', 'billing', 'invoice'
            ],
            'policy_info': [
                'policy', 'coverage', 'what is covered', 'benefits', 'poliza', 'cobertura', 'policy kya hai',
                'insurance', 'seguro', 'bima'
            ],
            'claim_status': [
                'claim', 'status', 'claim status', 'reclamo', 'estado', 'claim ka status', 'claim kya hai',
                'accident', 'incident', 'damage'
            ],
            'premium_change': [
                'change premium', 'modify coverage', 'update policy', 'cambiar', 'modificar', 'premium change karna'
            ],
            'terms_explanation': [
                'what does', 'explain', 'meaning', 'que significa', 'explicar', 'matlab kya hai', 'explain karo',
                'define', 'definition'
            ]
        }

    def detect_language(self, text: str) -> str:
        """Detect language from text, including romanized scripts"""
        text_lower = text.lower()
        
        # Check for romanized languages first
        for lang_key, lang_data in self.language_patterns.items():
            for pattern in lang_data['patterns']:
                if re.search(pattern, text_lower):
                    return lang_data['language']
        
        # Check for non-Latin scripts
        if re.search(r'[\u0900-\u097F]', text):  # Devanagari (Hindi)
            return 'hi'
        elif re.search(r'[\u4e00-\u9fff]', text):  # Chinese
            return 'zh'
        elif re.search(r'[\u0600-\u06ff]', text):  # Arabic
            return 'ar'
        elif re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):  # Japanese
            return 'ja'
        
        # Default to English
        return 'en'

    def gpt_translate(self, text: str, source_lang: str, target_lang: str, context: str = "insurance") -> str:
        """Use OpenAI GPT for context-aware translation"""
        
        if source_lang == target_lang:
            return text
        
        # Check cache first
        cache_key = f"{source_lang}_{target_lang}_{hash(text)}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        # Language name mapping
        lang_names = {
            'en': 'English',
            'hi': 'Hindi',
            'es': 'Spanish',
            'fr': 'French',
            'zh': 'Chinese',
            'ar': 'Arabic',
            'ja': 'Japanese'
        }
        
        source_name = lang_names.get(source_lang, source_lang)
        target_name = lang_names.get(target_lang, target_lang)
        
        # Create context-aware prompt
        prompt = f"""
You are a professional translator specializing in insurance and financial services.

Task: Translate the following {context} text from {source_name} to {target_name}.

Requirements:
1. Maintain professional, customer-service tone
2. Use appropriate insurance terminology
3. Keep formatting (bullets, numbers, etc.)
4. Ensure cultural appropriateness
5. If romanized script (like Hindi in English letters), translate meaning not just words

Text to translate:
{text}

Translation:"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a professional translator specializing in insurance and customer service communications. Provide accurate, culturally appropriate translations that maintain the professional tone and insurance terminology."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.3  # Lower temperature for more consistent translations
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            # Cache the translation
            self.translation_cache[cache_key] = translated_text
            
            return translated_text
            
        except Exception as e:
            print(f"GPT Translation error: {e}")
            # Fallback to original text if translation fails
            return text

    def detect_intent(self, text: str) -> str:
        """Detect user intent from translated text"""
        text_lower = text.lower()
        
        for intent, keywords in self.insurance_intents.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return intent
        
        return 'general_inquiry'

    def handle_bill_payment(self, customer_id: str) -> str:
        """Handle bill payment requests"""
        if customer_id not in self.customers:
            return "I couldn't find your account. Please provide your policy number."
        
        customer = self.customers[customer_id]
        premium = customer['premium']
        due_date = customer['due_date']
        
        return f"""💳 **Bill Payment Information**
        
**Customer:** {customer['name']}
**Policy:** {customer['policy_number']}
**Premium Due:** ${premium:.2f}
**Due Date:** {due_date}

Would you like to:
1. Pay full amount (${premium:.2f})
2. Set up payment plan
3. View payment history

Reply with the number of your choice."""

    def handle_policy_info(self, customer_id: str) -> str:
        """Handle policy information requests"""
        if customer_id not in self.customers:
            return "Please provide your policy number to view coverage details."
        
        customer = self.customers[customer_id]
        coverage = customer['coverage']
        
        return f"""📋 **Your Policy Coverage**
        
**Policy:** {customer['policy_number']}
**Coverage Details:**
• Liability: {coverage['liability']}
• Collision: {coverage['collision']}
• Comprehensive: {coverage['comprehensive']}

**Annual Premium:** ${customer['premium']:.2f}

Need help understanding any coverage? Just ask!"""

    def handle_claim_status(self, customer_id: str) -> str:
        """Handle claim status requests"""
        if customer_id not in self.customers:
            return "Please provide your policy number to check claim status."
        
        customer = self.customers[customer_id]
        claims = customer.get('claims', [])
        
        if not claims:
            return "You don't have any active claims. Need to file a new claim?"
        
        claim = claims[0]  # Most recent claim
        return f"""🔍 **Claim Status Update**
        
**Claim ID:** {claim['claim_id']}
**Type:** {claim['type']}
**Status:** {claim['status']}
**Filed:** {claim['date']}
**Estimated Amount:** {claim['amount']}

**Next Steps:** An adjuster will contact you within 24 hours.

Need to update your claim or have questions?"""

    def handle_terms_explanation(self, term: str) -> str:
        """Explain insurance terms in simple language"""
        explanations = {
            'deductible': "A deductible is the amount you pay out of pocket before insurance covers the rest. For example, with a $500 deductible, you pay the first $500 of any claim.",
            'premium': "Your premium is the amount you pay (monthly, quarterly, or annually) to keep your insurance active.",
            'liability': "Liability coverage pays for damage you cause to other people or their property in an accident.",
            'collision': "Collision coverage pays to repair your vehicle if it's damaged in an accident, regardless of who's at fault.",
            'comprehensive': "Comprehensive coverage protects against non-collision damage like theft, vandalism, weather, or hitting an animal."
        }
        
        term_lower = term.lower()
        for key, explanation in explanations.items():
            if key in term_lower:
                return f"📖 **{key.title()} Explained:**\n\n{explanation}"
        
        return f"I'd be happy to explain '{term}' for you. Could you be more specific about which insurance term you'd like me to clarify?"

    def process_message(self, message: str, customer_id: str = "12345") -> str:
        """Main message processing pipeline with GPT translation"""
        # Step 1: Detect language
        detected_lang = self.detect_language(message)
        self.user_language = detected_lang
        
        # Step 2: Translate to English if needed (for processing only)
        if detected_lang != 'en':
            english_message = self.gpt_translate(message, detected_lang, 'en', "customer inquiry")
        else:
            english_message = message
        
        # Step 3: Detect intent
        intent = self.detect_intent(english_message)
        
        # Step 4: Generate response based on intent (always in English first)
        if intent == 'bill_payment':
            english_response = self.handle_bill_payment(customer_id)
        elif intent == 'policy_info':
            english_response = self.handle_policy_info(customer_id)
        elif intent == 'claim_status':
            english_response = self.handle_claim_status(customer_id)
        elif intent == 'terms_explanation':
            english_response = self.handle_terms_explanation(english_message)
        else:
            english_response = f"Hello! I'm your insurance assistant. I can help you with:\n\n• Bill payments\n• Policy information\n• Claim status\n• Coverage explanations\n\nWhat would you like to know?"
        
        # Step 5: Translate response to user's language (seamlessly)
        if detected_lang != 'en':
            user_response = self.gpt_translate(english_response, 'en', detected_lang, "insurance response")
        else:
            user_response = english_response
        
        # Step 6: Store conversation with BOTH versions
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user_message_original': message,  # What user actually typed
            'user_message_english': english_message,  # For agent/history reference
            'detected_language': detected_lang,
            'intent': intent,
            'bot_response_english': english_response,  # For agent/history reference
            'bot_response_user_language': user_response,  # What user sees
            'customer_id': customer_id,
            'translation_method': 'gpt'
        })
        
        # Return the response in user's language (no translation markers)
        return user_response

    def get_conversation_summary(self) -> Dict:
        """Get conversation analytics"""
        return {
            'total_messages': len(self.conversation_history),
            'languages_used': list(set([msg['detected_language'] for msg in self.conversation_history])),
            'intents_detected': list(set([msg['intent'] for msg in self.conversation_history])),
            'translation_method': 'gpt',
            'conversation_history': self.conversation_history[-10:]  # Last 10 messages
        }

    def get_agent_view(self) -> List[Dict]:
        """Get conversation history in English for agent handoff"""
        agent_history = []
        for msg in self.conversation_history:
            agent_history.append({
                'timestamp': msg['timestamp'],
                'customer_language': msg['detected_language'],
                'customer_said': msg['user_message_english'],  # English version for agent
                'customer_original': msg['user_message_original'],  # Original for reference
                'intent_detected': msg['intent'],
                'bot_responded': msg['bot_response_english'],  # English version for agent
                'customer_saw': msg['bot_response_user_language'],  # What customer actually saw
                'customer_id': msg.get('customer_id', 'unknown'),
                'translation_method': msg.get('translation_method', 'gpt')
            })
        return agent_history

    def get_customer_view(self) -> List[Dict]:
        """Get conversation history as customer sees it (in their language)"""
        customer_history = []
        for msg in self.conversation_history:
            customer_history.append({
                'timestamp': msg['timestamp'],
                'user_message': msg['user_message_original'],
                'bot_response': msg['bot_response_user_language'],
                'language': msg['detected_language']
            })
        return customer_history

# Demo usage
if __name__ == "__main__":
    # Note: You need to set OPENAI_API_KEY environment variable
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Please set OPENAI_API_KEY environment variable to test GPT translation")
        print("Example: export OPENAI_API_KEY='your-api-key-here'")
        exit(1)
    
    chatbot = GPTMultilingualInsuranceChatbot()
    
    print("🌍 GPT-Powered Multilingual Insurance Chatbot Demo")
    print("=" * 60)
    
    # Test messages in different languages
    test_messages = [
        "Hello, how are you?",
        "aap kaise hain",  # Hindi in Roman script
        "mera bill kitna hai",  # "What is my bill" in Hindi
        "claim ka status kya hai",  # "What is claim status" in Hindi
        "what does deductible mean",
        "hola, como estas",  # Spanish
        "cuanto es mi factura"  # "What is my bill" in Spanish
    ]
    
    for message in test_messages:
        print(f"\n👤 User: {message}")
        response = chatbot.process_message(message)
        print(f"🤖 Bot: {response}")
        print("-" * 40)
    
    # Show conversation summary
    print("\n📊 Conversation Summary:")
    summary = chatbot.get_conversation_summary()
    print(json.dumps(summary, indent=2))
