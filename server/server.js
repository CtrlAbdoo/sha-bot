import express from 'express';
import cors from 'cors';
import { MongoClient } from 'mongodb';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB connection
let db;
const client = new MongoClient(process.env.MONGODB_URI);

async function connectToDatabase() {
  try {
    await client.connect();
    db = client.db();
    console.log('Connected to MongoDB Atlas');
  } catch (error) {
    console.error('Failed to connect to MongoDB:', error);
    process.exit(1);
  }
}

// Function to search relevant data from MongoDB
async function searchRelevantData(query) {
  try {
    // Get all collection names
    const collections = await db.listCollections().toArray();
    let relevantData = [];

    // Search through all collections for relevant information
    for (const collectionInfo of collections) {
      const collection = db.collection(collectionInfo.name);
      
      // Create a text search query
      const searchResults = await collection.find({
        $or: [
          { $text: { $search: query } },
          // Fallback regex search for collections without text index
          ...Object.keys(await collection.findOne() || {}).map(field => ({
            [field]: { $regex: query, $options: 'i' }
          }))
        ]
      }).limit(10).toArray();

      if (searchResults.length > 0) {
        relevantData.push({
          collection: collectionInfo.name,
          data: searchResults
        });
      }
    }

    return relevantData;
  } catch (error) {
    console.error('Error searching database:', error);
    return [];
  }
}

// Function to format data for AI context
function formatDataForAI(relevantData) {
  if (!relevantData || relevantData.length === 0) {
    return "No specific information found in the database.";
  }

  let formattedData = "Here is relevant information from El Shorouk Academy database:\n\n";
  
  relevantData.forEach(({ collection, data }) => {
    formattedData += `From ${collection}:\n`;
    data.forEach(item => {
      // Remove MongoDB _id and format the data nicely
      const { _id, ...cleanItem } = item;
      formattedData += `- ${JSON.stringify(cleanItem, null, 2)}\n`;
    });
    formattedData += "\n";
  });

  return formattedData;
}

// Function to send message to OpenRouter API
async function sendToOpenRouter(messages) {
  try {
    const response = await axios.post(
      'https://openrouter.ai/api/v1/chat/completions',
      {
        model: 'openai/gpt-3.5-turbo',
        messages: messages,
        temperature: 0.7,
        max_tokens: 1000
      },
      {
        headers: {
          'Authorization': `Bearer ${process.env.OPENROUTER_API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );

    return response.data.choices[0].message.content;
  } catch (error) {
    console.error('Error calling OpenRouter API:', error);
    throw new Error('Failed to get AI response');
  }
}

// Chat endpoint
app.post('/api/chat', async (req, res) => {
  try {
    const { message, conversationHistory = [] } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Search for relevant data in MongoDB
    const relevantData = await searchRelevantData(message);
    const contextData = formatDataForAI(relevantData);

    // Prepare messages for AI
    const messages = [
      {
        role: 'system',
        content: `You are a helpful assistant for El Shorouk Academy. You have access to the academy's database and should provide accurate, helpful information about the academy's programs, courses, faculty, admissions, and other services.

Context from database:
${contextData}

Guidelines:
- Always be helpful and professional
- If you don't have specific information, say so clearly
- Provide accurate information based on the database context
- If asked about something not in the database, explain that you need more specific information
- Answer in the same language the user asks (Arabic or English)
- Be concise but comprehensive in your responses`
      },
      ...conversationHistory.slice(-8), // Keep last 8 messages for context
      {
        role: 'user',
        content: message
      }
    ];

    // Get AI response
    const aiResponse = await sendToOpenRouter(messages);

    res.json({
      response: aiResponse,
      hasRelevantData: relevantData.length > 0
    });

  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({ 
      error: 'Failed to process your request. Please try again.' 
    });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', message: 'Server is running' });
});

// Test database connection endpoint
app.get('/api/test-db', async (req, res) => {
  try {
    const collections = await db.listCollections().toArray();
    const collectionNames = collections.map(c => c.name);
    
    res.json({
      status: 'Connected',
      collections: collectionNames,
      totalCollections: collectionNames.length
    });
  } catch (error) {
    res.status(500).json({
      status: 'Error',
      error: error.message
    });
  }
});

// Start server
async function startServer() {
  await connectToDatabase();
  
  app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`Health check: http://localhost:${PORT}/api/health`);
    console.log(`Database test: http://localhost:${PORT}/api/test-db`);
  });
}

startServer().catch(console.error);