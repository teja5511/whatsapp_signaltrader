import { create } from "zustand";

export type ThemeMode = "system" | "dark" | "light";

interface UiState {
  sidebarOpen: boolean;
  theme: ThemeMode;
  mockMode: boolean;
  activeConfirmModal: {
    type: "ENABLE_DEMO" | "EMERGENCY_STOP" | "RESET_EMERGENCY_STOP" | "CLOSE_ALL_DEMO" | "RESET_WHATSAPP" | null;
    title?: string;
    description?: string;
    phrase?: string;
    action?: () => Promise<void>;
  };
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
  setTheme: (theme: ThemeMode) => void;
  setMockMode: (mock: boolean) => void;
  openConfirmModal: (modal: UiState["activeConfirmModal"]) => void;
  closeConfirmModal: () => void;
}

export const useUiStore = create<UiState>((set) => ({
  sidebarOpen: true,
  theme: "system",
  mockMode: Boolean(import.meta.env.VITE_DESKTOP_MOCK_MODE === "true"),
  activeConfirmModal: { type: null },
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setTheme: (theme) => set({ theme }),
  setMockMode: (mockMode) => set({ mockMode }),
  openConfirmModal: (activeConfirmModal) => set({ activeConfirmModal }),
  closeConfirmModal: () => set({ activeConfirmModal: { type: null } }),
}));
