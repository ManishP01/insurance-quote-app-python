"""
Multilingual Insurance Chatbot with Self-Service Capabilities
Supports language detection, translation, and insurance-specific operations
"""

import re
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import requests

class MultilingualInsuranceChatbot:
    def __init__(self):
        self.conversation_history = []
        self.user_language = None
        self.user_context = {}
        
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
                    r'\b(theek|accha|bura|paisa|paise|rupee|rupaye)\b'
                ],
                'language': 'hi'
            },
            'spanish_roman': {
                'patterns': [
                    r'\b(hola|como|estas|gracias|por|favor|que|es|soy|estoy)\b',
                    r'\b(bueno|malo|dinero|pesos|dolares)\b'
                ],
                'language': 'es'
            },
            'french_roman': {
                'patterns': [
                    r'\b(bonjour|comment|allez|vous|merci|sil|vous|plait|que|est|je|suis)\b',
                    r'\b(bon|mauvais|argent|euros)\b'
                ],
                'language': 'fr'
            }
        }
        
        # Insurance-specific intents
        self.insurance_intents = {
            'bill_payment': [
                'pay bill', 'payment', 'premium', 'due', 'bill', 'pagar', 'pago', 'paisa dena', 'payment karna'
            ],
            'policy_info': [
                'policy', 'coverage', 'what is covered', 'benefits', 'poliza', 'cobertura', 'policy kya hai'
            ],
            'claim_status': [
                'claim', 'status', 'claim status', 'reclamo', 'estado', 'claim ka status', 'claim kya hai'
            ],
            'premium_change': [
                'change premium', 'modify coverage', 'update policy', 'cambiar', 'modificar', 'premium change karna'
            ],
            'terms_explanation': [
                'what does', 'explain', 'meaning', 'que significa', 'explicar', 'matlab kya hai', 'explain karo'
            ]
        }

    def detect_language(self, text: str) -> str:
        """Detect language from text, including romanized scripts"""
        text_lower = text.lower()
        
        # Check for romanized languages
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

    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text between languages (mock implementation)"""
        # In production, use Google Translate API, Azure Translator, or similar
        
        if source_lang == target_lang:
            return text
        
        # Mock translations for demo - COMPLETE translations, not partial
        translations = {
            ('hi', 'en'): {
                'aap kaise hain': 'how are you',
                'namaste': 'hello',
                'dhanyawad': 'thank you',
                'mera bill kitna hai': 'what is my bill',
                'claim ka status kya hai': 'what is the claim status',
                'policy kya cover karta hai': 'what does the policy cover',
                'premium kitna hai': 'what is the premium',
                'deductible kya hai': 'what is deductible'
            },
            ('es', 'en'): {
                'hola': 'hello',
                'como estas': 'how are you',
                'gracias': 'thank you',
                'cuanto es mi factura': 'what is my bill',
                'estado del reclamo': 'claim status',
                'que cubre mi poliza': 'what does my policy cover',
                'cuanto es la prima': 'what is the premium'
            },
            ('en', 'hi'): {
                # Complete phrase translations first (more specific)
                "hello! i'm your insurance assistant. i can help you with:\n\n• bill payments\n• policy information\n• claim status\n• coverage explanations\n\nwhat would you like to know?": 
                "namaste! main aapka insurance assistant hun. main aapki madad kar sakta hun:\n\n• bill payments\n• policy information\n• claim status\n• coverage explanations\n\naap kya jaanna chahte hain?",
                
                # Individual word/phrase translations
                'hello': 'namaste',
                'how are you': 'aap kaise hain',
                'thank you': 'dhanyawad',
                'your bill is': 'aapka bill hai',
                'claim status is': 'claim ka status hai',
                'policy covers': 'policy cover karta hai',
                'premium due': 'premium due hai',
                'customer': 'customer',
                'policy': 'policy',
                'coverage details': 'coverage details',
                'liability': 'liability',
                'collision': 'collision',
                'comprehensive': 'comprehensive',
                'annual premium': 'saalik premium',
                'bill payment information': 'bill payment ki jaankari',
                'due date': 'due date',
                'would you like to': 'kya aap chahte hain',
                'pay full amount': 'pura amount pay karna',
                'set up payment plan': 'payment plan set karna',
                'view payment history': 'payment history dekhna',
                'reply with the number': 'number ke saath reply kariye',
                'claim status update': 'claim status update',
                'claim id': 'claim id',
                'type': 'type',
                'status': 'status',
                'filed': 'filed',
                'estimated amount': 'estimated amount',
                'next steps': 'agle steps',
                'adjuster will contact': 'adjuster contact karega',
                'within 24 hours': '24 ghante mein',
                'need to update': 'update karna hai',
                'have questions': 'sawal hain',
                'your policy coverage': 'aapka policy coverage',
                'need help understanding': 'samjhane mein madad chahiye',
                'just ask': 'bas puchiye',
                'explained': 'explain kiya gaya',
                'insurance assistant': 'insurance assistant',
                'i can help you with': 'main aapki madad kar sakta hun',
                'what would you like to know': 'aap kya jaanna chahte hain'
            },
            ('en', 'es'): {
                # Complete phrase translations first
                "hello! i'm your insurance assistant. i can help you with:\n\n• bill payments\n• policy information\n• claim status\n• coverage explanations\n\nwhat would you like to know?":
                "hola! soy su asistente de seguros. puedo ayudarle con:\n\n• pagos de facturas\n• informacion de poliza\n• estado de reclamos\n• explicaciones de cobertura\n\nque le gustaria saber?",
                
                # Individual translations
                'hello': 'hola',
                'how are you': 'como estas',
                'thank you': 'gracias',
                'your bill is': 'su factura es',
                'claim status is': 'el estado del reclamo es',
                'policy covers': 'la poliza cubre',
                'customer': 'cliente',
                'policy': 'poliza',
                'coverage details': 'detalles de cobertura',
                'liability': 'responsabilidad',
                'collision': 'colision',
                'comprehensive': 'integral',
                'annual premium': 'prima anual',
                'bill payment information': 'informacion de pago de factura',
                'due date': 'fecha de vencimiento',
                'would you like to': 'le gustaria',
                'pay full amount': 'pagar el monto completo',
                'set up payment plan': 'configurar plan de pago',
                'view payment history': 'ver historial de pagos',
                'reply with the number': 'responda con el numero',
                'claim status update': 'actualizacion del estado del reclamo',
                'claim id': 'id del reclamo',
                'type': 'tipo',
                'status': 'estado',
                'filed': 'presentado',
                'estimated amount': 'monto estimado',
                'next steps': 'proximos pasos',
                'adjuster will contact': 'el ajustador se comunicara',
                'within 24 hours': 'dentro de 24 horas',
                'need to update': 'necesita actualizar',
                'have questions': 'tiene preguntas',
                'your policy coverage': 'su cobertura de poliza',
                'need help understanding': 'necesita ayuda para entender',
                'just ask': 'solo pregunte',
                'explained': 'explicado',
                'insurance assistant': 'asistente de seguros',
                'i can help you with': 'puedo ayudarle con',
                'what would you like to know': 'que le gustaria saber'
            }
        }
        
        text_lower = text.lower()
        
        # For responses, do comprehensive translation
        if (source_lang, target_lang) in translations:
            translated_text = text_lower
            
            # Sort by length (longest first) to handle complete phrases before individual words
            translation_items = sorted(translations[(source_lang, target_lang)].items(), 
                                     key=lambda x: len(x[0]), reverse=True)
            
            # Apply all translations, starting with longest phrases
            for original, translated in translation_items:
                if original in translated_text:
                    translated_text = translated_text.replace(original, translated)
            
            # Preserve original formatting and structure
            if text != text_lower:  # Had uppercase/mixed case
                # Try to preserve some formatting
                if text.isupper():
                    translated_text = translated_text.upper()
                elif text.istitle():
                    translated_text = translated_text.title()
            
            return translated_text
        
        # For production, this would call actual translation API
        # For now, return original text (better than showing translation markers)
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
        """Main message processing pipeline"""
        # Step 1: Detect language
        detected_lang = self.detect_language(message)
        self.user_language = detected_lang
        
        # Step 2: Translate to English if needed (for processing only)
        if detected_lang != 'en':
            english_message = self.translate_text(message, detected_lang, 'en')
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
            user_response = self.translate_text(english_response, 'en', detected_lang)
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
            'customer_id': customer_id
        })
        
        # Return the response in user's language (no translation markers)
        return user_response

    def get_conversation_summary(self) -> Dict:
        """Get conversation analytics"""
        return {
            'total_messages': len(self.conversation_history),
            'languages_used': list(set([msg['detected_language'] for msg in self.conversation_history])),
            'intents_detected': list(set([msg['intent'] for msg in self.conversation_history])),
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
                'customer_id': msg.get('customer_id', 'unknown')
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
    chatbot = MultilingualInsuranceChatbot()
    
    print("🌍 Multilingual Insurance Chatbot Demo")
    print("=" * 50)
    
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
        print("-" * 30)
    
    # Show conversation summary
    print("\n📊 Conversation Summary:")
    summary = chatbot.get_conversation_summary()
    print(json.dumps(summary, indent=2))
