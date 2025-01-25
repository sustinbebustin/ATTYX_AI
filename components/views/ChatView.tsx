import { useEffect, useRef } from 'react';
import { useChatStore } from '../../stores/chatStore';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function ChatView() {
  const { messages, addMessage, isProcessing, subscribeToSession, currentSession } = useChatStore();
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (currentSession) {
      const subscription = subscribeToSession(currentSession);
      return () => {
        subscription?.unsubscribe();
      };
    }
  }, [currentSession, subscribeToSession]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-3xl p-4 rounded-lg ${
                message.role === 'user'
                  ? 'bg-blue-100 dark:bg-blue-900'
                  : 'bg-gray-100 dark:bg-gray-800'
              }`}
            >
              <Markdown remarkPlugins={[remarkGfm]} className="prose dark:prose-invert">
                {message.content}
              </Markdown>
              {message.status === 'sending' && (
                <div className="text-xs text-gray-500 mt-2">Sending...</div>
              )}
            </div>
          </div>
        ))}
        <div ref={endOfMessagesRef} />
      </div>
      
      {isProcessing && (
        <div className="p-4 border-t bg-white dark:bg-gray-900">
          <div className="flex items-center text-gray-500 dark:text-gray-400">
            <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
                fill="none"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            Generating response...
          </div>
        </div>
      )}
    </div>
  );
}