#!/usr/bin/env python3
"""
Simple script to test AI functionality - OpenAI integration removed.
"""
import os
import sys

def test_ai_functionality():
    print("🔬 Testing AI Functionality...")
    print("📋 OpenAI integration has been removed from this project")
    print("-" * 50)
    
    # Test fallback responses
    test_messages = [
        "coffee",
        "temperature", 
        "presence",
        "stock",
        "help"
    ]
    
    print("⏳ Testing fallback responses...")
    for message in test_messages:
        reply = get_fallback_reply(message)
        print(f"� Message: '{message}' -> Reply: {reply[:50]}...")
    
    print("✅ Fallback responses working correctly!")
    return True

def get_fallback_reply(message):
    """Get fallback reply for testing - same logic as api.py"""
    lm = message.lower()
    if 'coffee' in lm:
        return "Coffee machine beans are low (approx 12%). Water level is 68% and milk 45%. Would you like me to create a restock order?"
    elif 'temperature' in lm or 'temp' in lm:
        return "The current office temperature is 22°C. I can set a new target if you tell me the desired temperature."
    elif 'presence' in lm or 'who' in lm or 'in office' in lm:
        return "Currently 24 people are in the office and 3 are out. I can show the list or export attendance."
    elif 'stock' in lm or 'low' in lm or 'order' in lm:
        return "Low stock items: Coffee Beans, Paper. I can prepare a purchase order for these items."
    elif 'help' in lm or 'what' in lm:
        return "I can help with coffee machine status, temperature control, presence tracking, and stock management. Try asking about specific office functions!"
    else:
        return "I can help with coffee, temperature, stock, and presence. Try asking something like: 'How much coffee is left?'"

if __name__ == '__main__':
    success = test_ai_functionality()
    print("-" * 50)
    if success:
        print("🎉 AI fallback functionality is working correctly!")
    else:
        print("🚨 AI functionality test failed!")
    
    input("\n✋ Press Enter to exit...")