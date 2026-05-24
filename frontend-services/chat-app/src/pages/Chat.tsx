import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, Send, Settings, LogOut, User, Bot, Zap, PlusCircle, Clock } from 'lucide-react';
import { chatApi } from '../services/api';
import type { ChatMessage, ChatResponse } from '../services/api';

// Cookie utility functions
const cookieUtils = {
  set: (name: string, value: any, days: number = 30) => {
    const expires = new Date();
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${name}=${encodeURIComponent(JSON.stringify(value))};expires=${expires.toUTCString()};path=/`;
  },
  
  get: <T,>(name: string): T | null => {
    const nameEQ = name + '=';
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) === ' ') c = c.substring(1);
      if (c.indexOf(nameEQ) === 0) {
        try {
          return JSON.parse(decodeURIComponent(c.substring(nameEQ.length))) as T;
        } catch {
          return null;
        }
      }
    }
    return null;
  },
  
  delete: (name: string) => {
    document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`;
  }
};

interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  timestamp: number;
}

// Format text with basic markdown support
const FormattedText: React.FC<{ content: string }> = ({ content }) => {
  const formatContent = (text: string) => {
    // Split by code blocks first
    const parts = text.split(/(```[\s\S]*?```)/g);
    
    return parts.map((part, index) => {
      if (part.startsWith('```') && part.endsWith('```')) {
        // Code block - extract language and code
        const codeContent = part.slice(3, -3).trim();
        const lines = codeContent.split('\n');
        const firstLine = lines[0].trim();
        
        // Check if first line is a language identifier (common languages)
        const commonLanguages = ['javascript', 'js', 'python', 'py', 'java', 'cpp', 'c', 'html', 'css', 'sql', 'json', 'typescript', 'ts', 'bash', 'sh'];
        const hasLanguage = commonLanguages.some(lang => firstLine.toLowerCase() === lang);
        
        const code = hasLanguage ? lines.slice(1).join('\n') : codeContent;
        
        return (
          <pre key={index} style={{
            background: 'rgba(0,0,0,0.3)',
            padding: '1rem',
            borderRadius: '0.5rem',
            overflowX: 'auto',
            margin: '0.75rem 0',
            fontFamily: 'monospace',
            fontSize: '0.875rem',
            lineHeight: '1.5'
          }}>
            <code>{code}</code>
          </pre>
        );
      }
      
      // Regular text with formatting
      return (
        <span key={index}>
          {part.split('\n').map((line, lineIdx) => {
            // Handle bold (**text** or __text__)
            const boldParts = line.split(/(\*\*.*?\*\*|__.*?__)/g);
            
            return (
              <React.Fragment key={lineIdx}>
                {boldParts.map((boldPart, boldIdx) => {
                  if (boldPart.startsWith('**') && boldPart.endsWith('**')) {
                    return <strong key={boldIdx}>{boldPart.slice(2, -2)}</strong>;
                  }
                  if (boldPart.startsWith('__') && boldPart.endsWith('__')) {
                    return <strong key={boldIdx}>{boldPart.slice(2, -2)}</strong>;
                  }
                  
                  // Handle inline code (`text`)
                  const codeParts = boldPart.split(/(`.*?`)/g);
                  return (
                    <React.Fragment key={boldIdx}>
                      {codeParts.map((codePart, codeIdx) => {
                        if (codePart.startsWith('`') && codePart.endsWith('`')) {
                          return (
                            <code key={codeIdx} style={{
                              background: 'rgba(99, 102, 241, 0.2)',
                              padding: '0.125rem 0.375rem',
                              borderRadius: '0.25rem',
                              fontFamily: 'monospace',
                              fontSize: '0.875em'
                            }}>
                              {codePart.slice(1, -1)}
                            </code>
                          );
                        }
                        return codePart;
                      })}
                    </React.Fragment>
                  );
                })}
                {lineIdx < part.split('\n').length - 1 && <br />}
              </React.Fragment>
            );
          })}
        </span>
      );
    });
  };

  return <div className="formatted-content">{formatContent(content)}</div>;
};

export default function Chat() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string>(() => crypto.randomUUID());
  const [savedConversations, setSavedConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  
  const token = localStorage.getItem('sc_chat_token');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!token) {
      navigate('/');
    }
  }, [token, navigate]);

  // Load saved conversations on mount
  useEffect(() => {
    const saved = cookieUtils.get<Conversation[]>('sc_conversations') || [];
    setSavedConversations(saved);
  }, []);

  // Save conversations whenever they change
  useEffect(() => {
    if (savedConversations.length > 0) {
      cookieUtils.set('sc_conversations', savedConversations, 30);
    }
  }, [savedConversations]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const generateTitle = (firstMessage: string) => {
    return firstMessage.length > 30 
      ? firstMessage.substring(0, 30) + '...' 
      : firstMessage;
  };

  const handleSend = async () => {
    if (!input.trim() || !token) return;

    const userMessage: ChatMessage = { role: 'user', content: input };
    const currentHistory = [...messages];
    
    setMessages([...currentHistory, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage(
        userMessage.content,
        token,
        conversationId,
        currentHistory
      ).catch(() => {
        console.log('API not reachable, using mock response');
        return new Promise<ChatResponse>(resolve => {
          setTimeout(() => {
            resolve({
              route: 'mock_fallback',
              hit: false,
              response: "This is a mock response because the backend API couldn't be reached. Ensure Semantic-Cache is running on localhost:8000.",
              cache_level: 'none',
              latency_ms: 1500
            });
          }, 1500);
        });
      });

      setMessages(prev => [...prev, { role: 'assistant', content: response.response }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I encountered an error connecting to the Semantic-Cache API." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const startNewChat = () => {
    // Save current conversation if it has messages
    if (messages.length > 0) {
      const conversation: Conversation = {
        id: conversationId,
        title: generateTitle(messages[0].content),
        messages: messages,
        timestamp: Date.now()
      };
      
      setSavedConversations(prev => {
        const filtered = prev.filter(c => c.id !== conversationId);
        return [conversation, ...filtered].slice(0, 50); // Keep last 50 conversations
      });
    }
    
    setMessages([]);
    const newId = crypto.randomUUID();
    setConversationId(newId);
    setActiveConversationId(null);
  };

  const loadConversation = (conversation: Conversation) => {
    // Save current conversation first if it has messages
    if (messages.length > 0 && conversation.id !== conversationId) {
      const currentConv: Conversation = {
        id: conversationId,
        title: generateTitle(messages[0].content),
        messages: messages,
        timestamp: Date.now()
      };
      
      setSavedConversations(prev => {
        const filtered = prev.filter(c => c.id !== currentConv.id && c.id !== conversation.id);
        return [currentConv, ...filtered].slice(0, 50);
      });
    }
    
    setMessages(conversation.messages);
    setConversationId(conversation.id);
    setActiveConversationId(conversation.id);
  };

  const deleteConversation = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    setSavedConversations(prev => prev.filter(c => c.id !== id));
    if (activeConversationId === id) {
      startNewChat();
    }
  };

  const handleLogout = () => {
    // Save current conversation before logout
    if (messages.length > 0) {
      const conversation: Conversation = {
        id: conversationId,
        title: generateTitle(messages[0].content),
        messages: messages,
        timestamp: Date.now()
      };
      
      setSavedConversations(prev => {
        const filtered = prev.filter(c => c.id !== conversationId);
        return [conversation, ...filtered].slice(0, 50);
      });
    }
    
    localStorage.removeItem('sc_chat_token');
    localStorage.removeItem('sc_tenant_id');
    navigate('/');
  };

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (days === 1) {
      return 'Yesterday';
    } else if (days < 7) {
      return date.toLocaleDateString([], { weekday: 'short' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  return (
    <div className="app-layout animate-fade-in">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Zap size={20} className="text-gradient" />
            <span style={{ fontWeight: 600, fontSize: '1.125rem' }}>Semantic Chat</span>
          </div>
          <button className="btn-icon" onClick={startNewChat} title="New Chat">
            <PlusCircle size={20} />
          </button>
        </div>
        
        <div className="sidebar-content" style={{ flex: 1, overflowY: 'auto' }}>
          <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.5rem', fontWeight: 600 }}>
            Recent Sessions
          </div>
          
          {/* Current Session */}
          <div 
            className={`chat-history-item ${!activeConversationId ? 'active' : ''}`}
            onClick={() => {
              if (activeConversationId) {
                startNewChat();
              }
            }}
            style={{ cursor: 'pointer' }}
          >
            <MessageSquare size={16} />
            <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              Current Session
            </span>
          </div>

          {/* Saved Conversations */}
          {savedConversations.length > 0 && (
            <>
              <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', margin: '1rem 0 0.5rem 0', fontWeight: 600 }}>
                History
              </div>
              {savedConversations.map((conv) => (
                <div 
                  key={conv.id}
                  className={`chat-history-item ${activeConversationId === conv.id ? 'active' : ''}`}
                  onClick={() => loadConversation(conv)}
                  style={{ 
                    cursor: 'pointer', 
                    position: 'relative',
                    paddingRight: '2rem'
                  }}
                >
                  <MessageSquare size={16} />
                  <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                    <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {conv.title}
                    </span>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      <Clock size={10} />
                      {formatTime(conv.timestamp)}
                    </span>
                  </div>
                  <button
                    onClick={(e) => deleteConversation(e, conv.id)}
                    style={{
                      position: 'absolute',
                      right: '0.5rem',
                      top: '50%',
                      transform: 'translateY(-50%)',
                      background: 'transparent',
                      border: 'none',
                      color: 'var(--text-muted)',
                      cursor: 'pointer',
                      padding: '0.25rem',
                      opacity: 0,
                      transition: 'opacity 0.2s'
                    }}
                    className="delete-btn"
                  >
                    ×
                  </button>
                </div>
              ))}
            </>
          )}
        </div>

        <div className="sidebar-footer">
          <button className="btn-secondary" style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', padding: '0.75rem' }} onClick={handleLogout}>
            <LogOut size={16} /> Logout
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="main-content">
        <div className="chat-header">
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontWeight: 500 }}>
              {activeConversationId 
                ? savedConversations.find(c => c.id === activeConversationId)?.title || 'Chat'
                : 'Default Domain'}
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              {activeConversationId ? 'Previous conversation' : 'Using general context'}
            </span>
          </div>
          <button className="btn-icon">
            <Settings size={20} />
          </button>
        </div>

        <div className="messages-container">
          {messages.length === 0 ? (
            <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
              <div className="btn-icon" style={{ background: 'rgba(99, 102, 241, 0.1)', color: 'var(--accent-primary)', width: '4rem', height: '4rem', marginBottom: '1rem' }}>
                <Zap size={32} />
              </div>
              <h2 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem' }}>How can I help you today?</h2>
              <p>Type a message to start caching context.</p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className="message-wrapper">
                <div className="message">
                  <div className={`message-avatar ${msg.role === 'user' ? 'avatar-user' : 'avatar-assistant'}`}>
                    {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                  </div>
                  <div className="message-content">
                    <p style={{ fontWeight: 600, marginBottom: '0.25rem', color: msg.role === 'user' ? 'var(--text-secondary)' : 'var(--accent-primary)' }}>
                      {msg.role === 'user' ? 'You' : 'Semantic AI'}
                    </p>
                    {msg.role === 'assistant' ? (
                      <FormattedText content={msg.content} />
                    ) : (
                      <p>{msg.content}</p>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="message-wrapper">
              <div className="message">
                <div className="message-avatar avatar-assistant">
                  <Bot size={16} />
                </div>
                <div className="message-content" style={{ display: 'flex', alignItems: 'center' }}>
                  <div className="typing-indicator">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area-wrapper">
          <div className="input-container">
            <textarea
              className="chat-input"
              placeholder="Message Semantic Cache..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
              rows={1}
            />
            <button 
              className="send-button"
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
            >
              <Send size={16} />
            </button>
          </div>
          <div style={{ textAlign: 'center', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
            Semantic-Cache can route queries to specific models and store context history.
          </div>
        </div>
      </div>
    </div>
  );
}