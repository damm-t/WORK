'use client'
import { useTickerStore } from '@/store/tickerStore'
import { useSentiment } from '@/hooks/useSentiment'

const sentColor = (s?: string) => {
  if (s === 'positive') return 'text-green-600 dark:text-green-400'
  if (s === 'negative') return 'text-red-600 dark:text-red-400'
  return 'text-muted-foreground'
}

export function SentimentFeed() {
  const ticker   = useTickerStore(s => s.ticker)
  const { articles, isLoading } = useSentiment(ticker)

  return (
    <div className="rounded-lg border p-4">
      <p className="text-xs font-mono text-muted-foreground mb-3">
        SENTIMENT FEED
      </p>
      {isLoading && (
        <div className="text-xs font-mono text-muted-foreground animate-pulse">
          FETCHING ARTICLES...
        </div>
      )}
      {!isLoading && articles.length === 0 && (
        <div className="text-xs font-mono text-muted-foreground">
          NO ARTICLES — RUN A TICKER
        </div>
      )}
      <div className="space-y-3">
        {articles.slice(0, 6).map((a, i) => (
          <div key={i}
               className="flex gap-3 text-xs border-b border-border
                          pb-2 last:border-0">
            <span className="text-muted-foreground min-w-[64px] font-mono">
              {a.source.replace('_', ' ').toUpperCase().slice(0, 8)}
            </span>
            <span className="flex-1 leading-relaxed">
              {a.title?.slice(0, 80)}{(a.title?.length ?? 0) > 80 ? '…' : ''}
            </span>
            <span className={`font-mono font-medium min-w-[36px]
                             text-right ${sentColor(a.sentiment)}`}>
              {a.sentiment_score?.toFixed(2) ?? '—'}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
