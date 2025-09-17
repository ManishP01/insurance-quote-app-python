"""
SSL Configuration for Corporate Networks
Supports both certificate bundle and SSL bypass approaches
"""
import os
import ssl
import urllib3

def configure_ssl():
    """Configure SSL settings for corporate networks"""
    
    # Check if custom certificate bundle is provided
    ca_bundle = os.getenv('REQUESTS_CA_BUNDLE')
    if ca_bundle and os.path.exists(ca_bundle):
        print(f"🔒 Using custom certificate bundle: {ca_bundle}")
        # REQUESTS_CA_BUNDLE is automatically used by requests library
        return
    
    # Fallback to SSL bypass if no certificate bundle
    disable_ssl_verify = os.getenv('DISABLE_SSL_VERIFY', 'false').lower() == 'true'
    
    if disable_ssl_verify:
        print("🔓 SSL verification disabled for corporate network")
        
        # Disable SSL warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Create unverified SSL context
        ssl._create_default_https_context = ssl._create_unverified_context
        
        # Clear certificate bundle variables for bypass
        os.environ['CURL_CA_BUNDLE'] = ''
        if 'REQUESTS_CA_BUNDLE' not in os.environ or not os.path.exists(os.environ['REQUESTS_CA_BUNDLE']):
            os.environ['REQUESTS_CA_BUNDLE'] = ''
    else:
        print("🔒 SSL verification enabled")

# Auto-configure on import
configure_ssl()
