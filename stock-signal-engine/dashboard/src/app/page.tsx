import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-50">
      <div className="mx-auto flex min-h-screen max-w-6xl flex-col justify-center px-6 py-16 sm:px-10">
        <div className="grid gap-10 lg:grid-cols-[0.9fr_0.8fr] lg:items-center">
          <section className="space-y-6">
            <p className="text-sm uppercase tracking-[0.3em] text-sky-400/80">Stock Signal Engine</p>
            <h1 className="text-5xl font-semibold tracking-tight text-white sm:text-6xl">
              A modern SaaS dashboard for live trading signals, sentiment, and risk.
            </h1>
            <p className="max-w-2xl text-lg leading-8 text-slate-300">
              Build your next trading workflow with a Next.js app router, TypeScript, Tailwind CSS, SWR, real-time WebSocket streams, and user auth for subscription control.
            </p>
            <div className="flex flex-col gap-4 sm:flex-row">
              <Link
                href="/dashboard"
                className="inline-flex items-center justify-center rounded-3xl bg-sky-500 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-sky-400"
              >
                View dashboard
              </Link>
              <Link
                href="/auth/signin"
                className="inline-flex items-center justify-center rounded-3xl border border-slate-700 px-6 py-3 text-sm text-slate-100 transition hover:border-slate-500"
              >
                Sign in
              </Link>
            </div>
          </section>

          <section className="rounded-[2rem] border border-slate-800/80 bg-slate-900/80 p-8 shadow-2xl shadow-slate-950/40 backdrop-blur-xl">
            <p className="text-sm uppercase tracking-[0.24em] text-sky-400/80">Dashboard preview</p>
            <div className="mt-6 space-y-4 text-slate-300">
              <div className="rounded-3xl bg-slate-950/80 p-5">
                <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Signal</p>
                <p className="mt-2 text-xl font-semibold text-white">AAPL BUY</p>
              </div>
              <div className="rounded-3xl bg-slate-950/80 p-5">
                <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Sentiment</p>
                <p className="mt-2 text-xl font-semibold text-white">Positive news momentum</p>
              </div>
              <div className="rounded-3xl bg-slate-950/80 p-5">
                <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Risk</p>
                <p className="mt-2 text-xl font-semibold text-white">Stop loss active</p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
