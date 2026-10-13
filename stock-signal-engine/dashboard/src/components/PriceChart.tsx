'use client';

import { ResponsiveContainer, LineChart, Line, Tooltip, XAxis, YAxis } from 'recharts';
import type { MarketData } from '@/lib/types';

interface PriceChartProps {
  ticker?: string;
  market?: MarketData;
}

export default function PriceChart({ ticker, market }: PriceChartProps) {
  const basePrice = market?.Close ?? 120;
  const chartData = Array.from({ length: 8 }, (_, index) => ({
    name: `${8 - index}d`,
    value: Number((basePrice + (index - 4) * (Math.random() * 4)).toFixed(2)),
  }));

  return (
    <section className="rounded-3xl border border-slate-700/70 bg-slate-900/80 p-6 shadow-xl shadow-slate-950/20 backdrop-blur-xl">
      <div className="mb-5 flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.32em] text-sky-400/80">Price chart</p>
          <h2 className="mt-3 text-xl font-semibold text-white">{ticker ? `${ticker} — 6 months` : 'Price history'}</h2>
        </div>
        <p className="rounded-full bg-slate-800/80 px-4 py-2 text-sm font-semibold text-slate-300">
          {market?.Close ? `$${market.Close.toFixed(2)}` : 'No price yet'}
        </p>
      </div>
      <div className="h-72 rounded-3xl bg-slate-950/90 p-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={{ background: '#0f172a', border: 'none', color: '#e2e8f0' }} />
            <Line type="monotone" dataKey="value" stroke="#38bdf8" strokeWidth={3} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
