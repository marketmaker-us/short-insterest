import streamlit as st
import yfinance as yf
import pandas as pd
from yfscreen import Screen
from datetime import datetime

st.set_page_config(page_title="Top Short Interest Stocks", layout="wide")
st.title("Top US Short Interest Stocks")

@st.cache_data(show_spinner=False)
def get_yahoo_most_shorted_tickers(limit=100):
    scr = Screen()
    df = scr.get_screener(
        category="most_shorted_stocks",
        count=limit
    )
    tickers = df["symbol"].tolist()
    st.success(f"✅ Loaded {len(tickers)} tickers from Yahoo Finance Screener")
    return tickers

@st.cache_data(show_spinner=False)
def get_short_interest_data(tickers):
    rows = []
    for ticker in tickers:
        info = yf.Ticker(ticker).info
        spf = info.get("shortPercentOfFloat")
        if spf is not None:
            rows.append({
                "Ticker": ticker,
                "Price": f"${info.get('currentPrice', 0):,.2f}",
                "Short Ratio": round(info.get("shortRatio", 0), 2),
                "% of Float Shorted": round(spf * 100, 2),
                "Float Shares": f"{info.get('floatShares'):,}",
                "Market Cap": f"${info.get('marketCap', 0):,}"
            })
    return pd.DataFrame(rows)

tickers = get_yahoo_most_shorted_tickers()
data = get_short_interest_data(tickers)

if data.empty:
    st.warning("⚠️ No valid short-interest data found.")
else:
    st.subheader("Top Shorted Stocks by % of Float")
    st.dataframe(data.head(25), use_container_width=True)
    st.download_button("Download CSV", data.to_csv(index=False), "shorted.csv", "text/csv")

# Ticker lookup
^[st.subheader("Lookup a Specific Ticker")]({"attribution":{"attributableIndex":"0-4"}})
^[ticker_input = st.text_input("Enter ticker:").upper()]({"attribution":{"attributableIndex":"0-5"}})
if ticker_input:
    ^[info = yf.Ticker(ticker_input).info]({"attribution":{"attributableIndex":"0-6"}})
    st.write({
        ^["Price": f"${info.get('currentPrice'):,.2f}",]({"attribution":{"attributableIndex":"0-7"}})
        ^["Short Ratio": round(info.get("shortRatio"), 2),]({"attribution":{"attributableIndex":"0-8"}})
        ^["% of Float Shorted": round(info.get("shortPercentOfFloat") * 100, 2),]({"attribution":{"attributableIndex":"0-9"}})
        ^["Float Shares": f"{info.get('floatShares'):,}",]({"attribution":{"attributableIndex":"0-10"}})
        ^["Market Cap": f"${info.get('marketCap'):,}"]({"attribution":{"attributableIndex":"0-11"}})
    })
