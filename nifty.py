import streamlit as st
from streamlit_gsheets import GSheetsConnection
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import time

# --- 1. GLOBAL SETTINGS & SYMBOLS ---
# Defined at top to prevent NameError
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

st.set_page_config(page_title="Absa's Live F&O Screener Pro", layout="wide")

# --- 2. AUTHENTICATION MODULE ---
def authenticate_user(user_in, pw_in):
    """Verifies credentials against GSheets with robust cleaning"""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Using ttl=0 to always get the freshest data from the sheet
        df = conn.read(worksheet="Users", ttl=0)
        
        # Robust Cleaning: Convert everything to string and strip spaces
        df['username'] = df['username'].astype(str).str.strip().str.lower()
        df['password'] = df['password'].astype(str).str.strip()
        
        user_match = df[
            (df['username'] == str(user_in).strip().lower()) & 
            (df['password'] == str(pw_in).strip())
        ]
        return not user_match.empty
    except Exception as e:
        # Catching the HTTP 400 or connection errors
        st.error(f"⚠️ Connection Error: {e}")
        return False

# --- 3. LOGIN PAGE UI ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 Absa's F&O Pro Login")
    
    # Debug Helper (Optional: Remove after fixing HTTP 400)
    if st.checkbox("Debug Connection"):
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            test_df = conn.read(worksheet="Users")
            st.success("Connection to Sheet Successful!")
            st.write("Current User List (Head):", test_df.head(2))
        except Exception as e:
            st.error(f"Debug Failed: {e}")

    with st.form("login_form"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Log In"):
            if authenticate_user(u, p):
                st.session_state["authenticated"] = True
                st.success("Login Successful!")
                st.rerun() # Refresh to show app
            else:
                st.error("Invalid credentials. Please try again.")
    st.stop() # Halt execution if not logged in

# --- 4. MAIN APPLICATION ---
st.title("🚀 Live F&O Intraday Momentum by Absa")
if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.rerun()

def get_sentiment(p_chg, oi_chg):
    """Categorize market sentiment based on Price and OI"""
    if p_chg > 0 and oi_chg > 0: return "Long Buildup 🚀"
    if p_chg < 0 and oi_chg > 0: return "Short Buildup 📉"
    if p_chg < 0 and oi_chg < 0: return "Long Unwinding ⚠️"
    if p_chg > 0 and oi_chg < 0: return "Short Covering 💨"
    return "Neutral"

@st.fragment(run_every=300)
def refreshable_data_tables():
    """Reruns only this block every 300s"""
    bullish, bearish = [], []
    st.write(f"🕒 **Update Sync:** {time.strftime('%H:%M:%S')} (Auto-refresh in 5 mins)")
    pb = st.progress(0, text="Analyzing Market Momentum...")
    
    for i, sym in enumerate(FNO_SYMBOLS):
        try:
            tk = yf.Ticker(sym)
            data = tk.history(period='60d', interval='1h') 
            if len(data) > 30:
                data['RSI'] = ta.rsi(data['Close'], length=14)
                adx_df = ta.adx(data['High'], data['Low'], data['Close'], length=14)
                
                curr_rsi, curr_adx = data['RSI'].iloc[-1], adx_df['ADX_14'].iloc[-1]
                ltp = data['Close'].iloc[-1]
                prev_close = tk.fast_info['previous_close']
                p_change = round(((ltp - prev_close) / prev_close) * 100, 2)
                
                sentiment = get_sentiment(p_change, 1) # Proxy OI
                row = {"Symbol": sym.replace(".NS", ""), "LTP": round(ltp, 2), 
                       "Chg%": p_change, "RSI": round(curr_rsi, 1), "ADX": round(curr_adx, 1), "Bias": sentiment}

                if p_change > 0.5 and curr_rsi > 60 and curr_adx > 20:
                    bullish.append(row)
                elif p_change < -0.5 and curr_rsi < 45 and curr_adx > 20:
                    bearish.append(row)
            pb.progress((i + 1) / len(FNO_SYMBOLS))
        except: continue
    pb.empty()
    
    c1, c2 = st.columns(2)
    with c1:
        st.success("🟢 BULLISH (RSI > 60 & ADX > 20)")
        if bullish: st.dataframe(pd.DataFrame(bullish), use_container_width=True, hide_index=True)
    with c2:
        st.error("🔴 BEARISH (RSI < 45 & ADX > 20)")
        if bearish: st.dataframe(pd.DataFrame(bearish), use_container_width=True, hide_index=True)

refreshable_data_tables()
