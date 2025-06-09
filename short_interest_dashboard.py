import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Top Short Interest Stocks – Benzinga", layout="wide")
st.title("Top US Shorted Stocks (Benzinga)")

@st.cache_data(show_spinner=False)
def get_benzinga_tickers():
    url = "https://www.benzinga.com/short-interest/most-shorted"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    ticker_rows = soup.select("table tr")
    tickers = []
    for row in ticker_rows:
        cols = row.find_all("td")
        if cols:
            ticker = cols[0].get_text(strip=True).upper()
            if ticker.isalpha() and 1 <= len(ticker) <= 5:
                tickers.append(ticker)
    if tickers:
        st.success(f"✅ Loaded {len(tickers)} tickers from Benzinga")
    else:
        st.warning("⚠️ No tickers found on Benzinga — falling back to static.")
        tickers = get_static_tickers()
    return tickers

def get_static_tickers():
    return ["TSLA", "AMC", "GME", "AAPL", "NVDA", "BBBY", "PLTR", "BABA"]

@st.cache_data(show_spinner=False)
def get_yahoo_data(tickers):
    rows = []
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            spf = info.get("shortPercentOfFloat")
            if spf is not None:
                rows.append({
                    "Ticker": t,
                    "Price": f"${info.get('currentPrice', 0):,.2f}",
                    "Short Ratio": round(info.get("shortRatio", 0), 2),
                    "% Float Shorted": round(spf * 100, 2),
                    "Float Shares": f"{info.get('floatShares', 0):,}",
                    "Market Cap": f"${info.get('marketCap', 0):,}"
                })
        except Exception:
            continue
    return pd.DataFrame(rows)

# Fetch tickers and data
tickers = get_benzinga_tickers()
data = get_yahoo_data(tickers)

# Show table
if data.empty:
    st.warning("⚠️ No valid short interest data found on Yahoo Finance.")
else:
    st.subheader("Top 25 by % Float Shorted")
    st.dataframe(data.head(25), use_container_width=True)
    st.download_button("📥 Download CSV", data.to_csv(index=False), "short_interest.csv", "text/csv")

# Lookup tool
st.subheader("Lookup a Specific Ticker")
ticker_input = st.text_input("Enter ticker:").upper()
if ticker_input:
    try:
        info = yf.Ticker(ticker_input).info
        st.write({
            "Price": f"${info.get('currentPrice', 0):,.2f}",
            "Short Ratio": round(info.get("shortRatio", 0), 2),
            "% Float Shorted": round(info.get("shortPercentOfFloat", 0) * 100, 2),
            "Float Shares": f"{info.get('floatShares', 0):,}",
            "Market Cap": f"${info.get('marketCap', 0):,}"
        })
    except Exception as e:
        st.error(f"Failed lookup: {e}")
