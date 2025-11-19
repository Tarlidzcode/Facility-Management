"""
AI Assistant Service - DEPRECATED
This file has been replaced by ai.py
Use the main ai.py file for Azure OpenAI integration instead.
"""

# This file is deprecated - use ai.py instead
print("INFO: services/ai_assistant.py is deprecated. Using ai.py for Azure OpenAI integration.")

# Import from the main ai.py file for backward compatibility
try:
    from ai import azure_ai as office_ai
except ImportError:
    # Fallback if import fails
    class DummyAI:
        def get_response(self, message, context=None):
            return "🤖 AI service unavailable. Please check configuration."
    
    office_ai = DummyAI()