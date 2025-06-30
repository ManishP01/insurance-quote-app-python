#!/usr/bin/env python3
"""
Demo script to showcase the enhanced insurance quote application
"""

import webbrowser
import time
import subprocess
import sys
import os

def main():
    print("🚀 QuickQuote Insurance Application Demo")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Please run this from the insurance-quote-app-python directory")
        return
    
    print("✨ Enhanced Features:")
    print("  📊 Real-time progress tracking")
    print("  🔄 Step-by-step processing indicators")
    print("  💡 Dynamic tips during processing")
    print("  📱 File preview before processing")
    print("  ❌ Cancel processing option")
    print("  🎯 Visual progress bar")
    print("  📸 Enhanced camera integration")
    print()
    
    print("🔧 Starting the application...")
    
    try:
        # Start the Flask app in background
        process = subprocess.Popen([sys.executable, 'app.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        print("✅ Server started successfully!")
        print("🌐 Opening browser to http://localhost:5000")
        
        # Open browser
        webbrowser.open('http://localhost:5000')
        
        print()
        print("🎯 Try these enhanced features:")
        print("  1. Upload the sample PDF and watch the progress bar")
        print("  2. Notice the step-by-step processing indicators")
        print("  3. Read the rotating tips during processing")
        print("  4. Try the 'Take Photo' feature with your camera")
        print("  5. Use the cancel button if needed")
        print()
        print("⏹️  Press Ctrl+C to stop the server")
        
        # Keep the server running
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        process.terminate()
        print("✅ Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
