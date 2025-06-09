import streamlit as st
import yfinance as yf
import pandas as pd
from yfscreen import Screen

st.set_page_config(page_title="Top Short Interest Stocks", layout="wide")
st.title("Top US Short Interest Stocks")

@st.cache_data(show_spinner=False)
def get_yahoo_most_shorted_tickers(limit=50):
    screen = Screen()
    df = screen.get_screener(category="most_shorted_stocks", count=limit)
    tickers = df["symbol"].tolist()
    st.success(f"✅ Loaded {len(tickers)} tickers from Yahoo Finance Screener")
    return tickers

@st.cache_data(show_spinner=False)
def get_short_interest_data(tickers):
    rows = []
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            spf = info.get("shortPercentOfFloat")
            if spf is not None:
                rows.append({
                    "Ticker": ticker,
                    "Price": f"${info.get('currentPrice', 0):,.2f}",
                    "Short Ratio": round(info.get("shortRatio", 0), 2),
                    "% of Float Shorted": round(spf * 100, 2),
                    "Float Shares": f"{info.get('floatShares', 0):,}",
                    "Market Cap": f"${info.get('marketCap', 0):,}"
                })
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
    return pd.DataFrame(rows)

# Step 1: Load tickers from Yahoo screener
tickers = get_yahoo_most_shorted_tickers()

# Step 2: Fetch Yahoo Finance data
data = get_short_interest_data(tickers)

# Step 3: Display
if data.empty:
    st.warning("⚠️ No valid short interest data found.")
else:
    st.subheader("Top 25 Stocks by % of Float Shorted")
    st.dataframe(data.head(25), use_container_width=True)
    st.download_button("Download CSV", data.to_csv(index=False), "short_interest.csv", "text/csv")

# Step 4: Lookup tool
st.subheader("Lookup a Specific Ticker")
ticker_input = st.text_input("Enter ticker:").upper()
if ticker_input:
    try:
        info = yf.Ticker(ticker_input).info
        st.write({
            "Price": f"${info.get('currentPrice', 0):,.2f}",
            "Short Ratio": round(info.get("shortRatio", 0), 2),
            "% of Float Shorted": round(info.get("shortPercentOfFloat", 0) * 100, 2),
            "Float Shares": f"{info.get('floatShares', 0):,}",
            "Market Cap": f"${info.get('marketCap', 0):,}"
        })
    except Exception as e:
        st.error(f"Failed to retrieve data: {e}")
