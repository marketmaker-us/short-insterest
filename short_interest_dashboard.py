import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Top Short Interest Stocks", layout="wide")
st.title("Top US Short Interest Stocks")

@st.cache_data(show_spinner=False)
def get_marketwatch_tickers():
    url = "https://www.marketwatch.com/tools/screener/short-interest"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    table = soup.find("table", class_="table table--overflow align--center")
    tickers = []
    if table:
        rows = table.find_all("tr")
        for row in rows[1:]:  # skip header
            cols = row.find_all("td")
            if len(cols) > 1:
                ticker = cols[0].text.strip().upper()
                # filter for real ticker patterns (A-Z, 1–5 chars)
                if ticker.isalpha() and 1 <= len(ticker) <= 5:
                    tickers.append(ticker)
        st.success(f"✅ Loaded {len(tickers)} tickers from MarketWatch Screener")
    else:
        st.warning("⚠️ Could not locate MarketWatch short-interest table — falling back to static list")
        tickers = get_static_tickers()
    return tickers

def get_static_tickers():
    return ["TSLA","AMC","GME","AAPL","NVDA","BBBY","PLTR","BABA",
            "LCID","RIVN","CVNA","NKLA","BYND","SPCE","AI","ROKU",
            "COIN","DKNG","FUBO","SOUN","TTOO","UPST","WISH","MARA","RIOT"]

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
                    "Price": f"${info.get('currentPrice',0):,.2f}",
                    "Short Ratio": round(info.get("shortRatio",0),2),
                    "% Float Shorted": round(spf*100,2),
                    "Float Shares": f"{info.get('floatShares',0):,}",
                    "Market Cap": f"${info.get('marketCap',0):,}"
                })
        except Exception:
            continue
    return pd.DataFrame(rows)

# Main flow
tickers = get_marketwatch_tickers()
data = get_yahoo_data(tickers)

if data.empty:
    st.warning("⚠️ No valid data from Yahoo Finance for these tickers.")
else:
    st.subheader("Top 25 Stocks by % Float Shorted")
    st.dataframe(data.head(25), use_container_width=True)
    st.download_button("Download CSV", data.to_csv(index=False), "short_interest.csv", "text/csv")

# Lookup tool
st.subheader("Lookup a Specific Ticker")
ticker_input = st.text_input("Enter ticker:").upper()
if ticker_input:
    try:
        info = yf.Ticker(ticker_input).info
        st.write({
            "Price": f"${info.get('currentPrice',0):,.2f}",
            "Short Ratio": round(info.get("shortRatio",0),2),
            "% Float Shorted": round(info.get("shortPercentOfFloat",0)*100,2),
            "Float Shares": f"{info.get('floatShares',0):,}",
            "Market Cap": f"${info.get('marketCap',0):,}"
        })
    except Exception as e:
        st.error(f"Failed lookup: {e}")
