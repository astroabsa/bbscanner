import streamlit as st
from streamlit_gsheets import GSheetsConnection
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import time

# --- DATABASE CONNECTION ---
def authenticate_user(username, password):
    try:
        # Connect to Google Sheets
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Users") # Name of your sheet tab
        
        # Verify credentials
        user_row = df[(df['username'] == username) & (df['password'] == password)]
        return not user_row.empty
    except:
        return False

# --- AUTHENTICATION UI ---
def login_page():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🔐 Absa's F&O Pro Login")
        with st.form("login_form"):
            user = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            submit = st.form_submit_button("Log In")
            
            if submit:
                if authenticate_user(user, pw):
                    st.session_state["authenticated"] = True
                    st.rerun() # Refresh to show the app
                else:
                    st.error("Invalid credentials. Please try again.")
        return False
    return True

# --- MAIN APPLICATION ---
if login_page():
    st.set_page_config(page_title="Absa's Live F&O Screener Pro", layout="wide")
    st.title("🚀 Live F&O Intraday Momentum by Absa")
    
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

    # List of F&O Symbols
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

    def get_sentiment(p_chg, oi_chg):
        if p_chg > 0 and oi_chg > 0: return "Long Buildup 🚀"
        if p_chg < 0 and oi_chg > 0: return "Short Buildup 📉"
        if p_chg < 0 and oi_chg < 0: return "Long Unwinding ⚠️"
        if p_chg > 0 and oi_chg < 0: return "Short Covering 💨"
        return "Neutral"

    @st.fragment(run_every=300)
    def refreshable_data_tables():
        bullish, bearish = [], []
        st.write(f"🕒 **Last Data Sync:** {time.strftime('%H:%M:%S')} (Auto-refreshing in 5 mins)")
        
        progress_bar = st.progress(0, text="Fetching Live Data...")
        
        for i, sym in enumerate(FNO_SYMBOLS):
            try:
                ticker = yf.Ticker(sym)
                data = ticker.history(period='60d', interval='1h') 
                if len(data) > 30:
                    data['RSI'] = ta.rsi(data['Close'], length=14)
                    adx_df = ta.adx(data['High'], data['Low'], data['Close'], length=14)
                    
                    curr_rsi = data['RSI'].iloc[-1]
                    curr_adx = adx_df['ADX_14'].iloc[-1]
                    ltp = data['Close'].iloc[-1]
                    prev_close = ticker.fast_info['previous_close']
                    p_change = round(((ltp - prev_close) / prev_close) * 100, 2)
                    
                    oi_chg = 1 
                    sentiment = get_sentiment(p_change, oi_chg)
                    
                    row = {
                        "Symbol": sym.replace(".NS", ""),
                        "LTP": round(ltp, 2),
                        "Change %": p_change,
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
        
        col1, col2 = st.columns(2)
        with col1:
            st.success("🟢 BULLISH")
            if bullish:
                st.dataframe(pd.DataFrame(bullish).sort_values(by="Change %", ascending=False), use_container_width=True, hide_index=True)
            else:
                st.info("No bullish breakouts.")
        with col2:
            st.error("🔴 BEARISH")
            if bearish:
                st.dataframe(pd.DataFrame(bearish).sort_values(by="Change %"), use_container_width=True, hide_index=True)
            else:
                st.info("No bearish breakdowns.")

    refreshable_data_tables()