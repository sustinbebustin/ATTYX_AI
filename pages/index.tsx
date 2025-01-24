import { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';
import { v4 as uuidv4 } from 'uuid';

const supabase = createClient(
  'https://rdgnjccyntmolhdizbhj.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJkZ25qY2N5bnRtb2xoZGl6YmhqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzczNTI0MzYsImV4cCI6MjA1MjkyODQzNn0.ik_rOz8YxhsPnExPac-YxErjiTvGVnrWryDWkt_D7UQ'
);

export default function Dashboard() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [sessionId] = useState(uuidv4());
  const [isChatOpen, setIsChatOpen] = useState(true);

  useEffect(() => {
    const channel = supabase
      .channel('realtime-messages')
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'messages'
        },
        async (payload) => {
        if (payload.new.session_id === sessionId) {
          setMessages(prev => [...prev, {
            ...payload.new.message.message,
            type: 'ai',
            id: uuidv4(),
            timestamp: new Date().toISOString()
          }]);
        }
      })
      .subscribe();

    return () => {
      channel.unsubscribe();
    };
  }, [sessionId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add human message
    // Add human message optimistically
    setMessages(prev => [...prev, {
      id: uuidv4(),
      content: input,
      type: 'human',
      timestamp: new Date().toISOString()
    }]);
    
    try {
      const response = await fetch('/api/sales-assistant', {
        method: 'POST',
        headers: {
          // Authentication handled by server API route
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: input,
          user_id: "NA",
          request_id: uuidv4(),
          session_id: sessionId
        })
      });

      if (!response.ok) {
        const errorBody = await response.json();
        throw new Error(errorBody.error || 'API request failed');
      }
      
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        id: uuidv4(),
        content: 'Error processing request',
        type: 'error',
        timestamp: new Date().toISOString()
      }]);
    }
    
    setInput('');
  };

  return (
    <div className="flex h-screen bg-[#000000]">
      {/* Main Dashboard Area */}
      <div className={`relative transition-all duration-300 ${isChatOpen ? 'w-[85%]' : 'w-full'}`}>
        <div className="absolute inset-0 flex flex-col">
          <div className="h-16 border-b border-white/10 bg-gradient-to-b from-black/80 to-black/20 backdrop-blur-md">
            <div className="flex h-full items-center px-6">
              <h1 className="text-lg font-semibold text-gray-300">ATTYX Sales Dashboard</h1>
            </div>
          </div>
          <div className="flex-1 bg-gradient-to-br from-gray-900/95 to-black p-6">
            <div className="h-full rounded-xl border border-white/10 bg-gradient-to-br from-gray-900/50 to-gray-900/20 backdrop-blur-xl">
              {/* Dashboard content will go here */}
            </div>
          </div>
        </div>
      </div>

      {/* Chat Interface */}
      {isChatOpen && (
        <div className="w-[15%] border-l border-white/10 bg-gradient-to-b from-black/80 via-black/60 to-black/80 backdrop-blur-xl">
          <div className="flex h-full flex-col">
            <div className="flex-1 overflow-y-auto px-4 pt-6">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'human' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`relative max-w-[85%] rounded-2xl p-4 ${
                        message.type === 'human'
                          ? 'bg-blue-500/90 text-white'
                          : 'bg-gray-700/60 text-gray-100'
                      }`}
                      style={{
                        boxShadow: '0 4px 12px -2px rgba(0, 0, 0, 0.2)'
                      }}
                    >
                      <div className="absolute -bottom-1 h-3 w-3 transform rotate-45 bg-inherit"
                        style={{
                          [message.type === 'human' ? 'right' : 'left']: '12px'
                        }}
                      />
                      <p className="text-[15px] leading-snug">{message.content}</p>
                      <div className="mt-1.5 flex items-center justify-end space-x-1.5">
                        <span className="text-xs opacity-60">
                          {new Date(message.timestamp).toLocaleTimeString([], {
                            hour: 'numeric',
                            minute: '2-digit'
                          })}
                        </span>
                        {message.type === 'human' && (
                          <svg className="h-3 w-3 text-white/60" fill="currentColor" viewBox="0 0 12 12">
                            <path d="M10.28 2.28L3.989 8.575 1.695 6.28A1 1 0 00.28 7.695l3 3a1 1 0 001.414 0l7-7A1 1 0 0010.28 2.28z" />
                          </svg>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <form onSubmit={handleSubmit} className="border-t border-white/10 p-4">
              <div className="relative rounded-xl bg-gray-800/50 backdrop-blur-sm">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  className="w-full bg-transparent py-3 pl-4 pr-12 text-sm text-gray-100 placeholder-gray-400 focus:outline-none"
                  placeholder="Message ATTYX AI..."
                />
                <button
                  type="submit"
                  className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full p-1.5 hover:bg-gray-700/50 transition-colors"
                  disabled={!input.trim()}
                >
                  <svg className="h-5 w-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      <button
        onClick={() => setIsChatOpen(!isChatOpen)}
        className="absolute right-4 top-4 rounded-lg bg-slate-800 p-2 hover:bg-slate-700"
      >
        {isChatOpen ? '→' : '←'}
      </button>
    </div>
  );
}
