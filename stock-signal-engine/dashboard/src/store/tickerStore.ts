import { create } from 'zustand'

interface TickerStore {
  ticker: string | null
  setTicker: (t: string) => void
}

export const useTickerStore = create<TickerStore>((set) => ({
  ticker: null,
  setTicker: (t) => set({ ticker: t.toUpperCase().trim() }),
}))
