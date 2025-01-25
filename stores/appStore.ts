import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type AppView = 'tasks' | 'pipeline' | 'reporting' | null;

interface AppState {
  activeApp: AppView;
  taskInput: string;
  chatWidth: number;
  isChatOpen: boolean;
}

interface AppActions {
  setActiveApp: (app: AppView) => void;
  setTaskInput: (input: string) => void;
  setChatWidth: (width: number) => void;
  toggleChat: () => void;
}

type AppStore = AppState & AppActions;

export const useAppStore = create<AppStore>()(
  persist(
    (set) => ({
      // Initial state
      activeApp: null,
      taskInput: '',
      chatWidth: 440,
      isChatOpen: true,

      // Actions
      setActiveApp: (app: AppView) => set({ activeApp: app }),
      setTaskInput: (input: string) => set({ taskInput: input }),
      setChatWidth: (width: number) => set({ chatWidth: width }),
      toggleChat: () => set((state: AppState) => ({ isChatOpen: !state.isChatOpen })),
    }),
    {
      name: 'app-storage',
      partialize: (state: AppStore) => ({
        taskInput: state.taskInput,
        chatWidth: state.chatWidth,
      }),
    }
  )
);