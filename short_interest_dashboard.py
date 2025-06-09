import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(page_title="Top Short Interest Stocks", layout="wide")
st.title("Top US Short Interest Stocks")

@st.cache_data(show_spinner=False)
def get_high_short_interest_tickers():
    try:
        url = "https://www.highshortinterest.com/"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")

        table = soup.find("table")
        rows = table.find_all("tr")[1:]  # skip header

        tickers = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) > 1:
                ticker = cols[1].text.strip()
                tickers.append(ticker)

        if tickers:
            st.success(f"✅ Loaded {len(tickers)} tickers from HighShortInterest.com")
            return tickers
        else:
            raise Exception("No tickers found in parsed table.")
    except Exception as e:
        st.warning("⚠️ Using fallback static ticker list. Reason: " + str(e))
        return [
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
                "Price": f"${price:,.2f}" if price else None,
                "Short Ratio": round(short_ratio, 2) if short_ratio else None,
                "% of Float Shorted": round(short_percent_float * 100, 2) if short_percent_float else None,
                "Float Shares": f"{float_shares:,}" if float_shares else None,
                "Market Cap": f"${market_cap:,}" if market_cap else None
            })
        except:
            pass

    df = pd.DataFrame(data)
    df = df.dropna(subset=["% of Float Shorted"])
    df = df.sort_values("% of Float Shorted", ascending=False)
    return df

# Use dynamic ticker list
tickers = get_high_short_interest_tickers()

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
            "Price": f"${info.get('currentPrice'):,.2f}" if info.get("currentPrice") else None,
            "Short Ratio": round(info.get("shortRatio"), 2) if info.get("shortRatio") else None,
            "% of Float Shorted": round(info.get("shortPercentOfFloat") * 100, 2) if info.get("shortPercentOfFloat") else None,
            "Float Shares": f"{info.get('floatShares'):,}" if info.get("floatShares") else None,
            "Market Cap": f"${info.get('marketCap'):,}" if info.get("marketCap") else None
        })
    except:
        st.warning("Could not retrieve data for this ticker.")
