import Link from 'next/link';

export default function SignInPage() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-50">
      <div className="mx-auto flex min-h-screen max-w-xl flex-col items-center justify-center px-6 py-16 text-center">
        <div className="rounded-[2rem] border border-slate-800/80 bg-slate-900/80 p-10 shadow-2xl shadow-slate-950/40">
          <p className="text-sm uppercase tracking-[0.3em] text-sky-400/80">Sign in</p>
          <h1 className="mt-5 text-4xl font-semibold text-white">Access your trading dashboard</h1>
          <p className="mt-4 text-sm leading-7 text-slate-300">
            Use Google sign-in to unlock the SaaS analytics dashboard and live signal stream.
          </p>
          <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:justify-center">
            <a
              href="/api/auth/signin/google"
              className="inline-flex items-center justify-center rounded-3xl bg-sky-500 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-sky-400"
            >
              Sign in with Google
            </a>
            <Link
              href="/"
              className="inline-flex items-center justify-center rounded-3xl border border-slate-700 px-6 py-3 text-sm text-slate-100 transition hover:border-slate-500"
            >
              Back home
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
