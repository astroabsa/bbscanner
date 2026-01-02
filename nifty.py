import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import pytz
from datetime import datetime
import time

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="Absa's Live F&O Screener Pro", layout="wide")

# --- 2. GLOBAL SYMBOL LIST ---
FNO_SYMBOLS = [
    'ABFRL.NS', 'ADANIENSOL.NS', 'ADANIENT.NS', 'ADANIGREEN.NS', 'ADANIPORTS.NS', 'ALKEM.NS', 
    'AUROPHARMA.NS', 'AXISBANK.NS', 'BANDHANBNK.NS', 'BANKBARODA.NS', 'BANKINDIA.NS', 'BDL.NS', 
    'BEL.NS', 'BEML.NS', 'BHARTIARTL.NS', 'BHEL.NS', 'BIOCON.NS', 'BPCL.NS', 'BRITANNIA.NS', 
    'BSE.NS', 'CAMS.NS', 'CANBK.NS', 'CDSL.NS', 'CGPOWER.NS', 'CHAMBLFERT.NS', 'CHOLAFIN.NS', 
    'CIPLA.NS', 'COALINDIA.NS', 'COFORGE.NS', 'COLPAL.NS', 'CONCOR.NS', 'COROMANDEL.NS', 
    'CROMPTON.NS', 'CUMMINSIND.NS', 'CYIENT.NS', 'DABUR.NS', 'DALBHARAT.NS', 'DEEPAKNTR.NS', 
    'DELHIVERY.NS', 'DIVISLAB.NS', 'DIXON.NS', 'DMART.NS', 'DRREDDY.NS', 'FSL.NS', 'GAIL.NS', 
    'GLENMARK.NS', 'GMRINFRA.NS', 'GNFC.NS', 'GODREJCP.NS', 'GODREJPROP.NS', 'GRANULES.NS', 
    'GUJGASLTD.NS', 'HAL.NS', 'HAVELLS.NS', 'HCLTECH.NS', 'HDFCAMC.NS', 'HDFCBANK.NS', 'HDFCLIFE.NS', 
    'HEROMOTOCO.NS', 'HINDALCO.NS', 'HINDCOPPER.NS', 'HINDPETRO.NS', 'HINDUNILVR.NS', 'ICICIBANK.NS', 
    'ICICIGI.NS', 'IDFC.NS', 'IDFCFIRSTB.NS', 'IEX.NS', 'IGL.NS', 'INDHOTEL.NS', 'INDIACEM.NS', 'INDIAMART.NS', 
    'INDIGO.NS', 'INDUSINDBK.NS', 'INDUSTOWER.NS', 'INFY.NS', 'IOC.NS', 'IPCALAB.NS', 'IRCTC.NS', 'IRFC.NS', 
    'ITC.NS', 'JINDALSTEL.NS', 'JSWSTEEL.NS', 'JUBLFOOD.NS', 'KOTAKBANK.NS', 'LALPATHLAB.NS', 
    'LAURUSLABS.NS', 'LICHSGFIN.NS', 'LICI.NS', 'LT.NS', 'LTIM.NS', 'LTTS.NS', 
    'LUPIN.NS', 'M&M.NS', 'M&MFIN.NS', 'MANAPPURAM.NS', 'MARICO.NS', 'MARUTI.NS', 
    'MCDOWELL-N.NS', 'MCX.NS', 'METROPOLIS.NS', 'MGL.NS', 'MOTHERSON.NS', 'MPHASIS.NS', 
    'MRF.NS', 'MUTHOOTFIN.NS', 'NATIONALUM.NS', 'NAUKRI.NS', 'NAVINFLUOR.NS', 'NBCC.NS', 
    'NESTLEIND.NS', 'NHPC.NS', 'NMDC.NS', 'NTPC.NS', 'NYKAA.NS', 'OBEROIRLTY.NS', 
    'OFSS.NS', 'OIL.NS', 'ONGC.NS', 'PAGEIND.NS', 'PATANJALI.NS', 'PEL.NS', 
    'PERSISTENT.NS', 'PETRONET.NS', 'PFC.NS', 'PHOENIXLTD.NS', 'PIDILITIND.NS', 'PIIND.NS', 
    'PNB.NS', 'POLYCAP.NS', 'POWERTARID.NS', 'PRESTIGE.NS', 'PVRINOX.NS', 'RAMCOCEM.NS', 
    'RBLBANK.NS', 'RECLTD.NS', 'RELIANCE.NS', 'SAIL.NS', 'SBICARD.NS', 'SBILIFE.NS', 
    'SBIN.NS', 'SHREECEM.NS', 'SHRIRAMFIN.NS', 'SIEMENS.NS', 'SONACOMS.NS', 'SRF.NS', 
    'SUNPHARMA.NS', 'SUNTV.NS', 'SUPREMEIND.NS', 'SYNGENE.NS', 'TATACHEMICAL.NS', 
    'TATACOMM.NS', 'TATACONSUM.NS', 'TATAMOTORS.NS', 'TATAPOWER.NS', 'TATASTEEL.NS', 
    'TCS.NS', 'TECHM.NS', 'TITAN.NS', 'TORNTPHARM.NS', 'TRENT.NS', 'TVSMOTOR.NS', 
    'UNIONBANK.NS', 'UNITDSPIRITS.NS', 'UPL.NS', 'VBL.NS', 'VEDL.NS', 
    'VOLTAS.NS', 'WIPRO.NS', 'YESBANK.NS', 'ZOMATO.NS', 'ZYDUSLIFE.NS'
]

# --- 3. AUTHENTICATION (Publish to Web CSV Method) ---
def authenticate_user(user_in, pw_in):
    try:
        # REPLACE THIS with your "Publish to web" CSV link
        csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSEan21a9IVnkdmTFP2Q9O_ILI3waF52lFWQ5RTDtXDZ5MI4_yTQgFYcCXN5HxgkCxuESi5Dwe9iROB/pub?gid=0&single=true&output=csv"
        
        df = pd.read_csv(csv_url)
        df['username'] = df['username'].astype(str).str.strip().str.lower()
        df['password'] = df['password'].astype(str).str.strip()
        
        match = df[(df['username'] == str(user_in).strip().lower()) & 
                   (df['password'] == str(pw_in).strip())]
        return not match.empty
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return False

# --- 4. LOGIN GATE ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 Absa's F&O Pro Login")
    with st.form("login_form"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Log In"):
            if authenticate_user(u, p):
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid credentials or Connection Failed.")
    st.stop()

# --- 5. MAIN APPLICATION ---
st.title("🚀 Absa's Live F&O Screener Pro")
if st.sidebar.button("Log out"):
    st.session_state["authenticated"] = False
    st.rerun()

def get_sentiment(p_chg, oi_chg):
    if p_chg > 0 and oi_chg > 0: return "Long Buildup 🚀"
    if p_chg < 0 and oi_chg > 0: return "Short Buildup 📉"
    if p_chg < 0 and oi_chg < 0: return "Long Unwinding ⚠️"
    if p_chg > 0 and oi_chg < 0: return "Short Covering 💨"
    return "Neutral"

# --- HELPER: MARKET DASHBOARD ---
def fetch_market_dashboard():
    indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK"}
    data = {}
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    for name, ticker in indices.items():
        try:
            # Quick fetch for index data
            t = yf.Ticker(ticker)
            info = t.fast_info
            ltp = info['last_price']
            prev = info['previous_close']
            chg = ltp - prev
            pct = (chg / prev) * 100
            
            # Color code based on movement
            data[name] = {"ltp": ltp, "chg": chg, "pct": pct}
        except:
            data[name] = {"ltp": 0, "chg": 0, "pct": 0}

    # Render Metrics
    with col1:
        nifty = data["NIFTY 50"]
        st.metric(label="NIFTY 50", value=f"{nifty['ltp']:,.2f}", delta=f"{nifty['chg']:.2f} ({nifty['pct']:.2f}%)")
    
    with col2:
        bank = data["BANK NIFTY"]
        st.metric(label="BANK NIFTY", value=f"{bank['ltp']:,.2f}", delta=f"{bank['chg']:.2f} ({bank['pct']:.2f}%)")
        
    with col3:
        # Simple Sentiment Logic based on Nifty
        bias = "SIDEWAYS ↔️"
        color = "gray"
        if nifty['pct'] > 0.25: 
            bias = "BULLISH 🚀"
            color = "green"
        elif nifty['pct'] < -0.25: 
            bias = "BEARISH 📉"
            color = "red"
            
        st.markdown(f"""
            <div style="text-align: center; padding: 10px; border: 1px solid {color}; border-radius: 10px;">
                <h3 style="margin:0; color: {color};">Market Bias: {bias}</h3>
            </div>
        """, unsafe_allow_html=True)

@st.fragment(run_every=300)
def refreshable_data_tables():
    # 1. SHOW MARKET DASHBOARD FIRST
    fetch_market_dashboard()
    st.markdown("---") # Separator line
    
    bullish, bearish = [], []
    
    # IST TIME
    ist_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M:%S')
    st.write(f"🕒 **Last Data Sync:** {ist_time} IST (Auto-refreshing in 5 mins)")
    
    progress_bar = st.progress(0, text="Fetching Live Data...")
    
    for i, sym in enumerate(FNO_SYMBOLS):
        try:
            ticker = yf.Ticker(sym)
            data = ticker.history(period='60d', interval='1h') 
            
            if len(data) > 30:
                data['RSI'] = ta.rsi(data['Close'], length=14)
                adx_df = ta.adx(data['High'], data['Low'], data['Close'], length=14)
                
                # Active Momentum Logic (EMA Deviation)
                data['EMA_5'] = ta.ema(data['Close'], length=5)
                ltp = data['Close'].iloc[-1]
                ema_5 = data['EMA_5'].iloc[-1]
                momentum_pct = round(((ltp - ema_5) / ema_5) * 100, 2)
                
                curr_rsi = data['RSI'].iloc[-1]
                curr_adx = adx_df['ADX_14'].iloc[-1]
                prev_close = ticker.fast_info['previous_close']
                p_change = round(((ltp - prev_close) / prev_close) * 100, 2)
                
                clean_sym = sym.replace(".NS", "")
                tv_url = f"https://in.tradingview.com/chart/?symbol=NSE:{clean_sym}"
                
                oi_chg = 1 
                sentiment = get_sentiment(p_change, oi_chg)
                
                row = {
                    "Symbol": tv_url,
                    "LTP": round(ltp, 2),
                    "Mom %": momentum_pct, # Active Trend
                    "Chg %": p_change,
                    "RSI": round(curr_rsi, 1),
                    "ADX": round(curr_adx, 1),
                    "Sentiment": sentiment
                }

                if p_change > 0.5 and curr_rsi > 60 and curr_adx > 20:
                    bullish.append(row)
                elif p_change < -0.5 and curr_rsi < 45 and curr_adx > 20:
                    bearish.append(row)
            
            progress_bar.progress((i + 1) / len(FNO_SYMBOLS))
        except:
            continue
            
    progress_bar.empty()
    
    column_config = {
        "Symbol": st.column_config.LinkColumn(
            "Script (Click to Chart)", 
            display_text="symbol=NSE:(.*)"
        )
    }
    
    col1, col2 = st.columns(2)
    with col1:
        st.success("🟢 ACTIVE BULLS (Accelerating Up)")
        if bullish:
            st.dataframe(
                pd.DataFrame(bullish).sort_values(by="Mom %", ascending=False).head(10), 
                use_container_width=True, 
                hide_index=True,
                column_config=column_config
            )
        else:
            st.info("No bullish breakouts detected.")

    with col2:
        st.error("🔴 ACTIVE BEARS (Accelerating Down)")
        if bearish:
            st.dataframe(
                pd.DataFrame(bearish).sort_values(by="Mom %", ascending=True).head(10), 
                use_container_width=True, 
                hide_index=True,
                column_config=column_config
            )
        else:
            st.info("No bearish breakdowns detected.")

refreshable_data_tables()
