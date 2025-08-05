#!/usr/bin/env python3
"""
Setup verification script for LinkedIn Interview Prep AI
Run this to check if everything is configured correctly.
"""

import os
import sys
from pathlib import Path

def check_setup():
    print("🔍 LinkedIn Interview Prep AI - Setup Verification\n")
    
    issues = []
    warnings = []
    
    # Check Python version
    print("1. Checking Python version...")
    if sys.version_info < (3, 8):
        issues.append("❌ Python 3.8+ required (you have {}.{})".format(*sys.version_info[:2]))
    else:
        print("   ✅ Python {}.{}.{} detected".format(*sys.version_info[:3]))
    
    # Check backend directory
    print("\n2. Checking backend setup...")
    backend_dir = Path("backend")
    if not backend_dir.exists():
        issues.append("❌ Backend directory not found")
    else:
        print("   ✅ Backend directory found")
        
        # Check .env file
        env_file = backend_dir / ".env"
        if not env_file.exists():
            issues.append("❌ backend/.env file not found (copy from env.example)")
        else:
            print("   ✅ .env file exists")
            
            # Check for API key
            with open(env_file) as f:
                content = f.read()
                if "your_openai_api_key_here" in content or "OPENAI_API_KEY=" not in content:
                    warnings.append("⚠️  OpenAI API key not set (AI features will use fallbacks)")
                else:
                    print("   ✅ OpenAI API key configured")
    
    # Check frontend directory
    print("\n3. Checking frontend setup...")
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        issues.append("❌ Frontend directory not found")
    else:
        print("   ✅ Frontend directory found")
        
        # Check node_modules
        node_modules = frontend_dir / "node_modules"
        if not node_modules.exists():
            issues.append("❌ Frontend dependencies not installed (run: cd frontend && npm install)")
        else:
            print("   ✅ Frontend dependencies installed")
    
    # Check startup script
    print("\n4. Checking startup script...")
    if not Path("startup.sh").exists():
        issues.append("❌ startup.sh not found")
    elif not os.access("startup.sh", os.X_OK):
        issues.append("❌ startup.sh not executable (run: chmod +x startup.sh)")
    else:
        print("   ✅ startup.sh is executable")
    
    # Summary
    print("\n" + "="*50)
    print("SETUP SUMMARY")
    print("="*50)
    
    if issues:
        print("\n🚨 Critical Issues (must fix):")
        for issue in issues:
            print(f"   {issue}")
    
    if warnings:
        print("\n⚠️  Warnings (optional but recommended):")
        for warning in warnings:
            print(f"   {warning}")
    
    if not issues and not warnings:
        print("\n✅ Everything looks good! Run ./startup.sh to start the application.")
    elif not issues:
        print("\n✅ Setup is functional. Address warnings for full functionality.")
    else:
        print("\n❌ Please fix the critical issues before running the application.")
    
    print("\n📚 Quick Start Commands:")
    print("   1. cd backend && cp env.example .env")
    print("   2. # Edit backend/.env and add your OpenAI API key")
    print("   3. cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt")
    print("   4. cd frontend && npm install")
    print("   5. ./startup.sh")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = check_setup()
    sys.exit(0 if success else 1) 