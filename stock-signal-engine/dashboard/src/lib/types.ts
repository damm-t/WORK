export interface Article {
  source: string
  ticker: string
  title: string
  body: string
  published_at: string
  url: string
  sentiment?: string
  sentiment_score?: number
  entities?: string[]
}

export interface MarketFeatures {
  RSI_14: number
  MACDh_12_26_9: number
  'BBU_20_2.0': number
  'BBL_20_2.0': number
  ATRr_14: number
  Close: number
}

export interface SignalResult {
  action: 'BUY' | 'HOLD'
  confidence: number
  reason: string
}

export interface RiskDecision {
  approved: boolean
  shares: number
  position_value: number
  stop_loss_price: number
  reason: string
}

export interface SignalResponse {
  ticker: string
  signal: SignalResult
  decision: RiskDecision
}

export interface PortfolioResponse {
  portfolio_value: number
  current_exposure: number
  available: number
}
