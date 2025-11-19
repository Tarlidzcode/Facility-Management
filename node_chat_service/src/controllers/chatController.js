import { sendChatCompletion } from '../services/azureClient.js';

export async function postChat(req, res, next) {
  try {
    const { message } = req.body ?? {};

    if (typeof message !== 'string' || !message.trim()) {
      return res.status(400).json({ error: 'A non-empty "message" field is required.' });
    }

    const reply = await sendChatCompletion(message.trim());
    return res.json({ reply });
  } catch (error) {
    return next(error);
  }
}
