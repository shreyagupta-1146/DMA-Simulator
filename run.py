#!/usr/bin/env python3
"""
DMA Controller Simulator - Quick Start Script
Automatically sets up and runs the application
"""
import os
import sys
import subprocess

def main():
    print("=" * 60)
    print("🚀 DMA CONTROLLER SIMULATOR - QUICK START")
    print("=" * 60)
    print()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print("✓ Python version check passed")
    
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    print("✓ Changed to backend directory")
    
    # Check if requirements are installed
    try:
        import flask
        import flask_socketio
        print("✓ Dependencies already installed")
    except ImportError:
        print("⚠ Installing dependencies...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', '../requirements.txt'])
            print("✓ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Error: Failed to install dependencies")
            print("   Please run manually: pip install -r requirements.txt")
            sys.exit(1)
    
    print()
    print("=" * 60)
    print("STARTING DMA CONTROLLER SIMULATOR SERVER")
    print("=" * 60)
    print()
    print("📡 Server URL: http://localhost:5000")
    print("🌐 Open this URL in your web browser")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    print("=" * 60)
    print()
    
    # Run the Flask app
    try:
        subprocess.call([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print()
        print("=" * 60)
        print("Server stopped. Thank you for using DMA Controller Simulator!")
        print("=" * 60)

if __name__ == '__main__':
    main()