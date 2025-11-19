#!/usr/bin/env python3
"""
Test the cleaned Azure AI setup
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_azure_ai():
    """Test the Azure AI implementation"""
    print("🔍 TESTING CLEANED AZURE AI")
    print("=" * 40)
    
    try:
        # Import the cleaned AI module
        from ai import azure_ai, get_ai_response
        print("✅ Successfully imported ai.py")
        
        # Check configuration
        if azure_ai.is_configured():
            print("✅ Azure OpenAI is configured")
            print(f"   Endpoint: {azure_ai.azure_endpoint}")
            print(f"   Deployment: {azure_ai.deployment_name}")
            print(f"   API Version: {azure_ai.api_version}")
        else:
            print("❌ Azure OpenAI not configured")
            print("   Missing environment variables")
        
        # Test responses
        print("\n🔄 Testing AI responses...")
        
        test_messages = [
            "How does the coffee machine work?",
            "What's the temperature in the office?",
            "Who is in the office today?",
            "What stock items are low?"
        ]
        
        for msg in test_messages:
            print(f"\nQ: {msg}")
            response = get_ai_response(msg)
            print(f"A: {response}")
        
        print("\n✅ Azure AI test completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_azure_ai()