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
          setMessages(prev => [...prev, payload.new.message.message]);
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
      content: input,
      type: 'human'
    }]);
    
    try {
      const response = await fetch('/api/sales-assistant', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${process.env.API_BEARER_TOKEN || 'dev_token'}`, // TEMP FALLBACK FOR DEVELOPMENT
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
    <div className="flex h-screen bg-slate-900 text-slate-100">
      <div className={`flex-grow p-6 ${isChatOpen ? 'w-[85%]' : 'w-full'}`}>
        <div className="h-full rounded-lg bg-slate-800 p-4">
          <h1 className="text-2xl font-bold text-indigo-400">Sales Dashboard</h1>
          <div className="mt-4">
            {/* Dashboard content will go here */}
          </div>
        </div>
      </div>

      {isChatOpen && (
        <div className="w-[15%] border-l border-slate-700">
          <div className="flex h-full flex-col">
            <div className="flex-1 overflow-y-auto p-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`mb-3 rounded-lg p-3 ${
                    message.type === 'human' 
                      ? 'ml-4 bg-indigo-600' 
                      : 'mr-4 bg-slate-700'
                  }`}
                >
                  <p className="text-sm">{message.content}</p>
                </div>
              ))}
            </div>
            <form onSubmit={handleSubmit} className="border-t border-slate-700 p-4">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                className="w-full rounded bg-slate-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="Type your message..."
              />
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
