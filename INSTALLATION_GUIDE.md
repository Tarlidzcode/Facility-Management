# Installation Guide for Azure AI Assistant

## Quick Start

1. **Install the OpenAI package:**
   ```bash
   pip install openai==1.51.2
   ```

2. **Test the AI Assistant:**
   ```bash
   python test_azure_ai_assistant.py
   ```

3. **Start the application:**
   ```bash
   python run_app.py
   ```

## If You Get Import Errors

The AI assistant is designed to work even without the OpenAI package installed:

- **With OpenAI package**: Uses Azure OpenAI for intelligent responses
- **Without OpenAI package**: Uses smart fallback responses

## Azure OpenAI Configuration

Your Azure OpenAI settings are already configured in `.env`:
- Endpoint: https://ai-jonathannel8686ai993092310020.openai.azure.com/
- Deployment: gpt-4o
- API Version: 2024-11-20

## Features That Work Right Now

✅ **Chat interface** - Click the chat icon to start
✅ **Smart fallback responses** - Works even without Azure OpenAI
✅ **Office management help** - Answers about coffee, temperature, employees, stock
✅ **App navigation guidance** - Helps users understand features
✅ **Employee check-in portal** - Separate login portal on port 5002 with live presence tracking

## Employee Login Portal

The application includes a **separate employee login portal** running on port **5002**:

1. **Start the login portal:**
   ```bash
   python start_employee_login.py
   ```

2. **Access the portal:**
   - URL: `http://localhost:5002`
   - Login with employee credentials
   - Default password: `password123`

3. **Live Presence Updates:**
   When employees check in or out, the system returns updated presence counts:
   - `employees_in_office`: Number of employees currently checked in
   - `total_employees`: Total active employees in database
   - `visitors_in_office`: Number of active visitors
   - `total_in_office`: Combined employees + visitors

4. **API Endpoint:**
   ```
   POST http://localhost:5002/api/employee/check-in
   Content-Type: application/json
   
   {
     "email": "employee@example.com",
     "password": "password123",
     "status": "in"  // or "out"
   }
   ```

   Response includes user info, check-in time, and **live presence summary**.

## To Enable Full AI Features

Simply install the OpenAI package and the assistant will automatically use Azure OpenAI for more intelligent responses.

The system is designed to be robust and work regardless of the OpenAI package installation status!