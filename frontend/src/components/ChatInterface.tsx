"use client";

import { useState, useRef, useEffect } from 'react';

type Message = {
  role: 'user' | 'assistant';
  content: string;
  vector_context?: string[];
  graph_context?: string[];
};

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userQuery = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userQuery }]);
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/v1/query", {
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: userQuery }),
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: data.answer,
          vector_context: data.vector_context,
          graph_context: data.graph_context
        }]);
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: "An error occurred while fetching the answer." }]);
      }
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'assistant', content: "Failed to connect to the server." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel flex flex-col h-full max-h-[80vh] w-full animate-fade-in" style={{ animationDelay: '0.1s' }}>
      <div className="p-6 border-b border-gray-700/50 bg-black/20 rounded-t-[20px]">
        <h2 className="text-2xl font-bold tracking-tight flex items-center gap-3">
          <span style={{ color: 'var(--neon-purple)' }}>Graph Query</span> Engine
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-6">
        {messages.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-gray-500 gap-4">
            <svg className="w-16 h-16 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <p>Ask a multi-hop question about your knowledge graph.</p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div key={index} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} max-w-full`}>
              <div className={`p-4 rounded-2xl max-w-[85%] ${msg.role === 'user' ? 'message-user rounded-tr-sm' : 'message-bot rounded-tl-sm'}`}>
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
              
              {/* Context display for Assistant */}
              {msg.role === 'assistant' && (msg.vector_context?.length || msg.graph_context?.length) ? (
                <details className="mt-2 text-sm text-gray-400 w-full max-w-[85%] context-section">
                  <summary className="cursor-pointer p-2 opacity-70 hover:opacity-100 transition-opacity">
                    View Retrieval Context
                  </summary>
                  <div className="p-4 border-t border-gray-700/50 space-y-4">
                    {msg.graph_context && msg.graph_context.length > 0 && (
                      <div>
                        <h4 className="text-purple-400 font-semibold mb-1">Graph Relationships (Neo4j)</h4>
                        <ul className="list-disc pl-4 space-y-1">
                          {msg.graph_context.map((ctx, i) => <li key={i}>{ctx}</li>)}
                        </ul>
                      </div>
                    )}
                    {msg.vector_context && msg.vector_context.length > 0 && (
                      <div>
                        <h4 className="text-blue-400 font-semibold mb-1">Text Chunks (ChromaDB)</h4>
                        <div className="space-y-2">
                          {msg.vector_context.map((ctx, i) => (
                            <div key={i} className="bg-black/30 p-2 rounded line-clamp-3 hover:line-clamp-none transition-all">{ctx}</div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </details>
              ) : null}
            </div>
          ))
        )}
        
        {loading && (
          <div className="flex items-start">
            <div className="p-4 rounded-2xl message-bot rounded-tl-sm flex gap-2 items-center">
              <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 bg-black/20 rounded-b-[20px] border-t border-gray-700/50">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="E.g. What companies is John Doe related to based on the recent merger?"
            className="glass-input flex-1"
            disabled={loading}
          />
          <button 
            type="submit" 
            disabled={!input.trim() || loading}
            className="glass-button px-6"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
