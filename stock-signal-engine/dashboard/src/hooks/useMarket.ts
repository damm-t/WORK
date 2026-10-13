'use client'
import useSWR from 'swr'
import { api } from '@/lib/api'
import type { MarketFeatures } from '@/lib/types'

export function useMarket(ticker: string | null) {
  const { data, error, isLoading } = useSWR<MarketFeatures>(
    ticker ? `market-${ticker}` : null,
    () => api.market(ticker!),
    { refreshInterval: 60000, shouldRetryOnError: false }
  )
  return { market: data, error, isLoading }
}
