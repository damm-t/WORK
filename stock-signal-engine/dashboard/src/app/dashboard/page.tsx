import { TickerSearch }    from '@/components/TickerSearch'
import { SignalCard }       from '@/components/SignalCard'
import { IndicatorPanel }  from '@/components/IndicatorPanel'
import { SentimentFeed }   from '@/components/SentimentFeed'
import { PortfolioBar }    from '@/components/PortfolioBar'

export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <PortfolioBar />
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-lg font-mono font-semibold mb-1">
            SIGNAL ENGINE
          </h1>
          <p className="text-xs text-muted-foreground font-mono">
            news sentiment + technical indicators → trading signals
          </p>
        </div>
        <TickerSearch />
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="lg:col-span-2">
            <SignalCard />
          </div>
          <IndicatorPanel />
          <SentimentFeed />
        </div>
      </div>
    </main>
  )
}
                <p className="mt-2 text-sm text-rose-400">Error: {signalError ?? marketError ?? sentimentError}</p>
              )}
            </div>
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-[1.3fr_0.7fr]">
          <div className="space-y-6">
            <SignalCard ticker={ticker} signal={signal?.signal} decision={signal?.decision} loading={signalLoading} />
            <IndicatorPanel market={market} />
            <PriceChart market={market} ticker={ticker} />
          </div>

          <div className="space-y-6">
            <RiskPanel ticker={ticker} signal={signal?.signal} decision={signal?.decision} market={market} loading={loading} />
            <SentimentHeatmap articles={articles} />
            <ArticlesFeed articles={articles} loading={sentimentLoading} />
          </div>
        </div>
      </div>
    </main>
  );
}
