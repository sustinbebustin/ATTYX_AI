import React, { useState, useEffect, useCallback, Suspense } from 'react';
import { createClient } from '@supabase/supabase-js';
import { v4 as uuidv4 } from 'uuid';

// Initialize Supabase client
const supabase = createClient(
  'https://rdgnjccyntmolhdizbhj.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJkZ25qY2N5bnRtb2xoZGl6YmhqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzczNTI0MzYsImV4cCI6MjA1MjkyODQzNn0.ik_rOz8YxhsPnExPac-YxErjiTvGVnrWryDWkt_D7UQ'
);

// Types
interface Message {
  id: string;
  content: string;
  type: 'human' | 'ai' | 'error' | 'system';
  timestamp: string;
  metadata?: {
    action?: string;
    data?: any;
  };
}

interface ViewState {
  tasks: any[];
  pipeline: {
    stages: string[];
    deals: any[];
  };
  reporting: {
    metrics: any[];
    period: string;
  };
}

// Error Boundary Component
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">
          <h2>Something went wrong</h2>
          <button
            onClick={() => this.setState({ hasError: false })}
            className="mt-2 text-red-600 hover:text-red-800"
          >
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// Loading Component
const LoadingSpinner = () => (
  <div className="flex justify-center p-4">
    <div className="h-8 w-8 animate-spin rounded-full border-2 border-gray-300 border-t-blue-600" />
  </div>
);

// Main Component
export default function Page() {
  // State Management
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>('');
  const [sessionId] = useState<string>(uuidv4());
  const [isChatOpen, setIsChatOpen] = useState<boolean>(true);
  const [chatWidth, setChatWidth] = useState<number>(440);
  const [isResizing, setIsResizing] = useState<boolean>(false);

  // Handle mouse move during resize
  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isResizing) return;
    
    const windowWidth = window.innerWidth;
    const minWidth = windowWidth * 0.15; // 15% of screen width
    const maxWidth = windowWidth * 0.50; // 50% of screen width
    const newWidth = windowWidth - e.clientX;
    
    // Constrain width between 25% and 50% of screen width
    setChatWidth(Math.min(Math.max(newWidth, minWidth), maxWidth));
  }, [isResizing]);

  // Handle mouse up to stop resizing
  const handleMouseUp = useCallback(() => {
    setIsResizing(false);
  }, []);

  // Add and remove event listeners for resize
  useEffect(() => {
    if (isResizing) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing, handleMouseMove, handleMouseUp]);
  const [currentView, setCurrentView] = useState<'tasks' | 'pipeline' | 'reporting'>('tasks');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [viewState, setViewState] = useState<ViewState>({
    tasks: [],
    pipeline: { stages: [], deals: [] },
    reporting: { metrics: [], period: 'month' }
  });

  // Real-time subscription setup
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
        (payload) => {
          if (payload.new.session_id === sessionId) {
            const messageData = payload.new.message.message;
            
            if (messageData.type === 'system' && messageData.metadata?.action === 'updateView') {
              handleViewUpdate(messageData.metadata.data);
            } else {
              setMessages(prev => [...prev, {
                ...messageData,
                type: messageData.type || 'ai',
                id: uuidv4(),
                timestamp: new Date().toISOString()
              }]);
            }
          }
        }
      )
      .subscribe();

    return () => {
      channel.unsubscribe();
    };
  }, [sessionId]);

  // View state update handler
  const handleViewUpdate = useCallback((data: any) => {
    setViewState(prev => ({
      ...prev,
      [currentView]: { ...prev[currentView], ...data }
    }));
  }, [currentView]);

  // Message submission handler
  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    setIsLoading(true);
    const newMessage: Message = {
      id: uuidv4(),
      content: input,
      type: 'human',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, newMessage]);

    try {
      const response = await fetch('/api/sales-assistant', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: input,
          user_id: "NA",
          request_id: uuidv4(),
          session_id: sessionId,
          current_view: currentView,
          view_state: viewState[currentView]
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.type === 'command' && data.action === 'setView') {
        setCurrentView(data.view);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setMessages(prev => [...prev, {
        id: uuidv4(),
        content: `Error: ${errorMessage}`,
        type: 'error',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsLoading(false);
      setInput('');
    }
  }, [input, sessionId, currentView, viewState, isLoading]);

  // View Components
  const TaskView = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-gray-900">Tasks</h2>
        <button className="rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm text-gray-700 shadow-sm hover:bg-gray-50">
          New Task
        </button>
      </div>
      <div className="grid gap-4">
        {viewState.tasks.map((task, i) => (
          <div key={i} className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <h3 className="font-medium text-gray-900">{task.title}</h3>
            <p className="text-sm text-gray-500 mt-1">{task.description}</p>
          </div>
        ))}
      </div>
    </div>
  );

  const PipelineView = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-gray-900">Pipeline</h2>
        <button className="rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm text-gray-700 shadow-sm hover:bg-gray-50">
          Add Deal
        </button>
      </div>
      <div className="grid grid-cols-4 gap-4">
        {viewState.pipeline.stages.map((stage, i) => (
          <div key={i} className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <h3 className="font-medium text-gray-900">{stage}</h3>
            <div className="mt-2 space-y-2">
              {viewState.pipeline.deals
                .filter(deal => deal.stage === stage)
                .map((deal, j) => (
                  <div key={j} className="rounded-lg bg-gray-50 p-2">
                    <p className="font-medium text-gray-900">{deal.name}</p>
                    <p className="text-sm text-gray-500">${deal.value}</p>
                  </div>
                ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const ReportingView = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-gray-900">Analytics</h2>
        <select
          value={viewState.reporting.period}
          onChange={(e) => handleViewUpdate({ period: e.target.value })}
          className="rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm text-gray-700 shadow-sm"
        >
          <option value="week">This Week</option>
          <option value="month">This Month</option>
          <option value="quarter">This Quarter</option>
          <option value="year">This Year</option>
        </select>
      </div>
      <div className="grid grid-cols-3 gap-4">
        {viewState.reporting.metrics.map((metric, i) => (
          <div key={i} className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <h3 className="font-medium text-gray-900">{metric.name}</h3>
            <p className="text-2xl font-bold text-gray-900 mt-2">{metric.value}</p>
            <p className="text-sm text-gray-500 mt-1">{metric.change}</p>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Main content area */}
      <div className={`flex-1 flex items-center justify-center ${
        isChatOpen ? `w-[calc(100%-${chatWidth}px)]` : 'w-full'
      } animate-fade-in transition-all duration-200`}>
        <div className="max-w-5xl w-full items-center justify-between px-8">
          <h1 className="text-6xl font-bold tracking-tight text-gray-900 animate-slide-up">
            Welcome to{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-primary-400">
              Attyx AI
            </span>
          </h1>
          <p className="mt-6 text-xl text-gray-600 animate-slide-up" style={{ animationDelay: '200ms' }}>
            Your intelligent CRM assistant powered by advanced AI. Manage deals, analyze customer relationships, and get actionable insights.
          </p>
          
          {/* Dashboard Views */}
          <div className="mt-16 space-y-8 w-full">
            <ErrorBoundary>
              <Suspense fallback={<LoadingSpinner />}>
                {currentView === 'tasks' && (
                  <div className="rounded-2xl bg-white p-8 shadow-sm border border-gray-200">
                    <TaskView />
                  </div>
                )}

                {currentView === 'pipeline' && (
                  <div className="rounded-2xl bg-white p-8 shadow-sm border border-gray-200">
                    <PipelineView />
                  </div>
                )}

                {currentView === 'reporting' && (
                  <div className="rounded-2xl bg-white p-8 shadow-sm border border-gray-200">
                    <ReportingView />
                  </div>
                )}
              </Suspense>
            </ErrorBoundary>
          </div>
        </div>
      </div>

      {/* Chat Interface - 440px fixed width */}
      {isChatOpen && (
        <div
          className={`relative flex flex-col bg-white border-l border-gray-200`}
          style={{ width: `${chatWidth}px` }}
        >
          {/* Resize Handle */}
          <div
            className="absolute left-0 top-0 w-1 h-full cursor-ew-resize hover:bg-blue-500/50 transition-colors"
            onMouseDown={() => setIsResizing(true)}
          />
          {/* Header */}
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              Attyx AI Assistant
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              Your intelligent CRM companion
            </p>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="space-y-4">
                <div className="rounded-lg border border-gray-200 bg-white px-4 py-3 text-left text-sm text-gray-700 shadow-sm">
                  <h3 className="font-medium mb-2">Example Questions</h3>
                  <button
                    className="block w-full rounded-lg bg-white border border-gray-200 p-2 text-left text-sm text-gray-700 hover:border-gray-300 hover:bg-gray-50 hover:shadow-md transition-all"
                    onClick={() => setInput("Show Q3 pipeline")}
                  >
                    "Show Q3 pipeline"
                  </button>
                  <button
                    className="block w-full rounded-lg bg-white border border-gray-200 p-2 text-left text-sm text-gray-700 hover:border-gray-300 hover:bg-gray-50 hover:shadow-md transition-all"
                    onClick={() => setInput("Create follow-up task")}
                  >
                    "Create follow-up task"
                  </button>
                  <button
                    className="block w-full rounded-lg bg-white border border-gray-200 p-2 text-left text-sm text-gray-700 hover:border-gray-300 hover:bg-gray-50 hover:shadow-md transition-all"
                    onClick={() => setInput("Analyze lead conversion")}
                  >
                    "Analyze lead conversion"
                  </button>
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`rounded-2xl p-4 ${
                    message.type === 'human'
                      ? 'bg-blue-600 text-white ml-12'
                      : message.type === 'error'
                      ? 'bg-red-50 text-red-700'
                      : 'bg-gray-100 text-gray-900 mr-12'
                  }`}
                >
                  {message.content}
                </div>
              ))
            )}
            {isLoading && <LoadingSpinner />}
          </div>

          {/* Input Section */}
          <div className="border-t border-gray-200 p-4 bg-white">
            <form onSubmit={handleSubmit} className="flex items-center gap-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 min-h-[44px] max-h-32 px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                disabled={isLoading}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    if (input.trim()) handleSubmit(e as any);
                  }
                }}
              />
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className={`rounded-full p-2 text-white ${
                  input.trim() && !isLoading
                    ? 'bg-blue-600 hover:bg-blue-700'
                    : 'bg-gray-300 cursor-not-allowed'
                }`}
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Toggle Chat Button */}
      <button
        onClick={() => setIsChatOpen(!isChatOpen)}
        className="fixed right-4 top-4 rounded-full p-2 bg-white border border-gray-200 shadow-sm hover:bg-gray-50"
      >
        {isChatOpen ? (
          <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        )}
      </button>
    </div>
  );
}
