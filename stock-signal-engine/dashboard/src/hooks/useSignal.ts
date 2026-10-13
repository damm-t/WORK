'use client'
import useSWR from 'swr'
import { api } from '@/lib/api'
import type { SignalResponse } from '@/lib/types'

export function useSignal(ticker: string | null) {
  const { data, error, isLoading } = useSWR<SignalResponse>(
    ticker ? `signal-${ticker}` : null,
    () => api.signal(ticker!),
    {
      refreshInterval: 30000,      // refresh every 30s
      revalidateOnFocus: true,
      shouldRetryOnError: false
    }
  )
  return { signal: data, error, isLoading }
}
