'use client'
import { useState } from 'react'
import { useTickerStore } from '@/store/tickerStore'

export function TickerSearch() {
  const [input, setInput] = useState('')
  const setTicker = useTickerStore(s => s.setTicker)

  const handleSubmit = () => {
    const t = input.trim().toUpperCase()
    if (!t || t.length > 5) return
    setTicker(t)
    setInput('')
  }

  return (
    <div className="flex gap-2 mb-6">
      <input
        value={input}
        onChange={e => setInput(e.target.value.toUpperCase())}
        onKeyDown={e => e.key === 'Enter' && handleSubmit()}
        placeholder="Enter ticker — AAPL, TSLA, NVDA..."
        maxLength={5}
        className="flex-1 px-4 py-2 text-sm font-mono
                   bg-background border border-border rounded-md
                   focus:outline-none focus:ring-1 focus:ring-ring"
      />
      <button
        onClick={handleSubmit}
        className="px-6 py-2 text-sm font-mono font-medium
                   bg-primary text-primary-foreground
                   rounded-md hover:opacity-90 transition-opacity"
      >
        RUN ↗
      </button>
    </div>
  )
}
