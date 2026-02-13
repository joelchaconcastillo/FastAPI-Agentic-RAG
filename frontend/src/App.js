import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [provider, setProvider] = useState('openai');
  const [conversationId, setConversationId] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [thinkingMessage, setThinkingMessage] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, thinkingMessage]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;

    const userMessage = input.trim();
    setInput('');
    
    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsStreaming(true);
    setThinkingMessage('');

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          provider: provider,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from server');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.type === 'thinking') {
                setThinkingMessage(data.content);
              } else if (data.type === 'token') {
                setThinkingMessage('');
                assistantMessage += data.content;
                // Update the last message or create a new one
                setMessages(prev => {
                  const newMessages = [...prev];
                  if (newMessages[newMessages.length - 1]?.role === 'assistant' && 
                      newMessages[newMessages.length - 1]?.streaming) {
                    newMessages[newMessages.length - 1].content = assistantMessage;
                  } else {
                    newMessages.push({ 
                      role: 'assistant', 
                      content: assistantMessage,
                      streaming: true 
                    });
                  }
                  return newMessages;
                });
              } else if (data.type === 'done') {
                setThinkingMessage('');
                setMessages(prev => {
                  const newMessages = [...prev];
                  if (newMessages[newMessages.length - 1]?.streaming) {
                    delete newMessages[newMessages.length - 1].streaming;
                  }
                  return newMessages;
                });
              } else if (data.type === 'error') {
                setThinkingMessage('');
                setMessages(prev => [...prev, { 
                  role: 'error', 
                  content: `Error: ${data.content}` 
                }]);
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }

      // Generate conversation ID if not exists
      if (!conversationId) {
        setConversationId(Date.now().toString());
      }

    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        role: 'error', 
        content: `Error: ${error.message}` 
      }]);
    } finally {
      setIsStreaming(false);
      setThinkingMessage('');
    }
  };

  const handleNewConversation = () => {
    setMessages([]);
    setConversationId(null);
    setThinkingMessage('');
  };

  return (
    <div className="App">
      <div className="chat-container">
        <div className="chat-header">
          <h1>FastAPI Agentic RAG</h1>
          <div className="header-controls">
            <select 
              value={provider} 
              onChange={(e) => setProvider(e.target.value)}
              disabled={isStreaming}
              className="provider-select"
            >
              <option value="openai">OpenAI</option>
              <option value="gemini">Gemini</option>
            </select>
            <button 
              onClick={handleNewConversation}
              disabled={isStreaming}
              className="new-conversation-btn"
            >
              New Conversation
            </button>
          </div>
        </div>

        <div className="messages-container">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className="message-role">
                {msg.role === 'user' ? '👤 You' : 
                 msg.role === 'assistant' ? '🤖 Assistant' : '⚠️ Error'}
              </div>
              <div className="message-content">
                {msg.content}
                {msg.streaming && <span className="cursor">▊</span>}
              </div>
            </div>
          ))}
          
          {thinkingMessage && (
            <div className="message assistant thinking">
              <div className="message-role">🤖 Assistant</div>
              <div className="message-content">
                {thinkingMessage}
                <span className="thinking-dots">...</span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="input-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={isStreaming}
            className="message-input"
          />
          <button 
            type="submit" 
            disabled={isStreaming || !input.trim()}
            className="send-button"
          >
            {isStreaming ? '...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
