"""
Full OpenAI-Enhanced AI Insurance Bot with Natural Language Processing
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

class AIInsuranceBotOpenAIFull(AIInsuranceBot):
    def __init__(self):
        super().__init__()
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY')
        self.openai_available = OPENAI_AVAILABLE and api_key and api_key.startswith('sk-')
        
        if self.openai_available:
            openai.api_key = api_key
            print("✅ OpenAI integration enabled")
        else:
            print("⚠️ OpenAI not available, using fallback methods")
            if not OPENAI_AVAILABLE:
                print("   - OpenAI package not installed")
            elif not api_key:
                print("   - No OPENAI_API_KEY found in environment")
            elif not api_key.startswith('sk-'):
                print("   - Invalid API key format")
    
    def detect_language(self, message: str) -> str:
        """Detect language using OpenAI with improved fallback"""
        # Try fallback first for known patterns
        fallback_lang = self._simple_language_detect(message)
        
        if not self.openai_available:
            return fallback_lang
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "You are a language detector. Respond with only the 2-letter language code. Hindi words like 'mera', 'hai', 'kya', 'agar', 'toh', 'karegi' indicate Hindi (hi). Spanish words like 'cuál', 'mi', 'prima' indicate Spanish (es)."
                }, {
                    "role": "user", 
                    "content": f"Detect language: '{message}'"
                }],
                max_tokens=5,
                temperature=0
            )
            detected = response.choices[0].message.content.strip().lower()[:2]
            print(f"🌍 OpenAI detected language: {detected}")
            
            # If OpenAI disagrees with fallback for Hindi/Spanish, trust fallback
            if fallback_lang in ['hi', 'es'] and detected == 'en':
                print(f"🔄 Using fallback detection: {fallback_lang} (OpenAI said {detected})")
                return fallback_lang
            
            return detected
        except Exception as e:
            print(f"❌ OpenAI language detection failed: {e}")
            return fallback_lang
    
    def translate_to_english(self, message: str, detected_lang: str) -> str:
        """Translate message to English using OpenAI"""
        if detected_lang == 'en':
            return message
            
        if not self.openai_available:
            return self._simple_translate(message, detected_lang)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "You are a translator specializing in insurance terminology. Translate the user's message to English. Focus on insurance terms like premium, coverage, policy, bill, deductible, liability, etc."
                }, {
                    "role": "user",
                    "content": f"Translate this to English: '{message}'"
                }],
                max_tokens=100,
                temperature=0
            )
            translated = response.choices[0].message.content.strip()
            print(f"🔄 OpenAI translated: '{message}' -> '{translated}'")
            return translated
        except Exception as e:
            print(f"❌ OpenAI translation failed: {e}")
            return self._simple_translate(message, detected_lang)
    
    def translate_response(self, response: str, target_lang: str) -> str:
        """Translate English response to target language using OpenAI"""
        if target_lang == 'en':
            return response
        
        if not self.openai_available:
            return self._simple_response_translate(response, target_lang)
        
        try:
            lang_names = {
                'hi': 'Hindi', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
                'pt': 'Portuguese', 'it': 'Italian', 'zh': 'Chinese', 'ja': 'Japanese',
                'ko': 'Korean', 'ar': 'Arabic', 'ru': 'Russian', 'nl': 'Dutch'
            }
            lang_name = lang_names.get(target_lang, target_lang)
            
            response_openai = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": f"You are a professional translator specializing in insurance terminology. Translate the insurance response to {lang_name}. Keep all formatting, emojis, dollar amounts, and structure exactly the same. Only translate the text content. Maintain professional insurance language."
                }, {
                    "role": "user",
                    "content": response
                }],
                max_tokens=800,
                temperature=0
            )
            translated = response_openai.choices[0].message.content.strip()
            print(f"🌍 OpenAI response translated to {lang_name}")
            return translated
        except Exception as e:
            print(f"❌ OpenAI response translation failed: {e}")
            return self._simple_response_translate(response, target_lang)
    
    def _simple_language_detect(self, message: str) -> str:
        """Fallback language detection"""
        message_lower = message.lower()
        
        # English detection first (most common words)
        english_words = ['if', 'will', 'i', 'be', 'covered', 'what', 'is', 'my', 'when', 'how', 'much', 'does', 'can', 'the', 'a', 'an', 'on', 'house', 'tree', 'falls']
        english_count = sum(1 for word in english_words if word in message_lower)
        
        # Hindi detection (specific words)
        hindi_words = ['mera', 'kitna', 'hai', 'kya', 'kab', 'ghar', 'pe', 'agar', 'ped', 'gira', 'toh', 'karegi', 'policy', 'renew', 'hoga']
        hindi_count = sum(1 for word in hindi_words if word in message_lower)
        
        # Spanish detection
        spanish_words = ['que', 'cual', 'cuál', 'mi', 'prima', 'cuando', 'cuándo', 'factura', 'cobertura', 'estaré', 'cubierto']
        spanish_count = sum(1 for word in spanish_words if word in message_lower)
        
        # Return language with highest count
        if hindi_count > 0 and hindi_count >= english_count:
            return 'hi'
        elif spanish_count > 0 and spanish_count >= english_count:
            return 'es'
        else:
            return 'en'
    
    def _simple_translate(self, message: str, lang: str) -> str:
        """Simple translation without OpenAI"""
        if lang == 'hi':
            if 'mera premium kitna hai' in message.lower():
                return 'what is my premium amount'
            if 'mera coverage kya hai' in message.lower():
                return 'what is my coverage'
            if 'agar ped gira' in message.lower():
                return 'will I be covered if a tree falls on my house'
            if 'ghar pe agar ped gira' in message.lower():
                return 'will I be covered if a tree falls on my house'
            if 'mera policy kab renew hoga' in message.lower():
                return 'when does my policy renew'
            if 'policy kab renew' in message.lower():
                return 'when does my policy renew'
        elif lang == 'es':
            if 'cual es mi prima' in message.lower():
                return 'what is my premium amount'
        
        return message
    
    def _simple_response_translate(self, response: str, lang: str) -> str:
        """Fallback response translation"""
        if lang == 'hi':
            response = response.replace('Hi', 'नमस्ते')
            response = response.replace('Your Payment Information', 'आपकी भुगतान जानकारी')
            response = response.replace('Annual Premium', 'वार्षिक प्रीमियम')
        elif lang == 'es':
            response = response.replace('Hi', 'Hola')
            response = response.replace('Your Payment Information', 'Su Información de Pago')
            response = response.replace('Annual Premium', 'Prima Anual')
        
        return response
    
    def handle_query(self, message: str, customer_id: str = "12345") -> Dict:
        """Enhanced query handling with full OpenAI integration"""
        print(f"🔍 Processing query: '{message}' for customer: {customer_id}")
        
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
        result['translation_method'] = 'openai_full' if self.openai_available else 'simple_fallback'
        
        print(f"✅ Response ready in {detected_lang}: {result['intent']}")
        return result

# Test the enhanced bot
if __name__ == "__main__":
    bot = AIInsuranceBotOpenAIFull()
    
    # Test multilingual queries
    test_queries = [
        ("What does my liability coverage include?", "12345"),
        ("mera premium kitna hai", "67890"),
        ("ghar pe agar ped gira toh cover karegi policy?", "67890"),
        ("¿cuál es mi prima?", "12345")
    ]
    
    for query, customer_id in test_queries:
        print(f"\n🔍 Query: {query}")
        result = bot.handle_query(query, customer_id)
        print(f"🌍 Language: {result['detected_language']}")
        print(f"🎯 Intent: {result['intent']}")
        print(f"💬 Response: {result['response'][:100]}...")
