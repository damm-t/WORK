"use client";

import { create } from 'zustand';

type Signal = {
  action: 'BUY' | 'SELL' | 'HOLD' | string;
  confidence?: number;
  reason?: string;
};

type Article = {
  source: string;
  title: string;
  body?: string;
  sentiment?: string;
};

interface AppState {
  ticker?: string;
  setTicker: (t?: string) => void;

  signal?: Signal;
  setSignal: (s?: Signal) => void;

  market?: Record<string, any>;
  setMarket: (m?: Record<string, any>) => void;

  articles?: Article[];
  setArticles: (a?: Article[]) => void;

  connected: boolean;
  setConnected: (v: boolean) => void;
}

export const useAppStore = create<AppState>((set: any) => ({
  ticker: undefined,
  setTicker: (t?: string) => set({ ticker: t }),

  signal: undefined,
  setSignal: (s?: Signal) => set({ signal: s }),

  market: undefined,
  setMarket: (m?: Record<string, any>) => set({ market: m }),

  articles: undefined,
  setArticles: (a?: Article[]) => set({ articles: a }),

  connected: false,
  setConnected: (v: boolean) => set({ connected: v }),
}));

export default useAppStore;
