import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { v4 as uuidv4 } from 'uuid';

const supabase: SupabaseClient = createClient(
  'https://eyqygdvatsmorbhhgqgm.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV5cXlnZHZhdHNtb3JiaGhncWdtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzc4MDQ3NDIsImV4cCI6MjA1MzM4MDc0Mn0.w3jJ1BOUOT2tJ88IIJJ8cYwWWE55U_b9dL4eQUVlZtw'
);

export type Message = {
  id: string;
  content: string;
  timestamp: number;
  role: 'user' | 'assistant';
  status: 'sending' | 'sent' | 'error';
  reaction?: string;
};

interface ChatState {
  messages: Message[];
  sessions: { id: string; title: string; created_at?: string }[];
  currentSession: string | null;
  isProcessing: boolean;
  dynamicIslandState: 'default' | 'typing' | 'uploading' | 'alert';
  addMessage: (message: Message) => Promise<void>;
  clearMessages: () => void;
  setProcessingStatus: (isProcessing: boolean) => void;
  updateDynamicIsland: (state: 'default' | 'typing' | 'uploading' | 'alert') => void;
  loadSessions: () => Promise<void>;
  createSession: () => Promise<string>;
  subscribeToSession: (sessionId: string) => void;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      messages: [],
      sessions: [],
      currentSession: null,
      isProcessing: false,
      dynamicIslandState: 'default',
      
      addMessage: async (message) => {
        // Local optimistic update
        set((state) => ({ messages: [...state.messages, message] }));
        
        // Sync with Supabase
        if (get().currentSession) {
          const { error } = await supabase
            .from('messages')
            .insert([{
              session_id: get().currentSession,
              message: {
                type: message.role === 'user' ? 'human' : 'ai',
                content: message.content
              }
            }]);

          if (error) {
            console.error('Message save error:', error);
            set((state) => ({
              messages: state.messages.map(m =>
                m.id === message.id ? {...m, status: 'error'} : m
              )
            }));
          }
        }
      },

      clearMessages: () => set({ messages: [] }),
      
      setProcessingStatus: (isProcessing) => set({ isProcessing }),
      
      updateDynamicIsland: (state) => set({ dynamicIslandState: state }),
      
      loadSessions: async () => {
        const { data, error } = await supabase
          .from('messages')
          .select('session_id, created_at, message')
          .order('created_at', { ascending: false }) as {
            data: Array<{
              session_id: string;
              created_at: string;
              message: { content?: string }
            }>;
            error: any
          };

        if (!error) {
          const sessionsMap = new Map();
          data.forEach(({ session_id, created_at, message }) => {
            if (!sessionsMap.has(session_id)) {
              sessionsMap.set(session_id, {
                id: session_id,
                title: message.content?.substring(0, 100) || 'New Chat',
                created_at
              });
            }
          });
          set({ sessions: Array.from(sessionsMap.values()) });
        }
      },
      
      createSession: async () => {
        const newSessionId = uuidv4();
        set({ currentSession: newSessionId, messages: [] });
        return newSessionId;
      },
      
      subscribeToSession: (sessionId) => {
        return supabase
          .channel('messages')
          .on('postgres_changes', {
            event: 'INSERT',
            schema: 'public',
            table: 'messages',
            filter: `session_id=eq.${sessionId}`
          }, (payload) => {
            const newMessage: Message = {
              id: payload.new.id,
              content: payload.new.message.content,
              timestamp: Date.now(),
              role: (payload.new.message.type === 'human' ? 'user' : 'assistant') as 'user' | 'assistant',
              status: 'sent',
              session_id: sessionId
            };
            set((state) => ({ messages: [...state.messages, newMessage] }));
          })
          .subscribe();
      }
    }),
    {
      name: 'chat-storage',
      partialize: (state) => ({
        messages: state.messages,
        currentSession: state.currentSession
      }),
    }
  )
);