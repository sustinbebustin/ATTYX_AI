import { create } from 'zustand';
import { persist } from 'zustand/middleware';

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
  isProcessing: boolean;
  dynamicIslandState: 'default' | 'typing' | 'uploading' | 'alert';
  addMessage: (message: Message) => void;
  clearMessages: () => void;
  setProcessingStatus: (isProcessing: boolean) => void;
  updateDynamicIsland: (state: 'default' | 'typing' | 'uploading' | 'alert') => void;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      messages: [],
      isProcessing: false,
      dynamicIslandState: 'default',
      addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
      clearMessages: () => set({ messages: [] }),
      setProcessingStatus: (isProcessing) => set({ isProcessing }),
      updateDynamicIsland: (state) => set({ dynamicIslandState: state }),
    }),
    {
      name: 'chat-storage',
      partialize: (state) => ({
        messages: state.messages,
      }),
    }
  )
);