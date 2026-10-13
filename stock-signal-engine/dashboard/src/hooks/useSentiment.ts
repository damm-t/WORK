'use client'
import useSWR from 'swr'
import { api } from '@/lib/api'
import type { Article } from '@/lib/types'

export function useSentiment(ticker: string | null) {
  const { data, error, isLoading } = useSWR<Article[]>(
    ticker ? `sentiment-${ticker}` : null,
    () => api.sentiment(ticker!),
    { refreshInterval: 60000, shouldRetryOnError: false }
  )
  return { articles: data ?? [], error, isLoading }
}
