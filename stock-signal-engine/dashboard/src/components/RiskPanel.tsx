'use client';

import type { MarketData, Signal } from '@/lib/types';

interface RiskPanelProps {
  ticker?: string;
  signal?: Signal['signal'];
  decision?: Signal['decision'];
  market?: MarketData;
  loading?: boolean;
}

const formatValue = (value?: number | string) => (value === undefined || value === null ? '—' : value);

export default function RiskPanel({ ticker, signal, decision, market, loading }: RiskPanelProps) {
  const riskLevel = signal?.action === 'BUY' ? 'Moderate' : signal?.action === 'SELL' ? 'High' : 'Low';
  const currentPrice = market?.Close ? `$${market.Close.toFixed(2)}` : '—';

  return (
    <section className="rounded-3xl border border-slate-700/70 bg-slate-900/80 p-6 shadow-xl shadow-slate-950/20 backdrop-blur-xl">
      <div className="mb-5 flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.32em] text-sky-400/80">Risk & sizing</p>
          <h2 className="mt-3 text-xl font-semibold text-white">Position risk</h2>
        </div>
        <span className="rounded-full bg-slate-800/80 px-4 py-2 text-sm font-semibold text-slate-300">{riskLevel}</span>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-3xl bg-slate-950/80 p-4 text-sm text-slate-300">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Current price</p>
          <p className="mt-2 text-xl font-semibold text-white">{currentPrice}</p>
        </div>
        <div className="rounded-3xl bg-slate-950/80 p-4 text-sm text-slate-300">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Position size</p>
          <p className="mt-2 text-xl font-semibold text-white">{formatValue(decision?.shares ?? '—')}</p>
        </div>
        <div className="rounded-3xl bg-slate-950/80 p-4 text-sm text-slate-300">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Stop loss</p>
          <p className="mt-2 text-xl font-semibold text-white">{decision?.stop_loss_price ? `$${decision.stop_loss_price.toFixed(2)}` : '—'}</p>
        </div>
        <div className="rounded-3xl bg-slate-950/80 p-4 text-sm text-slate-300">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Approval</p>
          <p className="mt-2 text-xl font-semibold text-white">{decision?.approved ? 'Approved' : 'Pending'}</p>
        </div>
      </div>

      <div className="mt-6 rounded-3xl bg-slate-950/80 p-4 text-sm text-slate-300">
        <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Ticker</p>
        <p className="mt-2 text-lg font-semibold text-white">{ticker ?? '—'}</p>
        {loading && <p className="mt-2 text-sm text-slate-400">Refreshing risk updates…</p>}
      </div>
    </section>
  );
}
