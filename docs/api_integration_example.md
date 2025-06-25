# SHA-Bot API Integration Guide

This guide shows how to integrate the SHA-Bot API into various applications.

## API Endpoints

The SHA-Bot API has the following main endpoints:

- `POST /chat` - Send a message to the chatbot
- `GET /health` - Check the health status of the API
- `GET /models` - List available models

## Integration Examples

### JavaScript/TypeScript Example

```javascript
// Example using fetch API in JavaScript
async function sendMessage(message, model = 'gpt-3.5') {
  const apiUrl = 'https://your-render-app.onrender.com/chat';
  
  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        model: model,
        max_tokens: 500,
        temperature: 0.7,
      }),
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

// Usage example
sendMessage('ما هي مواد الفرقة الثانية في قسم علم الحاسب؟')
  .then(response => {
    console.log('Response:', response.response);
    console.log('Model:', response.model);
    console.log('Tokens used:', response.tokens_used);
  })
  .catch(error => {
    console.error('Failed to send message:', error);
  });
```

### Python Example

```python
import requests

def send_message(message, model='gpt-4.1-mini', max_tokens=500, temperature=0.7):
    """Send a message to the SHA-Bot API"""
    api_url = 'https://your-render-app.onrender.com/chat'
    
    payload = {
        'message': message,
        'model': model,
        'max_tokens': max_tokens,
        'temperature': temperature
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Usage example
if __name__ == "__main__":
    response = send_message("Tell me about El-Shorouk Academy")
    
    if response:
        print(f"Response: {response['response']}")
        print(f"Model: {response['model']}")
        print(f"Tokens used: {response['tokens_used']}")
```

### React Component Example

```jsx
import React, { useState } from 'react';
import axios from 'axios';

const ChatBot = () => {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const API_URL = 'https://your-render-app.onrender.com/chat';
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!message.trim()) return;
    
    setLoading(true);
    setError('');
    
    try {
      const result = await axios.post(API_URL, {
        message: message,
        model: 'gpt-3.5',
        max_tokens: 500,
        temperature: 0.7,
      });
      
      setResponse(result.data.response);
    } catch (err) {
      setError('Failed to get response from the chatbot API');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="chatbot-container">
      <h2>SHA-Bot Chat</h2>
      
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message here..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
      
      {error && <div className="error">{error}</div>}
      
      {response && (
        <div className="response">
          <h3>Response:</h3>
          <p>{response}</p>
        </div>
      )}
    </div>
  );
};

export default ChatBot;
```

### Flutter Example

```dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class ChatBotService {
  final String apiUrl = 'https://your-render-app.onrender.com/chat';
  
  Future<Map<String, dynamic>> sendMessage(String message) async {
    final response = await http.post(
      Uri.parse(apiUrl),
      headers: {
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'message': message,
        'model': 'gpt-3.5',
        'max_tokens': 500,
        'temperature': 0.7,
      }),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to send message');
    }
  }
}

class ChatScreen extends StatefulWidget {
  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final ChatBotService _chatBotService = ChatBotService();
  final TextEditingController _textController = TextEditingController();
  final List<Map<String, String>> _messages = [];
  bool _isLoading = false;
  
  void _handleSubmit(String text) async {
    _textController.clear();
    
    setState(() {
      _messages.add({
        'sender': 'user',
        'text': text,
      });
      _isLoading = true;
    });
    
    try {
      final response = await _chatBotService.sendMessage(text);
      
      setState(() {
        _messages.add({
          'sender': 'bot',
          'text': response['response'],
        });
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _messages.add({
          'sender': 'error',
          'text': 'Error: Failed to get response from the chatbot',
        });
        _isLoading = false;
      });
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('SHA-Bot Chat'),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[index];
                final bool isUser = message['sender'] == 'user';
                
                return Container(
                  margin: EdgeInsets.symmetric(vertical: 10.0, horizontal: 15.0),
                  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    padding: EdgeInsets.all(10.0),
                    decoration: BoxDecoration(
                      color: isUser ? Colors.blue : Colors.grey[300],
                      borderRadius: BorderRadius.circular(10.0),
                    ),
                    child: Text(
                      message['text']!,
                      style: TextStyle(
                        color: isUser ? Colors.white : Colors.black,
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          _isLoading
              ? Center(child: CircularProgressIndicator())
              : Container(),
          Divider(height: 1.0),
          Container(
            decoration: BoxDecoration(
              color: Theme.of(context).cardColor,
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _textController,
                    decoration: InputDecoration(
                      hintText: 'Type a message',
                      contentPadding: EdgeInsets.symmetric(horizontal: 20.0, vertical: 10.0),
                      border: InputBorder.none,
                    ),
                    onSubmitted: _isLoading ? null : _handleSubmit,
                  ),
                ),
                IconButton(
                  icon: Icon(Icons.send),
                  onPressed: _isLoading
                      ? null
                      : () => _handleSubmit(_textController.text),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
```

## API Response Format

The response from the `/chat` endpoint will have this format:

```json
{
  "response": "The bot's response text",
  "model": "fine-tuned-assistant (confidence: 0.90)",
  "tokens_used": 432,
  "conversation_id": null
}
```

- `response`: The text response from the chatbot
- `model`: The model used, including confidence score when using fine-tuned data
- `tokens_used`: Number of tokens consumed by the request
- `conversation_id`: Optional conversation ID for tracking (null if not provided)