import express from 'express';
import helmet from 'helmet';
import morgan from 'morgan';
import { config } from 'dotenv';
import chatRouter from './routes/chat.js';
import { errorHandler, notFoundHandler } from './middleware/errorHandler.js';
import { validateAzureSetup } from './services/azureClient.js';

config();

validateAzureSetup();

const app = express();

app.use(helmet());
app.use(express.json({ limit: '1mb' }));
app.use(morgan('combined'));

app.use('/chat', chatRouter);

app.use(notFoundHandler);
app.use(errorHandler);

const port = process.env.PORT ? Number(process.env.PORT) : 3000;
app.listen(port, () => {
  console.log(`Azure OpenAI chat service listening on port ${port}`);
});
