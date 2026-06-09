import { create } from "zustand";
import type { User } from "../types/domain";
import { authApi } from "../api/client";

interface AuthState {
  token: string | null;
  user: User | null;
  bootstrapped: boolean;
  setToken: (token: string | null) => void;
  setUser: (user: User | null) => void;
  bootstrap: () => Promise<void>;
  login: (username: string, password: string) => Promise<User>;
  logout: () => Promise<void>;
  clearSession: () => void;
}

const TOKEN_KEY = "medical_quiz_token";

export const useAuthStore = create<AuthState>((set, get) => ({
  token: localStorage.getItem(TOKEN_KEY),
  user: null,
  bootstrapped: false,
  setToken: (token) => {
    if (token) {
      localStorage.setItem(TOKEN_KEY, token);
    } else {
      localStorage.removeItem(TOKEN_KEY);
    }
    set({ token });
  },
  setUser: (user) => set({ user }),
  bootstrap: async () => {
    const token = get().token;
    if (!token) {
      set({ bootstrapped: true, user: null });
      return;
    }
    try {
      const user = await authApi.me();
      set({ user, bootstrapped: true });
    } catch {
      get().clearSession();
      set({ bootstrapped: true });
    }
  },
  login: async (username, password) => {
    const token = await authApi.login({ username, password });
    get().setToken(token.access_token);
    const user = await authApi.me();
    set({ user });
    return user;
  },
  logout: async () => {
    try {
      await authApi.logout();
    } finally {
      get().clearSession();
    }
  },
  clearSession: () => {
    localStorage.removeItem(TOKEN_KEY);
    set({ token: null, user: null });
  },
}));