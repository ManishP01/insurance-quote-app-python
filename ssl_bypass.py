"""
SSL Bypass for Corporate Networks
"""

import os
import ssl
import urllib3

def setup_ssl_bypass():
    """Setup SSL bypass for corporate networks"""
    disable_ssl = os.getenv('DISABLE_SSL_VERIFY', 'false').lower() == 'true'
    
    if disable_ssl:
        try:
            # Disable SSL warnings
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # Create unverified SSL context globally
            ssl._create_default_https_context = ssl._create_unverified_context
            
            # Monkey patch requests to ignore SSL
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            class SSLAdapter(HTTPAdapter):
                def init_poolmanager(self, *args, **kwargs):
                    kwargs['ssl_context'] = ssl._create_unverified_context()
                    return super().init_poolmanager(*args, **kwargs)
            
            # Apply to requests session
            session = requests.Session()
            session.mount('https://', SSLAdapter())
            
            # Patch OpenAI to use our session
            try:
                import openai
                openai.api_requestor.requests = requests
                openai.api_requestor.requests.Session = lambda: session
            except:
                pass
            
            print("🔓 SSL verification disabled for corporate network")
            return True
            
        except Exception as e:
            print(f"⚠️ SSL bypass setup failed: {e}")
            return False
    
    return False
