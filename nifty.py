import streamlit as st
from streamlit_gsheets import GSheetsConnection
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import time

# --- 1. DEFINE SYMBOLS AT TOP ---
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
def authenticate_user(u_in, p_in):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Users", ttl=0)
        # Clean data for robust matching
        df['username'] = df['username'].astype(str).str.strip().str.lower()
        df['password'] = df['password'].astype(str).str.strip()
        
        match = df[(df['username'] == str(u_in).strip().lower()) & 
                   (df['password'] == str(p_in).strip())]
        return not match.empty
    except Exception as e:
        st.error(f"⚠️ Connection Error: {e}")
        return False

# --- 3. LOGIN INTERFACE ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 Absa's F&O Pro Login")
    with st.form("login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Log In"):
            if authenticate_user(u, p):
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid credentials.")
    st.stop()

# --- 4. MAIN APPLICATION ---
st.title("🚀 Live F&O Intraday Momentum by Absa")
if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.rerun()

@st.fragment(run_every=300) #
def data_tables():
    bull, bear = [], []
    st.write(f"🕒 **Last Sync:** {time.strftime('%H:%M:%S')}")
    pb = st.progress(0, text="Fetching Live Momentum...")
    
    for i, sym in enumerate(FNO_SYMBOLS):
        try:
            tk = yf.Ticker(sym)
            hist = tk.history(period='60d', interval='1h')
            if len(hist) > 30:
                hist['RSI'] = ta.rsi(hist['Close'], length=14)
                adx = ta.adx(hist['High'], hist['Low'], hist['Close'], length=14)
                
                rsi, adx_val = hist['RSI'].iloc[-1], adx['ADX_14'].iloc[-1]
                ltp = hist['Close'].iloc[-1]
                prev = tk.fast_info['previous_close']
                p_chg = round(((ltp - prev) / prev) * 100, 2)
                
                row = {"Symbol": sym.replace(".NS", ""), "LTP": round(ltp, 2), "Chg%": p_chg, "RSI": round(rsi, 1), "ADX": round(adx_val, 1)}
                if p_chg > 0.5 and rsi > 60 and adx_val > 20: bull.append(row)
                elif p_chg < -0.5 and rsi < 45 and adx_val > 20: bear.append(row)
            pb.progress((i + 1) / len(FNO_SYMBOLS))
        except: continue
    pb.empty()
    
    c1, c2 = st.columns(2)
    with c1:
        st.success("🟢 BULLISH")
        if bull: st.dataframe(pd.DataFrame(bull), use_container_width=True, hide_index=True)
    with c2:
        st.error("🔴 BEARISH")
        if bear: st.dataframe(pd.DataFrame(bear), use_container_width=True, hide_index=True)

data_tables()
