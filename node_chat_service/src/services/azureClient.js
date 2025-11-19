import { OpenAIClient, AzureKeyCredential } from '@azure/openai';

const requiredEnvVars = ['AZURE_OPENAI_KEY', 'AZURE_OPENAI_ENDPOINT', 'AZURE_OPENAI_DEPLOYMENT'];

let cachedClient;

function getAzureConfig() {
  const config = {
    key: process.env.AZURE_OPENAI_KEY,
    endpoint: process.env.AZURE_OPENAI_ENDPOINT,
    deployment: process.env.AZURE_OPENAI_DEPLOYMENT
  };

  return config;
}

export function validateAzureSetup() {
  const missing = requiredEnvVars.filter((name) => !process.env[name]);
  if (missing.length) {
    throw new Error(`Missing required Azure OpenAI environment variables: ${missing.join(', ')}`);
  }
}

function getClient() {
  if (!cachedClient) {
    const { key, endpoint } = getAzureConfig();
    cachedClient = new OpenAIClient(endpoint, new AzureKeyCredential(key));
  }
  return cachedClient;
}

export async function sendChatCompletion(message) {
  const client = getClient();
  const { deployment } = getAzureConfig();

  try {
    const response = await client.getChatCompletions(deployment, [
      {
        role: 'system',
        content: 'You are a helpful AI assistant that provides concise, friendly responses.'
      },
      {
        role: 'user',
        content: message
      }
    ]);

    const topChoice = response?.choices?.[0];
    const reply = topChoice?.message?.content?.trim();

    if (!reply) {
      throw new Error('Azure OpenAI returned an empty response.');
    }

    return reply;
  } catch (error) {
    const err = error instanceof Error ? error : new Error('Unknown Azure OpenAI error');
    err.status = error?.status ?? 502;
    throw err;
  }
}
