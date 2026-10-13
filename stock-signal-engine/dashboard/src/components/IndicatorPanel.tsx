'use client'
import { useTickerStore } from '@/store/tickerStore'
import { useMarket } from '@/hooks/useMarket'

export function IndicatorPanel() {
  const ticker = useTickerStore(s => s.ticker)
  const { market, isLoading } = useMarket(ticker)

  const rows = [
    { label: 'RSI (14)',    value: market?.RSI_14?.toFixed(1) },
    { label: 'MACD',        value: market?.MACDh_12_26_9?.toFixed(3) },
    { label: 'BB Upper',    value: market?.['BBU_20_2.0'] ? '$' + market['BBU_20_2.0'].toFixed(2) : null },
    { label: 'BB Lower',    value: market?.['BBL_20_2.0'] ? '$' + market['BBL_20_2.0'].toFixed(2) : null },
    { label: 'ATR (14)',    value: market?.ATRr_14?.toFixed(2) },
    { label: 'Close',       value: market?.Close ? '$' + market.Close.toFixed(2) : null },
  ]

  return (
    <div className="rounded-lg border p-4">
      <p className="text-xs font-mono text-muted-foreground mb-3">
        TECHNICAL INDICATORS
      </p>
      {isLoading ? (
        <div className="text-xs font-mono text-muted-foreground animate-pulse">
          LOADING...
        </div>
      ) : (
        <div className="space-y-2">
          {rows.map(r => (
            <div key={r.label}
                 className="flex justify-between text-sm font-mono
                            border-b border-border pb-1 last:border-0">
              <span className="text-muted-foreground">{r.label}</span>
              <span className="font-medium">{r.value ?? '—'}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
