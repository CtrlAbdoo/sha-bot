# Flutter Integration Guide

This guide explains how to integrate the Chatbot API with a Flutter mobile or web application.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setting Up the Flutter Project](#setting-up-the-flutter-project)
3. [API Client Implementation](#api-client-implementation)
4. [UI Implementation](#ui-implementation)
5. [Advanced Features](#advanced-features)
6. [Error Handling](#error-handling)
7. [Testing](#testing)

## Prerequisites

- Flutter SDK (latest stable version)
- Dart SDK (latest stable version)
- Basic understanding of Flutter and Dart
- Chatbot API running (see main README)

## Setting Up the Flutter Project

1. Create a new Flutter project:

```bash
flutter create chatbot_app
cd chatbot_app
```

2. Add the required dependencies in `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  provider: ^6.0.5
  shared_preferences: ^2.2.0
  flutter_markdown: ^0.6.17
  intl: ^0.18.1
```

3. Run `flutter pub get` to install dependencies

## API Client Implementation

Create an API client to interact with the chatbot API:

```dart
// lib/services/chatbot_api.dart

import 'dart:convert';
import 'package:http/http.dart' as http;

class ChatbotApiService {
  final String baseUrl;
  final Map<String, String> headers;
  
  ChatbotApiService({
    required this.baseUrl,
    Map<String, String>? headers,
  }) : headers = headers ?? {
          'Content-Type': 'application/json',
        };
  
  // Get available models
  Future<Map<String, dynamic>> getModels() async {
    final response = await http.get(
      Uri.parse('$baseUrl/models'),
      headers: headers,
    );
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load models: ${response.body}');
    }
  }
  
  // Send a message to the chatbot
  Future<Map<String, dynamic>> sendMessage({
    required String message,
    String model = 'gpt-3.5',
    int maxTokens = 500,
    double temperature = 0.7,
    String? conversationId,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/chat'),
      headers: headers,
      body: json.encode({
        'message': message,
        'model': model,
        'max_tokens': maxTokens,
        'temperature': temperature,
        if (conversationId != null) 'conversation_id': conversationId,
      }),
    );
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Failed to get response');
    }
  }
  
  // Check API health
  Future<bool> checkHealth() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
        headers: headers,
      );
      
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}
```

## Chat Model Classes

Create model classes to represent chat messages:

```dart
// lib/models/chat_message.dart

class ChatMessage {
  final String content;
  final bool isUser;
  final DateTime timestamp;
  final String? model;
  
  ChatMessage({
    required this.content,
    required this.isUser,
    DateTime? timestamp,
    this.model,
  }) : timestamp = timestamp ?? DateTime.now();
  
  factory ChatMessage.fromUser(String content) {
    return ChatMessage(content: content, isUser: true);
  }
  
  factory ChatMessage.fromAssistant({
    required String content,
    required String model,
  }) {
    return ChatMessage(
      content: content,
      isUser: false,
      model: model,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'content': content,
      'isUser': isUser,
      'timestamp': timestamp.toIso8601String(),
      'model': model,
    };
  }
  
  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      content: json['content'],
      isUser: json['isUser'],
      timestamp: DateTime.parse(json['timestamp']),
      model: json['model'],
    );
  }
}
```

## Chat Service

Create a chat service to manage the conversation state:

```dart
// lib/services/chat_service.dart

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

import '../models/chat_message.dart';
import 'chatbot_api.dart';

class ChatService extends ChangeNotifier {
  final ChatbotApiService api;
  List<ChatMessage> messages = [];
  bool isLoading = false;
  String currentModel = 'gpt-3.5';
  String? error;
  
  ChatService({required this.api});
  
  // Send a message and get a response
  Future<void> sendMessage(String content) async {
    if (content.trim().isEmpty) return;
    
    // Add user message
    final userMessage = ChatMessage.fromUser(content);
    messages.add(userMessage);
    isLoading = true;
    error = null;
    notifyListeners();
    
    try {
      // Get response from API
      final response = await api.sendMessage(
        message: content,
        model: currentModel,
      );
      
      // Add assistant message
      final assistantMessage = ChatMessage.fromAssistant(
        content: response['response'],
        model: response['model'] ?? currentModel,
      );
      
      messages.add(assistantMessage);
    } catch (e) {
      error = e.toString();
    } finally {
      isLoading = false;
      notifyListeners();
      
      // Save messages to SharedPreferences
      saveMessages();
    }
  }
  
  // Change the current model
  void changeModel(String model) {
    currentModel = model;
    notifyListeners();
  }
  
  // Clear all messages
  void clearMessages() {
    messages.clear();
    notifyListeners();
    saveMessages();
  }
  
  // Load messages from SharedPreferences
  Future<void> loadMessages() async {
    final prefs = await SharedPreferences.getInstance();
    final String? savedMessages = prefs.getString('chat_messages');
    
    if (savedMessages != null) {
      final List<dynamic> decoded = json.decode(savedMessages);
      messages = decoded.map((m) => ChatMessage.fromJson(m)).toList();
      notifyListeners();
    }
  }
  
  // Save messages to SharedPreferences
  Future<void> saveMessages() async {
    final prefs = await SharedPreferences.getInstance();
    final String encoded = json.encode(messages.map((m) => m.toJson()).toList());
    await prefs.setString('chat_messages', encoded);
  }
}
```

## UI Implementation

### Main Chat Screen

```dart
// lib/screens/chat_screen.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:intl/intl.dart';

import '../services/chat_service.dart';
import '../models/chat_message.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({Key? key}) : super(key: key);

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  
  @override
  void initState() {
    super.initState();
    // Load saved messages
    Future.delayed(Duration.zero, () {
      Provider.of<ChatService>(context, listen: false).loadMessages();
    });
  }
  
  @override
  void dispose() {
    _textController.dispose();
    _scrollController.dispose();
    super.dispose();
  }
  
  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Chatbot'),
        actions: [
          PopupMenuButton<String>(
            onSelected: (model) {
              Provider.of<ChatService>(context, listen: false).changeModel(model);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Model changed to $model')),
              );
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'gpt-3.5',
                child: Text('GPT-3.5 Turbo'),
              ),
              const PopupMenuItem(
                value: 'gpt-4',
                child: Text('GPT-4'),
              ),
              const PopupMenuItem(
                value: 'claude-3',
                child: Text('Claude 3 Opus'),
              ),
              const PopupMenuItem(
                value: 'mixtral',
                child: Text('Mixtral 8x7B'),
              ),
              const PopupMenuItem(
                value: 'qwen',
                child: Text('Qwen 72B'),
              ),
            ],
          ),
          IconButton(
            icon: const Icon(Icons.delete),
            onPressed: () {
              Provider.of<ChatService>(context, listen: false).clearMessages();
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: Consumer<ChatService>(
              builder: (context, chatService, child) {
                final messages = chatService.messages;
                
                WidgetsBinding.instance.addPostFrameCallback((_) {
                  _scrollToBottom();
                });
                
                if (messages.isEmpty) {
                  return const Center(
                    child: Text('Send a message to start chatting'),
                  );
                }
                
                return ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.all(8.0),
                  itemCount: messages.length,
                  itemBuilder: (context, index) {
                    final message = messages[index];
                    return _buildMessageBubble(message);
                  },
                );
              },
            ),
          ),
          Consumer<ChatService>(
            builder: (context, chatService, child) {
              if (chatService.error != null) {
                return Container(
                  color: Colors.red[100],
                  padding: const EdgeInsets.all(8.0),
                  width: double.infinity,
                  child: Text(
                    'Error: ${chatService.error}',
                    style: TextStyle(color: Colors.red[900]),
                  ),
                );
              }
              return const SizedBox.shrink();
            },
          ),
          Consumer<ChatService>(
            builder: (context, chatService, child) {
              if (chatService.isLoading) {
                return const Padding(
                  padding: EdgeInsets.all(8.0),
                  child: LinearProgressIndicator(),
                );
              }
              return const SizedBox.shrink();
            },
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _textController,
                    decoration: const InputDecoration(
                      hintText: 'Type a message...',
                      border: OutlineInputBorder(),
                    ),
                    textInputAction: TextInputAction.send,
                    onSubmitted: (text) => _sendMessage(),
                  ),
                ),
                const SizedBox(width: 8.0),
                Consumer<ChatService>(
                  builder: (context, chatService, child) {
                    return IconButton(
                      icon: const Icon(Icons.send),
                      onPressed: chatService.isLoading ? null : _sendMessage,
                    );
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  void _sendMessage() {
    final text = _textController.text.trim();
    if (text.isNotEmpty) {
      Provider.of<ChatService>(context, listen: false).sendMessage(text);
      _textController.clear();
    }
  }
  
  Widget _buildMessageBubble(ChatMessage message) {
    final theme = Theme.of(context);
    final isUser = message.isUser;
    
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4.0),
        padding: const EdgeInsets.all(12.0),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        decoration: BoxDecoration(
          color: isUser ? theme.primaryColor : theme.cardColor,
          borderRadius: BorderRadius.circular(12.0),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 2.0,
              offset: const Offset(0, 1),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            MarkdownBody(
              data: message.content,
              styleSheet: MarkdownStyleSheet(
                p: TextStyle(
                  color: isUser ? Colors.white : theme.textTheme.bodyMedium?.color,
                ),
              ),
            ),
            const SizedBox(height: 4.0),
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  DateFormat('h:mm a').format(message.timestamp),
                  style: TextStyle(
                    fontSize: 10.0,
                    color: isUser ? Colors.white70 : theme.textTheme.bodySmall?.color,
                  ),
                ),
                if (!isUser && message.model != null) ...[
                  const SizedBox(width: 4.0),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 4.0, vertical: 2.0),
                    decoration: BoxDecoration(
                      color: isUser ? Colors.white24 : theme.primaryColor.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(4.0),
                    ),
                    child: Text(
                      message.model!,
                      style: TextStyle(
                        fontSize: 9.0,
                        color: isUser ? Colors.white : theme.primaryColor,
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }
}
```

### Main Application Setup

```dart
// lib/main.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'services/chatbot_api.dart';
import 'services/chat_service.dart';
import 'screens/chat_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Create API client with your server URL
    final apiService = ChatbotApiService(
      baseUrl: 'http://localhost:8000', // Change as needed
    );
    
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (_) => ChatService(api: apiService),
        ),
      ],
      child: MaterialApp(
        title: 'Chatbot App',
        theme: ThemeData(
          primarySwatch: Colors.blue,
          useMaterial3: true,
        ),
        darkTheme: ThemeData.dark(useMaterial3: true).copyWith(
          primaryColor: Colors.blue,
        ),
        themeMode: ThemeMode.system,
        home: const ChatScreen(),
      ),
    );
  }
}
```

## Advanced Features

### Model Selection Dialog

Add a more user-friendly model selection dialog:

```dart
// lib/widgets/model_selection_dialog.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../services/chat_service.dart';
import '../services/chatbot_api.dart';

class ModelSelectionDialog extends StatefulWidget {
  const ModelSelectionDialog({Key? key}) : super(key: key);

  @override
  State<ModelSelectionDialog> createState() => _ModelSelectionDialogState();
}

class _ModelSelectionDialogState extends State<ModelSelectionDialog> {
  bool _isLoading = true;
  Map<String, dynamic> _models = {};
  String? _selectedModel;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadModels();
  }

  Future<void> _loadModels() async {
    final chatService = Provider.of<ChatService>(context, listen: false);
    final api = Provider.of<ChatbotApiService>(context, listen: false);
    
    setState(() {
      _isLoading = true;
      _error = null;
      _selectedModel = chatService.currentModel;
    });
    
    try {
      final modelsResponse = await api.getModels();
      setState(() {
        _models = modelsResponse['models'];
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Select Model'),
      content: SizedBox(
        width: double.maxFinite,
        child: _buildDialogContent(),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('CANCEL'),
        ),
        TextButton(
          onPressed: _selectedModel == null
              ? null
              : () {
                  final chatService =
                      Provider.of<ChatService>(context, listen: false);
                  chatService.changeModel(_selectedModel!);
                  Navigator.of(context).pop();
                },
          child: const Text('SELECT'),
        ),
      ],
    );
  }

  Widget _buildDialogContent() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text('Error: $_error', style: const TextStyle(color: Colors.red)),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: _loadModels,
            child: const Text('Retry'),
          ),
        ],
      );
    }

    return ListView.builder(
      shrinkWrap: true,
      itemCount: _models.length,
      itemBuilder: (context, index) {
        final modelKey = _models.keys.elementAt(index);
        final model = _models[modelKey];
        return RadioListTile<String>(
          title: Text(modelKey),
          subtitle: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(model['description'] ?? ''),
              Text(
                'Context: ${model['context_length']} tokens',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ),
          value: modelKey,
          groupValue: _selectedModel,
          onChanged: (value) {
            setState(() {
              _selectedModel = value;
            });
          },
        );
      },
    );
  }
}
```

## Error Handling

Implement better error handling for API connection issues:

```dart
// lib/widgets/connection_status_widget.dart

import 'package:flutter/material.dart';
import 'dart:async';

import '../services/chatbot_api.dart';

class ConnectionStatusWidget extends StatefulWidget {
  final ChatbotApiService api;
  
  const ConnectionStatusWidget({
    Key? key,
    required this.api,
  }) : super(key: key);

  @override
  State<ConnectionStatusWidget> createState() => _ConnectionStatusWidgetState();
}

class _ConnectionStatusWidgetState extends State<ConnectionStatusWidget> {
  bool _isConnected = false;
  Timer? _timer;
  
  @override
  void initState() {
    super.initState();
    _checkConnection();
    
    // Check connection every 30 seconds
    _timer = Timer.periodic(const Duration(seconds: 30), (_) {
      _checkConnection();
    });
  }
  
  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }
  
  Future<void> _checkConnection() async {
    final isConnected = await widget.api.checkHealth();
    if (mounted) {
      setState(() {
        _isConnected = isConnected;
      });
    }
  }
  
  @override
  Widget build(BuildContext context) {
    if (_isConnected) {
      return const SizedBox.shrink();
    }
    
    return Container(
      color: Colors.red,
      padding: const EdgeInsets.symmetric(vertical: 4.0, horizontal: 16.0),
      child: Row(
        children: [
          const Icon(Icons.error_outline, color: Colors.white),
          const SizedBox(width: 8.0),
          const Expanded(
            child: Text(
              'Not connected to API server',
              style: TextStyle(color: Colors.white),
            ),
          ),
          TextButton(
            onPressed: _checkConnection,
            style: TextButton.styleFrom(
              foregroundColor: Colors.white,
            ),
            child: const Text('RETRY'),
          ),
        ],
      ),
    );
  }
}
```

## Testing

### Unit Testing the API Service

```dart
// test/services/chatbot_api_test.dart

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';

import 'package:your_app_name/services/chatbot_api.dart';

@GenerateMocks([http.Client])
import 'chatbot_api_test.mocks.dart';

void main() {
  group('ChatbotApiService', () {
    late MockClient mockClient;
    late ChatbotApiService apiService;
    
    setUp(() {
      mockClient = MockClient();
      apiService = ChatbotApiService(baseUrl: 'http://localhost:8000');
    });
    
    test('getModels returns models on successful response', () async {
      // Setup mock response
      when(mockClient.get(
        Uri.parse('http://localhost:8000/models'),
        headers: anyNamed('headers'),
      )).thenAnswer((_) async => http.Response(
        '{"models": {"gpt-3.5": {"id": "openai/gpt-3.5-turbo", "context_length": 16000, "description": "Fast and economical"}}}',
        200,
      ));
      
      // Call the method
      final result = await apiService.getModels();
      
      // Verify the result
      expect(result, isA<Map<String, dynamic>>());
      expect(result['models'], isNotNull);
      expect(result['models']['gpt-3.5'], isNotNull);
    });
    
    test('sendMessage throws exception on error', () async {
      // Setup mock response
      when(mockClient.post(
        Uri.parse('http://localhost:8000/chat'),
        headers: anyNamed('headers'),
        body: anyNamed('body'),
      )).thenAnswer((_) async => http.Response(
        '{"detail": "Invalid model"}',
        400,
      ));
      
      // Call the method and expect exception
      expect(
        () => apiService.sendMessage(message: 'Hello'),
        throwsException,
      );
    });
  });
}
```

## Deployment Notes

When deploying your Flutter app with the chatbot integration, consider the following:

1. **API URL Configuration**:
   - For development: Use `http://localhost:8000`
   - For production: Use your deployed API URL (e.g., `https://your-api-domain.com`)

2. **Mobile Platform Considerations**:
   - For Android: Add internet permission in `AndroidManifest.xml`
   - For iOS: Configure App Transport Security settings in `Info.plist`

3. **Web Deployment**:
   - Ensure CORS is properly configured on your API server
   - For production, use HTTPS for both the API and web app

4. **Environment Configuration**:
   - Create a configuration file that can be switched between development and production

## Conclusion

This integration guide provides the foundation for connecting a Flutter application to your Chatbot API. By following these steps, you can create a cross-platform mobile and web application that leverages the power of various language models through the OpenRouter API.

For any issues or questions about this integration, please refer to the main project repository or submit an issue. 