'use client'
import { usePortfolio } from '@/hooks/usePortfolio'

export function PortfolioBar() {
  const { portfolio, isLoading } = usePortfolio()

  const fmt = (n?: number) => n != null ? '$' + n.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }) : '—'

  return (
    <div className="flex gap-6 px-4 py-2 border-b text-xs font-mono
                    text-muted-foreground bg-background">
      <span>PORTFOLIO: <strong className="text-foreground">
        {isLoading ? '...' : fmt(portfolio?.portfolio_value)}
      </strong></span>
      <span>EXPOSURE: <strong className="text-foreground">
        {isLoading ? '...' : fmt(portfolio?.current_exposure)}
      </strong></span>
      <span>AVAILABLE: <strong className="text-green-600">
        {isLoading ? '...' : fmt(portfolio?.available)}
      </strong></span>
    </div>
  )
}
