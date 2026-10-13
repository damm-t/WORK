'use client'
import { useTickerStore } from '@/store/tickerStore'
import { useSignal } from '@/hooks/useSignal'

export function SignalCard() {
  const ticker = useTickerStore(s => s.ticker)
  const { signal, isLoading, error } = useSignal(ticker)

  if (!ticker) return (
    <div className="rounded-lg border p-6 text-center text-sm
                    text-muted-foreground font-mono">
      ENTER A TICKER TO SEE SIGNAL
    </div>
  )

  if (isLoading) return (
    <div className="rounded-lg border p-6 text-center text-sm
                    text-muted-foreground font-mono animate-pulse">
      ANALYZING {ticker}...
    </div>
  )

  if (error) return (
    <div className="rounded-lg border border-destructive p-6
                    text-sm text-destructive font-mono">
      ERROR — {error.message}
    </div>
  )

  const action = signal?.signal?.action
  const conf   = signal?.signal?.confidence ?? 0
  const reason = signal?.signal?.reason ?? '—'
  const isBuy  = action === 'BUY'

  return (
    <div className={`rounded-lg border p-6 ${
      isBuy
        ? 'border-green-300 bg-green-50 dark:bg-green-950/20'
        : 'border-border bg-background'
    }`}>
      <p className="text-xs font-mono text-muted-foreground mb-3">
        SIGNAL DECISION — {ticker}
      </p>
      <div className="flex items-center justify-between mb-4">
        <span className={`text-3xl font-semibold font-mono ${
          isBuy ? 'text-green-700 dark:text-green-400' : 'text-muted-foreground'
        }`}>
          {action ?? '—'}
        </span>
        <span className="text-sm font-mono text-muted-foreground">
          {(conf * 100).toFixed(0)}% confidence
        </span>
      </div>
      <div className="h-1 w-full bg-muted rounded-full overflow-hidden">
        <div
          className="h-1 bg-green-500 rounded-full transition-all duration-500"
          style={{ width: `${(conf * 100).toFixed(0)}%` }}
        />
      </div>
      <p className="text-xs text-muted-foreground font-mono mt-3 leading-relaxed">
        {reason}
      </p>
    </div>
  )
}
