# Azure OpenAI Chat Service

This Express service exposes a single `/chat` endpoint that proxies requests to an Azure OpenAI GPT-4 deployment.

## Setup

1. Copy `.env.example` to `.env` and provide your Azure credentials.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the server:
   ```bash
   npm start
   ```

## Request format

Send a `POST /chat` request with JSON payload:

```json
{
  "message": "Hello"
}
```

Response:

```json
{
  "reply": "Hello! How can I help you today?"
}
```

Errors are returned as JSON with an `error` field and an HTTP status code that reflects the failure.
