import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Database, AlertCircle, CheckCircle, Search } from 'lucide-react';
import axios from 'axios';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  hasRelevantData?: boolean;
  dataSourcesCount?: number;
}

interface ServerStatus {
  status: 'checking' | 'connected' | 'error';
  collections?: number;
  totalDocuments?: number;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'مرحباً بك في مساعد أكاديمية الشروق الذكي! 🎓\n\nأنا هنا لمساعدتك في الحصول على معلومات دقيقة حول:\n• البرامج الأكاديمية والتخصصات\n• متطلبات القبول والتسجيل\n• الرسوم الدراسية والمنح\n• أعضاء هيئة التدريس\n• الخدمات الطلابية\n• وأي معلومات أخرى تخص الأكاديمية\n\n---\n\nWelcome to El Shorouk Academy Smart Assistant! 🎓\n\nI\'m here to help you get accurate information about:\n• Academic programs and specializations\n• Admission requirements and registration\n• Tuition fees and scholarships\n• Faculty members\n• Student services\n• And any other information about the academy\n\nكيف يمكنني مساعدتك اليوم؟ / How can I help you today?',
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [serverStatus, setServerStatus] = useState<ServerStatus>({ status: 'checking' });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    checkServerStatus();
  }, []);

  const checkServerStatus = async () => {
    try {
      const [healthResponse, dbResponse] = await Promise.all([
        axios.get('http://localhost:3001/api/health'),
        axios.get('http://localhost:3001/api/test-db')
      ]);
      
      setServerStatus({
        status: 'connected',
        collections: dbResponse.data.totalCollections,
        totalDocuments: dbResponse.data.totalDocuments
      });
    } catch (error) {
      console.error('Server status check failed:', error);
      setServerStatus({ status: 'error' });
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentMessage = inputMessage;
    setInputMessage('');
    setIsLoading(true);

    try {
      const conversationHistory = messages.slice(-8).map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.text
      }));

      const response = await axios.post('http://localhost:3001/api/chat', {
        message: currentMessage,
        conversationHistory
      }, {
        timeout: 30000
      });

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.data.response,
        sender: 'bot',
        timestamp: new Date(),
        hasRelevantData: response.data.hasRelevantData,
        dataSourcesCount: response.data.dataSourcesCount
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'عذراً، حدث خطأ في الاتصال مع الخادم. يرجى التأكد من تشغيل الخادم والمحاولة مرة أخرى.\n\nSorry, there was a connection error with the server. Please make sure the server is running and try again.',
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatMessageText = (text: string) => {
    return text.split('\n').map((line, index) => (
      <React.Fragment key={index}>
        {line}
        {index < text.split('\n').length - 1 && <br />}
      </React.Fragment>
    ));
  };

  const getStatusIcon = () => {
    switch (serverStatus.status) {
      case 'connected':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />;
    }
  };

  const getStatusText = () => {
    switch (serverStatus.status) {
      case 'connected':
        return `متصل بقاعدة البيانات (${serverStatus.collections} مجموعات، ${serverStatus.totalDocuments} وثيقة)`;
      case 'error':
        return 'خطأ في الاتصال بالخادم';
      default:
        return 'جاري التحقق من الاتصال...';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 rtl:space-x-reverse">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  مساعد أكاديمية الشروق
                </h1>
                <p className="text-sm text-gray-600">El Shorouk Academy Assistant</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2 rtl:space-x-reverse">
              {getStatusIcon()}
              <span className="text-sm text-gray-600">
                {getStatusText()}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
          {/* Messages */}
          <div className="h-96 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex items-start space-x-3 rtl:space-x-reverse ${
                  message.sender === 'user' ? 'flex-row-reverse rtl:flex-row' : ''
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    message.sender === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  {message.sender === 'user' ? (
                    <User className="w-4 h-4" />
                  ) : (
                    <Bot className="w-4 h-4" />
                  )}
                </div>
                
                <div
                  className={`max-w-3xl rounded-2xl px-4 py-3 ${
                    message.sender === 'user'
                      ? 'bg-blue-600 text-white ml-auto rtl:mr-auto rtl:ml-0'
                      : 'bg-gray-50 text-gray-900'
                  }`}
                >
                  <div className="text-sm leading-relaxed">
                    {formatMessageText(message.text)}
                  </div>
                  
                  {message.sender === 'bot' && message.hasRelevantData && (
                    <div className="flex items-center space-x-1 rtl:space-x-reverse mt-2 pt-2 border-t border-gray-200">
                      <Database className="w-3 h-3 text-green-600" />
                      <span className="text-xs text-green-600">
                        تم العثور على بيانات من {message.dataSourcesCount} مصدر
                      </span>
                    </div>
                  )}
                  
                  <div className="text-xs opacity-70 mt-1">
                    {message.timestamp.toLocaleTimeString('ar-EG', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex items-start space-x-3 rtl:space-x-reverse">
                <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-gray-600" />
                </div>
                <div className="bg-gray-50 rounded-2xl px-4 py-3">
                  <div className="flex items-center space-x-2 rtl:space-x-reverse">
                    <div className="flex space-x-1 rtl:space-x-reverse">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <span className="text-sm text-gray-500">جاري البحث في قاعدة البيانات...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex items-center space-x-3 rtl:space-x-reverse">
              <div className="flex-1">
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="اكتب سؤالك هنا... / Type your question here..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-sm"
                  rows={1}
                  disabled={isLoading || serverStatus.status !== 'connected'}
                />
              </div>
              <button
                onClick={sendMessage}
                disabled={!inputMessage.trim() || isLoading || serverStatus.status !== 'connected'}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white p-3 rounded-xl transition-colors duration-200 flex-shrink-0"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
            
            {serverStatus.status === 'error' && (
              <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center space-x-2 rtl:space-x-reverse">
                  <AlertCircle className="w-4 h-4 text-red-500" />
                  <span className="text-sm text-red-700">
                    يرجى التأكد من تشغيل الخادم على المنفذ 3001
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => setInputMessage('ما هي التخصصات المتاحة في الأكاديمية؟')}
            className="p-4 bg-white rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all duration-200 text-right"
            disabled={isLoading}
          >
            <div className="text-sm font-medium text-gray-900">التخصصات المتاحة</div>
            <div className="text-xs text-gray-500 mt-1">Available Programs</div>
          </button>
          
          <button
            onClick={() => setInputMessage('ما هي متطلبات القبول؟')}
            className="p-4 bg-white rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all duration-200 text-right"
            disabled={isLoading}
          >
            <div className="text-sm font-medium text-gray-900">متطلبات القبول</div>
            <div className="text-xs text-gray-500 mt-1">Admission Requirements</div>
          </button>
          
          <button
            onClick={() => setInputMessage('معلومات عن الرسوم الدراسية')}
            className="p-4 bg-white rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all duration-200 text-right"
            disabled={isLoading}
          >
            <div className="text-sm font-medium text-gray-900">الرسوم الدراسية</div>
            <div className="text-xs text-gray-500 mt-1">Tuition Fees</div>
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;