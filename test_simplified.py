#!/usr/bin/env python3
"""
Test the simplified upload flow
"""

import subprocess
import time
import webbrowser
import sys
import os

def main():
    print("🧪 Testing Simplified Upload Flow")
    print("=" * 40)
    
    if not os.path.exists('app.py'):
        print("❌ Please run from the insurance-quote-app-python directory")
        return
    
    print("✨ Simplified Features:")
    print("  ⚡ Direct upload (no preview step)")
    print("  📊 Progress bar with cancel")
    print("  💡 Rotating tips during processing")
    print("  📱 Works for both PDF and images")
    print()
    
    try:
        # Start server
        print("🚀 Starting server...")
        process = subprocess.Popen([sys.executable, 'app.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        time.sleep(3)
        print("✅ Server started on http://localhost:5000")
        
        # Open browser
        webbrowser.open('http://localhost:5000')
        
        print()
        print("🎯 Test Instructions:")
        print("  1. Click 'Choose File' or drag & drop")
        print("  2. Select sample-auto-policy.pdf or sample-policy-image.jpg")
        print("  3. Watch immediate progress bar appear")
        print("  4. Try the cancel button during processing")
        print("  5. Notice the rotating tips")
        print()
        print("✅ Key Improvements:")
        print("  • No confusing preview step")
        print("  • Immediate processing feedback")
        print("  • Working cancel functionality")
        print("  • Same experience for all file types")
        print()
        print("⏹️  Press Ctrl+C to stop")
        
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        process.terminate()
        print("✅ Done!")

if __name__ == "__main__":
    main()
