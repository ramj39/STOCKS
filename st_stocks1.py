import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import yfinance as yf
import datetime

# Sidebar disclaimer
st.sidebar.markdown("""
---
**DISCLAIMER**  
This application is for educational and informational purposes only.  
It uses public stock market data and simple technical indicators (EMA crossover, regression trend lines).  
The AI-style recommendations (BUY/SELL/HOLD) are simulated signals and should not be considered financial advice.  
Always do your own research or consult a licensed financial advisor before making investment decisions.
""")

st.write("***developed by Subramanian Ramajayam with Copilot support***")
st.header("📈 Stock Portfolio")

# Dropdown with common tickers
default_tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "NFLX"]
selected_ticker = st.selectbox("Choose a stock ticker", default_tickers)

# Optional manual entry
manual_ticker = st.text_input("Or enter another ticker")

# Final ticker choice
ticker = manual_ticker if manual_ticker else selected_ticker

# User inputs for EMA spans
short_span = st.number_input("Short EMA span (days)", min_value=5, max_value=50, value=12, step=1)
long_span = st.number_input("Long EMA span (days)", min_value=10, max_value=200, value=26, step=1)

# Date range selector
start_date = st.date_input("Start date", datetime.date.today() - datetime.timedelta(days=90))
end_date = st.date_input("End date", datetime.date.today())

if st.button("Show Stock Chart"):
    if ticker:
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date).dropna(subset=["Close"])

        if hist.empty:
            st.error("⚠️ No data available for this ticker and date range.")
        else:
            # Calculate user-defined EMAs
            hist["ShortEMA"] = hist["Close"].ewm(span=short_span, adjust=False).mean()
            hist["LongEMA"] = hist["Close"].ewm(span=long_span, adjust=False).mean()

            # Chart with Close + ShortEMA + LongEMA
            df = hist.reset_index()
            base = alt.Chart(df).encode(x="Date")
            close_line = base.mark_line(color="blue").encode(y="Close")
            short_line = base.mark_line(color="green").encode(y="ShortEMA")
            long_line = base.mark_line(color="red").encode(y="LongEMA")

            chart = (close_line + short_line + long_line).interactive()
            st.altair_chart(chart, use_container_width=True)

            # Current price
            price = hist["Close"].iloc[-1]
            st.write(f"Current price of {ticker}: {price:.2f}")

            # --- AI-style Recommendation based on crossover ---
            latest_short = hist["ShortEMA"].iloc[-1]
            latest_long = hist["LongEMA"].iloc[-1]

            if latest_short > latest_long:
                st.success(f"AI Recommendation: BUY (short EMA {short_span} > long EMA {long_span})")
            elif latest_short < latest_long:
                st.error(f"AI Recommendation: SELL (short EMA {short_span} < long EMA {long_span})")
            else:
                st.info("***AI Recommendation:*** HOLD (lines converging)")
