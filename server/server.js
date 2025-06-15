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
let client;

async function connectToDatabase() {
  try {
    client = new MongoClient(process.env.MONGODB_URI);
    await client.connect();
    db = client.db();
    console.log('Connected to MongoDB Atlas');
    
    // Create text indexes for better search
    await createTextIndexes();
  } catch (error) {
    console.error('Failed to connect to MongoDB:', error);
    process.exit(1);
  }
}

// Create text indexes for better search capabilities
async function createTextIndexes() {
  try {
    const collections = await db.listCollections().toArray();
    
    for (const collectionInfo of collections) {
      const collection = db.collection(collectionInfo.name);
      
      // Get a sample document to understand the structure
      const sampleDoc = await collection.findOne();
      if (sampleDoc) {
        // Create text index on all string fields
        const textFields = {};
        Object.keys(sampleDoc).forEach(key => {
          if (typeof sampleDoc[key] === 'string' && key !== '_id') {
            textFields[key] = 'text';
          }
        });
        
        if (Object.keys(textFields).length > 0) {
          try {
            await collection.createIndex(textFields);
            console.log(`Created text index for collection: ${collectionInfo.name}`);
          } catch (indexError) {
            // Index might already exist, continue
            console.log(`Text index already exists for: ${collectionInfo.name}`);
          }
        }
      }
    }
  } catch (error) {
    console.log('Note: Some text indexes could not be created, but search will still work');
  }
}

// Enhanced function to search relevant data from MongoDB
async function searchRelevantData(query) {
  try {
    const collections = await db.listCollections().toArray();
    let allRelevantData = [];

    // Extract keywords from the query for better matching
    const keywords = extractKeywords(query);
    
    for (const collectionInfo of collections) {
      const collection = db.collection(collectionInfo.name);
      
      // Get sample document to understand structure
      const sampleDoc = await collection.findOne();
      if (!sampleDoc) continue;

      const stringFields = Object.keys(sampleDoc).filter(
        key => typeof sampleDoc[key] === 'string' && key !== '_id'
      );

      // Multiple search strategies
      const searchQueries = [
        // Text search if available
        { $text: { $search: query } },
        // Keyword-based search
        {
          $or: keywords.flatMap(keyword => 
            stringFields.map(field => ({
              [field]: { $regex: keyword, $options: 'i' }
            }))
          )
        },
        // Exact phrase search
        {
          $or: stringFields.map(field => ({
            [field]: { $regex: query, $options: 'i' }
          }))
        }
      ];

      let searchResults = [];
      
      // Try each search strategy
      for (const searchQuery of searchQueries) {
        try {
          const results = await collection.find(searchQuery).limit(5).toArray();
          if (results.length > 0) {
            searchResults = results;
            break;
          }
        } catch (error) {
          // Continue to next search strategy
          continue;
        }
      }

      // If no results, get some sample data from the collection
      if (searchResults.length === 0) {
        searchResults = await collection.find({}).limit(3).toArray();
      }

      if (searchResults.length > 0) {
        allRelevantData.push({
          collection: collectionInfo.name,
          data: searchResults,
          relevanceScore: calculateRelevanceScore(query, searchResults)
        });
      }
    }

    // Sort by relevance score
    allRelevantData.sort((a, b) => b.relevanceScore - a.relevanceScore);
    
    return allRelevantData.slice(0, 3); // Return top 3 most relevant collections
  } catch (error) {
    console.error('Error searching database:', error);
    return [];
  }
}

// Extract keywords from query for better matching
function extractKeywords(query) {
  // Remove common words and extract meaningful keywords
  const commonWords = ['what', 'how', 'when', 'where', 'why', 'who', 'is', 'are', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'about', 'ما', 'كيف', 'متى', 'أين', 'لماذا', 'من', 'هو', 'هي', 'في', 'على', 'إلى', 'عن', 'مع'];
  
  return query.toLowerCase()
    .split(/\s+/)
    .filter(word => word.length > 2 && !commonWords.includes(word))
    .slice(0, 5); // Limit to 5 keywords
}

// Calculate relevance score for search results
function calculateRelevanceScore(query, results) {
  const queryLower = query.toLowerCase();
  let score = 0;
  
  results.forEach(result => {
    Object.values(result).forEach(value => {
      if (typeof value === 'string') {
        const valueLower = value.toLowerCase();
        // Exact match gets higher score
        if (valueLower.includes(queryLower)) {
          score += 10;
        }
        // Partial matches
        queryLower.split(' ').forEach(word => {
          if (word.length > 2 && valueLower.includes(word)) {
            score += 2;
          }
        });
      }
    });
  });
  
  return score;
}

// Enhanced function to format data for AI context
function formatDataForAI(relevantData, originalQuery) {
  if (!relevantData || relevantData.length === 0) {
    return "No specific information found in El Shorouk Academy database for this query.";
  }

  let formattedData = `Based on the query "${originalQuery}", here is relevant information from El Shorouk Academy database:\n\n`;
  
  relevantData.forEach(({ collection, data }, index) => {
    formattedData += `=== ${collection.toUpperCase()} INFORMATION ===\n`;
    
    data.forEach((item, itemIndex) => {
      const { _id, ...cleanItem } = item;
      
      // Format each field nicely
      Object.entries(cleanItem).forEach(([key, value]) => {
        if (value && typeof value === 'string' && value.trim()) {
          formattedData += `${key}: ${value}\n`;
        } else if (value && typeof value !== 'string') {
          formattedData += `${key}: ${JSON.stringify(value)}\n`;
        }
      });
      
      if (itemIndex < data.length - 1) {
        formattedData += "---\n";
      }
    });
    
    formattedData += "\n";
  });

  return formattedData;
}

// Enhanced function to send message to OpenRouter API
async function sendToOpenRouter(messages, hasRelevantData) {
  try {
    const systemPrompt = hasRelevantData 
      ? `You are an intelligent assistant for El Shorouk Academy (أكاديمية الشروق). You have access to the academy's comprehensive database and should provide accurate, helpful information.

IMPORTANT INSTRUCTIONS:
1. Use ONLY the information provided in the database context to answer questions
2. If the database contains relevant information, base your answer entirely on that data
3. Be specific and detailed when you have the information
4. If asked about something not in the provided database context, clearly state that you need more specific information or that the information is not available in your current database
5. Always be professional and helpful
6. Answer in the same language the user asks (Arabic or English)
7. For academic information (courses, programs, requirements), be very specific and accurate
8. Include relevant details like course codes, credit hours, prerequisites when available
9. If multiple options exist, present them clearly

Remember: You represent El Shorouk Academy, so maintain a professional and knowledgeable tone.`
      : `You are an assistant for El Shorouk Academy. The specific information requested was not found in the database. Politely explain that you need more specific information or suggest how the user can get the information they need. Always be helpful and professional.`;

    const response = await axios.post(
      'https://openrouter.ai/api/v1/chat/completions',
      {
        model: 'openai/gpt-3.5-turbo',
        messages: [
          { role: 'system', content: systemPrompt },
          ...messages
        ],
        temperature: 0.3, // Lower temperature for more consistent, factual responses
        max_tokens: 1500,
        top_p: 0.9
      },
      {
        headers: {
          'Authorization': `Bearer ${process.env.OPENROUTER_API_KEY}`,
          'Content-Type': 'application/json'
        },
        timeout: 30000
      }
    );

    return response.data.choices[0].message.content;
  } catch (error) {
    console.error('Error calling OpenRouter API:', error.response?.data || error.message);
    throw new Error('Failed to get AI response');
  }
}

// Enhanced chat endpoint
app.post('/api/chat', async (req, res) => {
  try {
    const { message, conversationHistory = [] } = req.body;

    if (!message || !message.trim()) {
      return res.status(400).json({ error: 'Message is required' });
    }

    console.log(`Processing query: "${message}"`);

    // Search for relevant data in MongoDB
    const relevantData = await searchRelevantData(message.trim());
    const hasRelevantData = relevantData.length > 0;
    
    console.log(`Found ${relevantData.length} relevant data sources`);

    // Format the context data
    const contextData = formatDataForAI(relevantData, message);

    // Prepare messages for AI with enhanced context
    const messages = [
      ...conversationHistory.slice(-6), // Keep last 6 messages for context
      {
        role: 'user',
        content: hasRelevantData 
          ? `Context from El Shorouk Academy database:\n${contextData}\n\nUser question: ${message}`
          : message
      }
    ];

    // Get AI response
    const aiResponse = await sendToOpenRouter(messages, hasRelevantData);

    console.log(`Response generated successfully`);

    res.json({
      response: aiResponse,
      hasRelevantData,
      dataSourcesCount: relevantData.length
    });

  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({ 
      error: 'Failed to process your request. Please try again.',
      details: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

// Enhanced database test endpoint
app.get('/api/test-db', async (req, res) => {
  try {
    const collections = await db.listCollections().toArray();
    const collectionDetails = [];
    
    for (const collection of collections) {
      const coll = db.collection(collection.name);
      const count = await coll.countDocuments();
      const sample = await coll.findOne();
      
      collectionDetails.push({
        name: collection.name,
        documentCount: count,
        sampleFields: sample ? Object.keys(sample).filter(k => k !== '_id') : []
      });
    }
    
    res.json({
      status: 'Connected',
      collections: collectionDetails,
      totalCollections: collections.length,
      totalDocuments: collectionDetails.reduce((sum, coll) => sum + coll.documentCount, 0)
    });
  } catch (error) {
    res.status(500).json({
      status: 'Error',
      error: error.message
    });
  }
});

// Test search endpoint for debugging
app.post('/api/test-search', async (req, res) => {
  try {
    const { query } = req.body;
    if (!query) {
      return res.status(400).json({ error: 'Query is required' });
    }

    const relevantData = await searchRelevantData(query);
    const formattedData = formatDataForAI(relevantData, query);

    res.json({
      query,
      relevantDataCount: relevantData.length,
      relevantData,
      formattedContext: formattedData
    });
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    message: 'El Shorouk Academy Chatbot Server is running',
    timestamp: new Date().toISOString()
  });
});

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('Shutting down gracefully...');
  if (client) {
    await client.close();
  }
  process.exit(0);
});

// Start server
async function startServer() {
  await connectToDatabase();
  
  app.listen(PORT, () => {
    console.log(`🚀 El Shorouk Academy Chatbot Server running on port ${PORT}`);
    console.log(`📊 Health check: http://localhost:${PORT}/api/health`);
    console.log(`🔍 Database test: http://localhost:${PORT}/api/test-db`);
    console.log(`🧪 Search test: http://localhost:${PORT}/api/test-search`);
  });
}

startServer().catch(console.error);