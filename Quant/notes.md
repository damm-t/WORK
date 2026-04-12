so here we go with the core concept of quant at first

" Core " 

1. Mean = (x1 + x2 + x3 + .. + xN) / N
    * so this will lead to a few of the conceptual 
        &* so as an example, something that is normally stay on one rate sudden fallen 5% but u knw that it could be coming up but just need some times.
        - Mean revision 
        - Z-Score signals 
        - Bollinger-type logic 

2. Change(Returns) = [ Price(Today) - Price(yestd) ] / Price(yestd)

    * this will leading to some idea power
        - Momentum strategies 
        - Trend-Following
        - Breakout Strategies

3. Spread / differences = Spread = Price(A) - Price(B)
    * mostly used in Paris Trading / Arbitrage / Market making
        &* the main concept is like this 
            - when it is becoming wide -> trend to close 
            - when it become narrow -> trade to profit 

    * it should be setting a interval range to prevent profit overflow

4. votality / variance = Average of (x / mean) ^ 2
    * this is telling us how much we entry, how big is the slot and how strong is the trend 


===> EXPENSION For Mean

so in mean, we do have a depeer relationship in between the sum of all values and the number of values

so in this relationship, condition : 0 < x < 1 and x > 1

* Mean revision -> prices up / down on the range 

* Mean shift -> the average price is moving ( trend reforming )

* Mean votality -> how far can the prices dances away from the mean 

normally used in quant 
-> Z-Scores - distance from mean in units of standard deviation 
-> Stationarity tests - checking if the mean is stable 
-> Rolling means -> moving average windows 
    {
        Moving Mean [MA] -> usually count in a window to take the average in the window, and slide it day by day.
            ( used for)
                - trend detection 
                - price smoothing 
                - breakout signals
    }
-> Mean revision pairs trading 
-> moving average crossovers

===========================================================================
Kalman Filters, ARIMA, LSTMs

These are advanced ways to:
 - estimate dynamic means
 - adapt to real-time changes
 - predict future means
 - smooth noise
 - capture underlying hidden patterns

Kalman Filter is loved in:
 - pairs trading
 - forecasting trend levels
 - dynamic hedge ratios
 - predicting fair value of assets

LSTM is used when:
 - the structure is nonlinear
 - long-term dependencies matter
 - more adapting filtering 

===========================================================================

 Moving Mean [MA] -> usually count in a window to take the average in the window, and slide it day by day.
        ( used for
            - trend detection 
            - price smoothing 
            - breakout signals
        )

 Exponential Moving Mean ( EMA ) -> weight recent prices more
    Perspective ( viewing )
        => when the market want to reach some things which is a target, they will move and adjust faster, and this is the rate of that speed. 
        ( deciding on 
            - momentum 
            - trend-following 
            - high-frequency trading
        )
        
 Weighted Mean -> Giving different weights to different data points
    ( use in 
        - risk model 
        - factor weighting
        - combining signals 
    )

 Measure of returns 
    => notes :: Quant is never work in prices($), it is work with Percentage (%)

    as normally retruns is showing 
        - growth 
        - risk 
        - computing behaviour
            formulae : 
        
        R't​ = [P't−​P'(t-1)​] / P'(t-1)

        - daily mean return
        - weekly mean return
        - expected future return
 

=============================================================================
A. Mean Reversion Strategy
Buy when price is below its mean.
Sell when price is above its mean.
We quantify it with Z-score:

    Z = ( Price - Mean ) / SD, standard deviation 
 
If Z < −2 → buy
If Z > +2 → sell

B. Moving Average Crossover

Fast MA crosses above slow MA = buy
Fast crosses below slow = sell

Used in:
 - trend following
 - momentum trading

C. Pairs Trading (Stat Arb)
Two stocks have a “normal distance” between their prices (mean).

If distance > mean + threshold → short the high, long the low
If distance < mean − threshold → reverse

D. Volatility Mean Reversion
Volatility almost always returns to its mean.
Quant trades volatility like:

buy low vol
sell high vol

This is the engine behind many hedge fund strategies.


