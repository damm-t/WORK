'use client';

import type { Article } from '@/lib/types';

interface SentimentHeatmapProps {
  articles?: Article[];
}

const sources = ['NEWSAPI', 'YFINANCE', 'TWITTER', 'SEC EDGAR', 'OVERALL'];

export default function SentimentHeatmap({ articles }: SentimentHeatmapProps) {
  const sourceMap = sources.map((source) => {
    const count = articles?.filter((article) => article.source.toUpperCase().includes(source.split(' ')[0])).length ?? 0;
    return { source, value: count };
  });

  return (
    <section className="rounded-3xl border border-slate-700/70 bg-slate-900/80 p-6 shadow-xl shadow-slate-950/20 backdrop-blur-xl">
      <div className="mb-5">
        <p className="text-xs uppercase tracking-[0.32em] text-sky-400/80">Sentiment heatmap</p>
        <h2 className="mt-3 text-xl font-semibold text-white">Source sentiment</h2>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {sourceMap.map((item) => (
          <div key={item.source} className="rounded-3xl bg-slate-950/80 p-4 text-sm text-slate-300">
            <p className="text-xs uppercase tracking-[0.24em] text-slate-500">{item.source}</p>
            <p className="mt-3 text-2xl font-semibold text-white">{item.value || '—'}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
