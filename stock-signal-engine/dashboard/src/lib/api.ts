import type { SignalResponse, MarketFeatures, Article, PortfolioResponse } from './types'

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    next: { revalidate: 0 }  // always fresh, no cache
  })
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`)
  return res.json()
}

export const api = {
  health:    ()              => get<{status:string}>('/health'),
  signal:    (ticker:string) => get<SignalResponse>(`/signal/${ticker.toUpperCase()}`),
  market:    (ticker:string) => get<MarketFeatures>(`/market/${ticker.toUpperCase()}`),
  sentiment: (ticker:string) => get<Article[]>(`/sentiment/${ticker.toUpperCase()}`),
  portfolio: ()              => get<PortfolioResponse>('/portfolio'),
}
