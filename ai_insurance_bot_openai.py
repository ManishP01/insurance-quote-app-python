"""
OpenAI-Enhanced AI Insurance Bot with Multilingual Support
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from ai_insurance_bot import AIInsuranceBot

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class AIInsuranceBotOpenAI(AIInsuranceBot):
    def __init__(self):
        super().__init__()
        self.openai_available = OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY')
        if self.openai_available:
            openai.api_key = os.getenv('OPENAI_API_KEY')
    
    def detect_language(self, message: str) -> str:
        """Detect language of the message - fallback to simple detection if OpenAI fails"""
        if not self.openai_available:
            return self._simple_language_detect(message)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user", 
                    "content": f"Detect the language of this text and respond with just the 2-letter language code: '{message}'"
                }],
                max_tokens=10,
                temperature=0
            )
            return response.choices[0].message.content.strip().lower()[:2]
        except Exception as e:
            print(f"OpenAI language detection failed: {e}")
            return self._simple_language_detect(message)
    
    def _simple_language_detect(self, message: str) -> str:
        """Simple language detection without OpenAI"""
        message_lower = message.lower()
        
        # Hindi detection - check for Hindi words first
        hindi_words = ['mera', 'kitna', 'hai', 'kya', 'kab', 'kaise', 'premium', 'bill', 'coverage', 
                      'ghar', 'pe', 'agar', 'ped', 'gira', 'toh', 'cover', 'karegi', 'policy']
        if any(word in message_lower for word in hindi_words):
            return 'hi'
        
        # Hindi script detection
        if any(char in message for char in 'अआइईउऊएऐओऔकखगघचछजझटठडढणतथदधनपफबभमयरलवशषसह'):
            return 'hi'
        
        # Spanish detection
        spanish_words = ['que', 'como', 'cuando', 'donde', 'por', 'para', 'con', 'sin', 'sobre', 'mi', 'tu', 'el', 'la', 'los', 'las', 'es', 'son', 'está', 'están']
        if any(word in message_lower for word in spanish_words):
            return 'es'
        
        # French detection
        french_words = ['que', 'qui', 'quand', 'où', 'pour', 'avec', 'sans', 'sur', 'mon', 'ma', 'le', 'la', 'les', 'est', 'sont', 'c\'est']
        if any(word in message_lower for word in french_words):
            return 'fr'
        
        return 'en'
    
    def translate_to_english(self, message: str, detected_lang: str) -> str:
        """Translate message to English for processing - fallback to simple translation"""
        if detected_lang == 'en':
            return message
            
        if not self.openai_available:
            return self._simple_translate(message, detected_lang)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user",
                    "content": f"Translate this to English: '{message}'"
                }],
                max_tokens=200,
                temperature=0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI translation failed: {e}")
            return self._simple_translate(message, detected_lang)
    
    def _simple_translate(self, message: str, lang: str) -> str:
        """Simple translation without OpenAI"""
        message_lower = message.lower()
        
        # Hindi translations
        if lang == 'hi':
            hindi_map = {
                'mera': 'my', 'premium': 'premium', 'kitna': 'how much', 'hai': 'is',
                'bill': 'bill', 'kab': 'when', 'kya': 'what', 'kaise': 'how',
                'coverage': 'coverage', 'liability': 'liability',
                'ghar': 'house', 'pe': 'on', 'agar': 'if', 'ped': 'tree',
                'gira': 'falls', 'toh': 'then', 'cover': 'covered', 'karegi': 'will',
                'policy': 'policy'
            }
            
            for hindi, english in hindi_map.items():
                message = message.replace(hindi, english)
            
            # Handle common patterns
            if 'mera premium kitna hai' in message_lower:
                return 'what is my premium amount'
            if 'bill kab' in message_lower:
                return 'when is my bill due'
            if 'ghar pe agar ped gira' in message_lower:
                return 'will I be covered if a tree falls on my house'
        
        # Spanish translations  
        elif lang == 'es':
            spanish_map = {
                'cual': 'what', 'cuál': 'what', 'es': 'is', 'mi': 'my',
                'prima': 'premium', 'factura': 'bill', 'cobertura': 'coverage',
                'incluye': 'include', 'responsabilidad': 'liability',
                'cuando': 'when', 'cuándo': 'when'
            }
            
            for spanish, english in spanish_map.items():
                message = message.replace(spanish, english)
            
            # Handle common patterns
            if 'cual es mi prima' in message_lower or 'cuál es mi prima' in message_lower:
                return 'what is my premium amount'
        
        return message
    
    def translate_response(self, response: str, target_lang: str) -> str:
        """Translate English response to target language"""
        if target_lang == 'en':
            return response
        
        # Simple translation for common languages
        return self._simple_response_translate(response, target_lang)
    
    def _simple_response_translate(self, response: str, lang: str) -> str:
        """Simple response translation without OpenAI"""
        if lang == 'hi':
            # Hindi translations for common insurance terms
            hindi_translations = {
                'Hi': 'नमस्ते',
                'Your Payment Information': 'आपकी भुगतान जानकारी',
                'Annual Premium': 'वार्षिक प्रीमियम',
                'Monthly Payment': 'मासिक भुगतान',
                'Payment Frequency': 'भुगतान आवृत्ति',
                'Premium Breakdown': 'प्रीमियम विवरण',
                'Dwelling': 'आवास',
                'Personal Property': 'व्यक्तिगत संपत्ति',
                'Liability': 'देयता',
                'Due Date': 'देय तिथि',
                'Amount Due': 'देय राशि',
                'Days Until Due': 'देय होने तक के दिन',
                'Next Payment': 'अगला भुगतान'
            }
            
            for english, hindi in hindi_translations.items():
                response = response.replace(english, hindi)
        
        elif lang == 'es':
            # Spanish translations
            spanish_translations = {
                'Hi': 'Hola',
                'Your Payment Information': 'Su Información de Pago',
                'Annual Premium': 'Prima Anual',
                'Monthly Payment': 'Pago Mensual',
                'Payment Frequency': 'Frecuencia de Pago',
                'Premium Breakdown': 'Desglose de Prima',
                'Dwelling': 'Vivienda',
                'Personal Property': 'Propiedad Personal',
                'Liability': 'Responsabilidad',
                'Due Date': 'Fecha de Vencimiento',
                'Amount Due': 'Cantidad Debida'
            }
            
            for english, spanish in spanish_translations.items():
                response = response.replace(english, spanish)
        
        return response
    
    def enhance_response_with_ai(self, response: str, customer: Dict, intent: str, detected_lang: str) -> str:
        """Enhance response with AI for better personalization"""
        if not self.openai_available:
            return response
        
        try:
            customer_name = customer['personal_info']['name']
            policy_type = customer['policy_details']['policy_type']
            
            prompt = f"""You are an insurance expert. Enhance this response to be more helpful and personalized for {customer_name} who has {policy_type}. Keep the same factual information but make it more conversational and helpful. Keep all formatting and emojis:

{response}"""
            
            openai_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.3
            )
            enhanced = openai_response.choices[0].message.content.strip()
            
            # Translate if needed
            if detected_lang != 'en':
                enhanced = self.translate_response(enhanced, detected_lang)
            
            return enhanced
        except:
            return response
    
    def handle_query(self, message: str, customer_id: str = "12345") -> Dict:
        """Enhanced query handling with multilingual support"""
        # Detect language
        detected_lang = self.detect_language(message)
        
        # Translate to English for processing
        english_message = self.translate_to_english(message, detected_lang)
        
        # Process with parent class
        result = super().handle_query(english_message, customer_id)
        
        # Translate response back to original language
        if detected_lang != 'en' and result['intent'] != 'unknown':
            result['response'] = self.translate_response(result['response'], detected_lang)
        
        # Add language info
        result['detected_language'] = detected_lang
        result['translation_method'] = 'openai' if self.openai_available else 'simple'
        
        return result

# Test the enhanced bot
if __name__ == "__main__":
    bot = AIInsuranceBotOpenAI()
    
    # Test multilingual queries
    test_queries = [
        ("What does my liability coverage include?", "12345"),
        ("¿Qué incluye mi cobertura de responsabilidad civil?", "12345"),
        ("Quand est due ma prochaine facture?", "67890"),
        ("मेरा बिल कब देय है?", "12345")
    ]
    
    for query, customer_id in test_queries:
        print(f"\n🔍 Query: {query}")
        result = bot.handle_query(query, customer_id)
        print(f"🌍 Language: {result['detected_language']}")
        print(f"💬 Response: {result['response'][:100]}...")
