'use client'
import useSWR from 'swr'
import { api } from '@/lib/api'
import type { PortfolioResponse } from '@/lib/types'

export function usePortfolio() {
  const { data, error, isLoading } = useSWR<PortfolioResponse>(
    'portfolio',
    api.portfolio,
    { refreshInterval: 15000, shouldRetryOnError: false }
  )
  return { portfolio: data, error, isLoading }
}
