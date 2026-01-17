#!/usr/bin/env python3
"""
Sentinel-X Demo Script
Demonstrates all features without requiring manual interaction
"""

import os
import sys
import time
import subprocess

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_step(step_num, text):
    """Print a numbered step"""
    print(f"[{step_num}] {text}")

def main():
    print_header("SENTINEL-X DEMO LAUNCHER")
    
    print("This demo will showcase all features of Sentinel-X:")
    print("✓ Multi-modal vision processing")
    print("✓ Real-time object detection")
    print("✓ Movement tracking and trails")
    print("✓ Behavioral anomaly detection")
    print("✓ Threat level classification")
    print("✓ Explainable AI alerts")
    print("✓ Command dashboard")
    print()
    
    print_step(1, "Checking Python environment...")
    python_version = sys.version_info
    print(f"   Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 10):
        print("   ❌ ERROR: Python 3.10 or higher required")
        return
    print("   ✓ Python version OK")
    
    print_step(2, "Checking dependencies...")
    required_packages = [
        'streamlit',
        'cv2',
        'numpy',
        'pandas',
        'ultralytics'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'cv2':
                __import__('cv2')
            else:
                __import__(package)
            print(f"   ✓ {package}")
        except ImportError:
            print(f"   ✗ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print("\n   ❌ Missing packages detected!")
        print("   Run: pip install -r requirements.txt")
        return
    
    print_step(3, "Launching Sentinel-X application...")
    print("   The application will open in your default browser")
    print("   URL: http://localhost:8501")
    print()
    print("="*60)
    print("QUICK START INSTRUCTIONS:")
    print("="*60)
    print("1. Select 'Use Sample Video' under Video Source")
    print("2. Click 'Generate Sample Video' button")
    print("3. Click '▶️ Start Processing' button")
    print("4. Watch AI detect and track objects in real-time!")
    print("="*60)
    print()
    print("Press Ctrl+C to stop the application")
    print()
    
    time.sleep(2)
    
    try:
        # Launch Streamlit
        subprocess.run(['streamlit', 'run', 'sentinel_x_app.py'])
    except KeyboardInterrupt:
        print("\n\nShutting down Sentinel-X...")
        print("Thank you for using Sentinel-X!")
    except Exception as e:
        print(f"\n❌ Error launching application: {e}")
        print("\nTry running manually:")
        print("   streamlit run sentinel_x_app.py")

if __name__ == "__main__":
    main()
