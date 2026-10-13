'use client';

import type { Article } from '@/lib/types';

interface ArticlesFeedProps {
  articles?: Article[];
  loading?: boolean;
}

export default function ArticlesFeed({ articles, loading }: ArticlesFeedProps) {
  return (
    <section className="rounded-3xl border border-slate-700/70 bg-slate-900/80 p-6 shadow-xl shadow-slate-950/20 backdrop-blur-xl">
      <div className="mb-5 flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.32em] text-sky-400/80">News sentiment</p>
          <h2 className="mt-3 text-xl font-semibold text-white">Live articles</h2>
        </div>
        <span className="rounded-full bg-slate-800/80 px-4 py-2 text-sm font-semibold text-slate-300">{articles?.length ?? 0} items</span>
      </div>

      <div className="space-y-4">
        {loading ? (
          <div className="rounded-3xl bg-slate-950/80 p-4 text-sm text-slate-500">Loading latest sentiment articles…</div>
        ) : articles?.length ? (
          articles.slice(0, 5).map((article) => (
            <article key={`${article.source}-${article.publishing_at}-${article.title}`} className="rounded-3xl bg-slate-950/80 p-4 transition hover:border-slate-600/80 hover:bg-slate-900/90">
              <div className="flex items-center justify-between gap-3 text-xs uppercase tracking-[0.24em] text-slate-500">
                <span>{article.source}</span>
                <span className="rounded-full bg-slate-800/90 px-2 py-1 text-[11px] font-semibold text-slate-300">{article.sentiment}</span>
              </div>
              <h3 className="mt-3 text-sm font-semibold text-white line-clamp-2">{article.title}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-400 line-clamp-2">{article.body}</p>
            </article>
          ))
        ) : (
          <div className="rounded-3xl bg-slate-950/80 p-4 text-sm text-slate-300">No sentiment articles available for this ticker.</div>
        )}
      </div>
    </section>
  );
}
