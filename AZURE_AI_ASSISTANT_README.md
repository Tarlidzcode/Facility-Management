# Azure OpenAI Assistant for Office Management App

## Overview
This AI assistant is specifically designed to answer questions about your office management system using Azure OpenAI.

## Features
- **Azure OpenAI Integration**: Uses your specific Azure deployment (gpt-4o)
- **App-Specific Knowledge**: Trained on your office management system features
- **Smart Fallbacks**: Provides helpful responses even if Azure OpenAI is unavailable
- **Office Context**: Understands coffee machines, temperature control, employee management, etc.

## Configuration
The assistant uses the following Azure OpenAI settings:
- **Endpoint**: `https://ai-jonathannel8686ai993092310020.openai.azure.com/`
- **Deployment**: `gpt-4o` 
- **API Version**: `2024-11-20`
- **API Key**: Configured in `.env` file

## What the AI Can Help With
1. **Coffee Machine**: Status, bean levels, usage tracking, restock alerts
2. **Temperature Control**: Current readings, setting targets, climate management
3. **Employee Management**: Staff lists, presence tracking, who's in/out
4. **Stock Management**: Inventory levels, low-stock alerts, ordering supplies
5. **Dashboard**: Metrics overview, charts interpretation, recent activity
6. **General App Usage**: How to navigate and use different features

## How It Works
1. **User asks a question** through the chat interface
2. **AI Assistant receives the question** via `/api/ai` endpoint
3. **Azure OpenAI processes the question** with office management context
4. **Smart response returned** specific to your app's features
5. **Fallback responses** if Azure OpenAI is unavailable

## File Structure
```
services/
  ai_assistant.py          # Main AI assistant service
api.py                     # Updated /ai endpoint
test_azure_ai_assistant.py # Test script
.env                       # Azure OpenAI credentials
```

## Testing
Run the test script to verify everything is working:
```bash
python test_azure_ai_assistant.py
```

## Sample Questions Users Can Ask
- "What features does this office management system have?"
- "How do I check if the coffee machine needs refilling?"
- "How can I see who's currently in the office?"
- "What's the current temperature and how do I adjust it?"
- "How do I track inventory and stock levels?"
- "Show me how to use the dashboard"
- "What alerts can this system give me?"

The AI will provide helpful, contextual responses about your specific office management application!