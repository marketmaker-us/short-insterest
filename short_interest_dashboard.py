import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Top Short Interest Stocks", layout="wide")
st.title("📊 US Stocks with Highest Short Interest")

# Define a static list of popular tickers (we'll improve this later)
tickers = [
    "TSLA", "AMC", "GME", "AAPL", "NVDA", "BBBY", "PLTR", "BABA",
    "LCID", "RIVN", "CVNA", "NKLA", "BYND", "SPCE", "AI", "ROKU", "COIN",
    "DKNG", "FUBO", "SOUN", "TTOO", "UPST", "WISH", "MARA", "RIOT"
]

@st.cache_data(show_spinner=False)
def get_short_interest_data(tickers):
    data = []
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            short_ratio = info.get("shortRatio")
            float_shares = info.get("floatShares")
            short_percent_float = info.get("shortPercentOfFloat")
            market_cap = info.get("marketCap")
            price = info.get("currentPrice")

            data.append({
                "Ticker": ticker,
                "Price": price,
                "Short Ratio": short_ratio,
                "% of Float Shorted": short_percent_float,
                "Float Shares": float_shares,
                "Market Cap": market_cap
            })
        except:
            pass

    df = pd.DataFrame(data)
    df = df.sort_values("% of Float Shorted", ascending=False)
    return df

# Fetch and display data
st.subheader("Top 25 Stocks by % of Float Shorted")
data = get_short_interest_data(tickers)
st.dataframe(data.head(25), use_container_width=True)

# Optional: Download CSV
download = st.download_button(
    label="Download Data as CSV",
    data=data.to_csv(index=False),
    file_name="short_interest_data.csv",
    mime="text/csv"
)

# Optional: Ticker detail viewer
st.subheader("Lookup a Specific Ticker")
ticker_input = st.text_input("Enter a ticker symbol (e.g., TSLA):").upper()
if ticker_input:
    try:
        info = yf.Ticker(ticker_input).info
        st.write({
            "Price": info.get("currentPrice"),
            "Short Ratio": info.get("shortRatio"),
            "% of Float Shorted": info.get("shortPercentOfFloat"),
            "Float Shares": info.get("floatShares"),
            "Market Cap": info.get("marketCap")
        })
    except:
        st.warning("Could not retrieve data for this ticker.")
