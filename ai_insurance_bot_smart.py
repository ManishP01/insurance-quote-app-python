"""
Smart OpenAI-Based Insurance Bot - No Hardcoding
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from ai_insurance_bot import AIInsuranceBot

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class SmartAIInsuranceBot(AIInsuranceBot):
    def __init__(self):
        super().__init__()
        
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY')
        self.openai_available = OPENAI_AVAILABLE and api_key and api_key.startswith('sk-')
        
        if self.openai_available:
            openai.api_key = api_key
            print("✅ Smart OpenAI Insurance Bot enabled")
        else:
            print("⚠️ Falling back to hardcoded patterns")
    
    def detect_language_and_intent(self, message: str) -> Tuple[str, str, Dict]:
        """Use OpenAI to detect language and intent in one call"""
        if not self.openai_available:
            # Fallback to hardcoded
            lang = self._simple_language_detect(message)
            english_msg = self._simple_translate(message, lang)
            intent, params = self.detect_intent(english_msg)
            return lang, intent, params
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": """You are an insurance chatbot analyzer. Analyze the user's message and respond with JSON:
{
  "language": "en|hi|es|fr",
  "intent": "premium_question|coverage_question|claim_question|policy_renewal|coverage_scenario|bill_question|unknown",
  "english_translation": "translated message",
  "confidence": 0.9
}

Intent definitions:
- premium_question: asking about premium amount, cost, payment
- coverage_question: asking what's covered, coverage details
- claim_question: asking about claims, accidents, damage
- policy_renewal: asking about renewal, expiration dates
- coverage_scenario: asking "will I be covered if..." scenarios
- bill_question: asking about bills, due dates, payment methods
- unknown: unclear or unrelated to insurance"""
                }, {
                    "role": "user",
                    "content": f"Analyze: '{message}'"
                }],
                max_tokens=150,
                temperature=0
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            print(f"🤖 OpenAI Analysis: {result['language']} | {result['intent']} | {result['confidence']}")
            
            return result['language'], result['intent'], {'english_message': result['english_translation']}
            
        except Exception as e:
            print(f"❌ OpenAI analysis failed: {e}")
            # Fallback to hardcoded
            lang = self._simple_language_detect(message)
            english_msg = self._simple_translate(message, lang)
            intent, params = self.detect_intent(english_msg)
            return lang, intent, params
    
    def handle_query(self, message: str, customer_id: str = "12345") -> Dict:
        """Smart query handling with OpenAI"""
        print(f"🔍 Smart analysis for: '{message}'")
        
        # Get language and intent from OpenAI
        detected_lang, intent, params = self.detect_language_and_intent(message)
        
        # Get customer data
        customer = self.get_customer_info(customer_id)
        if not customer:
            return {
                'response': "I couldn't find your account. Please provide your policy number.",
                'intent': 'no_customer_data',
                'detected_language': detected_lang,
                'translation_method': 'smart_openai'
            }
        
        # Handle the intent
        if intent == 'premium_question':
            result = self.handle_bill_amount(customer, params)
        elif intent == 'coverage_question':
            result = self.handle_coverage_explanation(customer, {'coverage_type': 'general'})
        elif intent == 'coverage_scenario':
            result = self.handle_coverage_scenario(customer, {'scenario': params.get('english_message', message)})
        elif intent == 'policy_renewal':
            result = self.handle_policy_renewal(customer, params)
        elif intent == 'bill_question':
            result = self.handle_bill_due_date(customer, params)
        elif intent == 'claim_question':
            result = self.handle_claims_info(customer, params)
        else:
            result = self.handle_unknown_query(message)
        
        # Translate response back to original language
        if detected_lang != 'en' and self.openai_available:
            result['response'] = self.translate_response_smart(result['response'], detected_lang)
        
        result['detected_language'] = detected_lang
        result['translation_method'] = 'smart_openai' if self.openai_available else 'hardcoded_fallback'
        
        return result
    
    def translate_response_smart(self, response: str, target_lang: str) -> str:
        """Smart response translation"""
        if not self.openai_available or target_lang == 'en':
            return response
        
        try:
            lang_names = {'hi': 'Hindi', 'es': 'Spanish', 'fr': 'French'}
            lang_name = lang_names.get(target_lang, target_lang)
            
            translated = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": f"Translate this insurance response to {lang_name}. Keep formatting, emojis, and dollar amounts. Only translate text content."
                }, {
                    "role": "user",
                    "content": response
                }],
                max_tokens=800,
                temperature=0
            )
            return translated.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ Smart translation failed: {e}")
            return response
    
    def _simple_language_detect(self, message: str) -> str:
        """Fallback language detection"""
        message_lower = message.lower()
        hindi_words = ['mera', 'kitna', 'hai', 'kya', 'kab', 'agar', 'toh', 'hoga']
        if any(word in message_lower for word in hindi_words):
            return 'hi'
        return 'en'
    
    def _simple_translate(self, message: str, lang: str) -> str:
        """Fallback translation"""
        if lang == 'hi':
            if 'premium' in message.lower() or 'kitna' in message.lower():
                return 'what is my premium'
            if 'coverage' in message.lower() or 'kya hai' in message.lower():
                return 'what is my coverage'
        return message

# Test the smart bot
if __name__ == "__main__":
    bot = SmartAIInsuranceBot()
    
    test_queries = [
        "kitna paisa dena hoga?",  # How much money to pay?
        "accident mein kya hoga?",  # What happens in accident?
        "meri car chori ho gayi toh?",  # What if car stolen?
        "when is my next payment due?",
        "¿cuánto cuesta mi seguro?"  # How much does my insurance cost?
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: {query}")
        result = bot.handle_query(query, "67890")
        print(f"🎯 Intent: {result.get('intent')}")
        print(f"🌍 Language: {result.get('detected_language')}")
        print(f"💬 Response: {result['response'][:100]}...")
