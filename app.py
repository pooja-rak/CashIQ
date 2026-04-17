# 🔥 TOP OF FILE - CORRECT IMPORTS (CRITICAL!)
import streamlit as st
import pandas as pd
import pickle
from datetime import datetime
import json
import hashlib
import os
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium

import openrouteservice


@st.cache_resource
def get_ors_client():
    ORS_API_KEY = st.secrets.get("ORS_API_KEY", "demo")
    if ORS_API_KEY == "demo":
        st.warning("⚠️ Add ORS_API_KEY to .streamlit/secrets.toml")
        return None
    return openrouteservice.Client(key=ORS_API_KEY)


st.set_page_config(page_title="CashIQ - Smart ATM AI", layout="wide")
st.markdown("""
<style>

/* Background */
html, body, .stApp {
    background: linear-gradient(135deg, #eef2ff, #f8fafc);
    font-family: 'Inter', sans-serif;
}

/* Card container */
.card {
    background: white;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #2563eb, #1e40af);
    color: white !important;
    border-radius: 12px;
    font-weight: 600;
    border: none;
    padding: 0.6rem 1.2rem;
    transition: 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(37,99,235,0.4);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0f172a;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Metrics */
[data-testid="metric-container"] {
    background: white;
    border-radius: 14px;
    padding: 15px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.06);
}

</style>
""", unsafe_allow_html=True)

# 🔥 LOAD MODELS FIRST
@st.cache_data
def load_models():
    atm_locations = pd.read_csv("data/atm_master_data.csv")
    crowd_model = pickle.load(open("models/crowd_model.pkl", "rb"))
    cash_model = pickle.load(open("models/cash_model.pkl", "rb"))
    condition_model = pickle.load(open("models/condition_model.pkl", "rb"))
    le_atm = pickle.load(open("models/le_atm.pkl", "rb"))
    le_crowd = pickle.load(open("models/le_crowd.pkl", "rb"))
    le_cash = pickle.load(open("models/le_cash.pkl", "rb"))
    le_condition = pickle.load(open("models/le_condition.pkl", "rb"))
    le_time = pickle.load(open("models/le_time.pkl", "rb"))
    le_day = pickle.load(open("models/le_day.pkl", "rb"))
    return (atm_locations, crowd_model, cash_model, condition_model, le_atm, le_crowd, le_cash, le_condition, le_time, le_day)


atm_locations, crowd_model, cash_model, condition_model, le_atm, le_crowd, le_cash, le_condition, le_time, le_day = load_models()


def init_users():
    if not os.path.exists("users.json"):
        with open("users.json", "w") as f:
            json.dump({}, f)

def get_users():
    init_users()
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def register(username, password):
    users = get_users()
    if username in users: return False, "User exists!"
    users[username] = {
    "password": hash_pwd(password),
    "favorites": [],
    "recent": [],
    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    save_users(users)
    return True, "Registered!"

def login(username, password):
    users = get_users()
    return username in users and users[username]["password"] == hash_pwd(password)


if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "username" not in st.session_state: st.session_state.username = ""


if "app_stage" not in st.session_state:
    st.session_state.app_stage = "landing"  # landing → auth → app


if st.session_state.app_stage == "landing":

    st.write("""
# 💳 CashIQ – Intelligent ATM Locator System

### AI-Powered Smart Banking Assistance

CashIQ is a Machine Learning-based ATM Intelligence Platform designed to solve real-world challenges faced by users while searching for ATMs.

Traditional ATM locators only show locations.  
CashIQ goes beyond location by providing predictive intelligence.

🔬 This system integrates multiple ML models to:

• 🔍 Identify the nearest ATM using geolocation  
• 📊 Predict crowd levels based on time and day  
• 💰 Estimate cash availability probability  
• 🏧 Analyze ATM working condition status  
• 🗺️ Generate optimized navigation routes  
• ⭐ Personalize user experience with saved preferences  

📈 By combining data analytics, predictive modeling, and real-time mapping,  
CashIQ reduces waiting time, avoids inconvenience, and enhances user decision-making.

This project demonstrates:
• Application of Supervised Machine Learning  
• Real-world prediction system deployment  
• Integration of OpenStreetMap APIs  
• End-to-end full-stack development using Streamlit  

---

### 🚀 Transforming Traditional ATM Search into Intelligent Decision Support System
""")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔓 Login", use_container_width=True):
            st.session_state.app_stage = "auth"
            st.rerun()

    with col2:
        if st.button("➕ Register", use_container_width=True):
            st.session_state.app_stage = "auth"
            st.rerun()

    st.stop()


if st.session_state.app_stage == "auth" and not st.session_state.authenticated:
    
    st.markdown("# 🔐 CashIQ Login")
    tab1, tab2 = st.tabs(["🔓 Login", "➕ Register"])
    
    with tab1:
        username = st.text_input("👤 Username", key="login_username")
        password = st.text_input("🔒 Password", type="password", key="login_password")
        if st.button("🚀 Login", key="login_btn"):
            if login(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.app_stage = "app"
                st.success(f"✅ Welcome {username}!")
                st.rerun()
            else:
                st.error("❌ Wrong credentials!")
    
    with tab2:
        reg_user = st.text_input("👤 Username", key="register_username")
        reg_pwd = st.text_input("🔒 Password", type="password", key="register_password")
        if st.button("✅ Register", key="register_btn"):
            success, msg = register(reg_user, reg_pwd)
            if success: st.success("✅ Login now!")
            else: st.error(msg)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()



if "page" not in st.session_state:
    st.session_state.page = "📊 Dashboard"


if "go_to" in st.session_state:
    st.session_state.page = st.session_state.go_to
    del st.session_state.go_to

st.sidebar.success(f"Hey!! Welcome {st.session_state.username}")

# 🔥 UPDATED SIDEBAR - SPLIT FIND ATM INTO 2 PAGES
page = st.sidebar.radio(
    "Cash IQ",
    ["📊 Dashboard", "🧭 Find ATM", "🗺️ Route", "🎉 Complete", "⭐ Favorites", "📜 Recent"],  # 🔥 SPLIT HERE
    key="page"
)


if "previous_page" not in st.session_state:
    st.session_state.previous_page = page

if st.session_state.previous_page != page:
    
    keys_to_reset = ["show_route", "selected_atm"]
    if page != "🎉 Complete":
        keys_to_reset.append("finish_page")
    
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

    st.session_state.previous_page = page

if st.sidebar.button("🚪 Logout", key="logout_btn", use_container_width=True): 
    st.session_state.authenticated = False
    st.session_state.app_stage = "landing"
    st.rerun()


if page == "🧭 Find ATM":
    st.markdown("## 🧭 Smart ATM Finder")
    
    
    default_loc = st.session_state.get('location', 'Chennai Central')
    location = st.text_input("📍 Location", value=default_loc)
    if 'location' in st.session_state: del st.session_state.location
    
    
    default_radius = st.session_state.get('radius', 3)
    radius = st.slider("Radius (km)", 1, 10, default_radius)
    if 'radius' in st.session_state: del st.session_state.radius
    
    
    default_bank = st.session_state.get('bank_filter', 'All Banks')
    bank_options = ["All Banks"] + sorted(atm_locations["bank"].unique().tolist())
    bank_idx = 0 if default_bank == 'All Banks' else bank_options.index(default_bank)
    bank_filter = st.selectbox("🏦 Bank", bank_options, index=bank_idx)
    if 'bank_filter' in st.session_state: del st.session_state.bank_filter
    
    
    if 'repeat_search' in st.session_state and st.session_state.repeat_search is not None:
        repeat = st.session_state.repeat_search
        if isinstance(repeat, dict) and all(key in repeat for key in ['search_location', 'search_radius', 'search_bank']):
            location = repeat['search_location']
            radius = repeat['search_radius'] 
            bank_filter = repeat['search_bank']
            st.session_state.repeat_search = None
            st.rerun()
    
    if st.button("🔍 Find Best ATMs", use_container_width=True, key="find_atms_btn"):
        with st.spinner("🤖 AI Predicting..."):
            now = datetime.now()
            hour = now.hour
            day_name = now.strftime("%a")
            
            # Time classification
            if 6 <= hour < 12: time_slot = "Morning"
            elif 12 <= hour < 16: time_slot = "Afternoon"
            elif 16 <= hour < 20: time_slot = "Evening"
            else: time_slot = "Night"
            
            is_weekend = 1 if day_name in ["Sat", "Sun"] else 0
            time_enc = le_time.transform([time_slot])[0]
            day_enc = le_day.transform([day_name])[0]
            
            
            geolocator = Nominatim(user_agent="cashiq")
            user_loc = geolocator.geocode(location)
            if user_loc:
                st.session_state.user_loc = (user_loc.latitude, user_loc.longitude)
                
                
                filtered = atm_locations if bank_filter == "All Banks" else atm_locations[atm_locations["bank"] == bank_filter]
                
                results = []
                for _, atm in filtered.iterrows():
                    atm_loc = (atm["latitude"], atm["longitude"])
                    dist = geodesic(st.session_state.user_loc, atm_loc).km
                    
                    if dist <= radius:
                        atm_enc = le_atm.transform([atm["atm_id"]])[0]
                        
                        
                        X_crowd = pd.DataFrame([{
                            'atm_id_enc': atm_enc, 'time_enc': time_enc,
                            'day_enc': day_enc, 'is_weekend': is_weekend
                        }])
                        crowd_enc = crowd_model.predict(X_crowd)[0]
                        crowd = le_crowd.inverse_transform([crowd_enc])[0]
                        
                        X_cash = pd.DataFrame([{
                            'atm_id_enc': atm_enc, 'time_enc': time_enc,
                            'crowd_enc': crowd_enc, 'is_weekend': is_weekend
                        }])
                        cash_enc = cash_model.predict(X_cash)[0]
                        cash_status = le_cash.inverse_transform([cash_enc])[0]
                        
                        X_cond = pd.DataFrame([{'atm_id_enc': atm_enc}])
                        cond_enc = condition_model.predict(X_cond)[0]
                        condition = le_condition.inverse_transform([cond_enc])[0]
                        
                        # AI Score
                        base_score = 85.0
                        crowd_bonus = 10 if crowd == "Low" else 2 if crowd == "Medium" else 0
                        cash_bonus = 8 if cash_status == "High" else 3 if cash_status == "Medium" else 0
                        cond_bonus = 4 if condition == "Good" else 0 if condition == "Fair" else -5
                        ai_score = max(80.0, min(97.0, base_score + crowd_bonus + cash_bonus + cond_bonus))
                        
                        results.append({
                            'ATM_ID': atm["atm_id"],
                            'Bank': atm["bank"],
                            'AI_Score': f"{ai_score}%",
                            'AI_Score_Num': ai_score,
                            'Crowd': crowd,
                            'Cash': cash_status,
                            'Condition': condition,
                            'Distance': f"{dist:.2f}km",
                            'Distance_Num': dist,
                            'Lat': atm["latitude"],
                            'Lon': atm["longitude"]
                        })
                
                st.session_state.results = pd.DataFrame(results)
                st.success(f"✅ Found {len(results)} ATMs!")
                
                # 🔥 RECENT TRACKING - FIXED
                if len(results) > 0:

                    users = get_users()
                    username = st.session_state.username

                    # Ensure user structure exists properly
                    if username not in users:
                        users[username] = {
                            "password": "",
                            "favorites": [],
                            "recent": []
                        }

                    if "recent" not in users[username]:
                        users[username]["recent"] = []

                    new_recent = {
                        'search_location': location,
                        'search_radius': radius,
                        'search_bank': bank_filter,
                        'top_atm_id': results[0]['ATM_ID'],
                        'top_atm_bank': results[0]['Bank'],
                        'top_ai_score': results[0]['AI_Score'],
                        'search_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'result_count': len(results)
                    }

                    users[username]["recent"].insert(0, new_recent)
                    users[username]["recent"] = users[username]["recent"][:20]

                    save_users(users)
                    st.toast(f"📜 Saved! Total: {len(users[username]['recent'])}", icon="🔍")
    
    
    if 'results' in st.session_state and not st.session_state.results.empty:
        df = st.session_state.results.sort_values('Distance_Num')  # Closest first!
        
        
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("🥇 Best", f"{df['AI_Score_Num'].max():.0f}%")
        with col2: st.metric("📏 Closest", f"{df['Distance_Num'].min():.1f}km")
        with col3: st.metric("🎯 Total", len(df))
        
        
        st.markdown("### 🤖 **Smart ATM Recommendations**")
        st.dataframe(df[['ATM_ID', 'Bank', 'AI_Score', 'Crowd', 'Cash', 'Condition', 'Distance']], 
                    use_container_width=True, hide_index=True)
        
        
        st.markdown("### 🎯 **Select ATM**")
        atm_display_names = [f"{row['ATM_ID']} - {row['Bank']} ({row['AI_Score']})" for _, row in df.iterrows()]
        selected_display_name = st.selectbox("Choose ATM:", atm_display_names)
        
        if selected_display_name:
            selected_atm_id = selected_display_name.split(" - ")[0]
            st.session_state.selected_atm = df[df['ATM_ID'] == selected_atm_id].iloc[0]
            st.success(f"✅ **{selected_atm_id}** | {st.session_state.selected_atm['AI_Score']} | {st.session_state.selected_atm['Distance']}")
        
        
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            if st.button("⭐ Save to Favorites", use_container_width=True, key="save_fav_find"):
                users = get_users()
                username = st.session_state.username
                if 'selected_atm' in st.session_state:
                    current_atm = st.session_state.selected_atm
                    new_fav = {
                        'atm_id': current_atm['ATM_ID'],
                        'ai_score': current_atm['AI_Score'].replace('%', ''),
                        'added_date': datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    
                    user_favorites = users.get(username, {}).get("favorites", [])
                    if any(fav['atm_id'] == new_fav['atm_id'] for fav in user_favorites):
                        st.toast(f"⭐ **{current_atm['ATM_ID']}** already in favorites!", icon="⭐")
                    else:
                        user_favorites.append(new_fav)
                        users[username] = {"favorites": user_favorites, "password": users.get(username, {}).get("password", "")}
                        save_users(users)
                        st.toast(f"⭐ **{current_atm['ATM_ID']}** saved to favorites!", icon="⭐")
                else:
                    st.warning("👆 Select ATM first!")
        
        with col2:
            if st.button("🗺️ Go to Route", use_container_width=True, key="go_route_find"):  # 🔥 CHANGED
                if 'selected_atm' in st.session_state:
                    st.session_state.go_to = "🗺️ Route"  # 🔥 NEW PAGE
                    st.rerun()
                else:
                    st.warning("👆 Select ATM first!")
        
        with col3:
            if st.button("🔄 New Search", use_container_width=True, key="new_search_find"):
                for key in ['results', 'selected_atm', 'user_loc']:
                    if key in st.session_state: del st.session_state[key]
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# 🔥 NEW PAGE 2: ROUTE & NAVIGATION ONLY (🗺️ Route)
elif page == "🗺️ Route":
    st.markdown("## 🗺️ Navigation & Route")
    
    # 🔥 CHECK IF WE HAVE REQUIRED DATA
    if 'results' not in st.session_state or st.session_state.results.empty:
        st.warning("👆 **No search results!** Go to 🧭 Find ATM first.")
        if st.button("🧭 Find ATM", use_container_width=True):
            st.session_state.go_to = "🧭 Find ATM"
            st.rerun()
        st.stop()
    
    # 🔥 IF NO SELECTED ATM, SHOW RESULTS TABLE AGAIN
    if 'selected_atm' not in st.session_state:
        df = st.session_state.results.sort_values('Distance_Num')
        st.markdown("### 🎯 **Select ATM for Route**")
        atm_display_names = [f"{row['ATM_ID']} - {row['Bank']} ({row['AI_Score']})" for _, row in df.iterrows()]
        selected_display_name = st.selectbox("Choose ATM:", atm_display_names)
        
        if selected_display_name:
            selected_atm_id = selected_display_name.split(" - ")[0]
            st.session_state.selected_atm = df[df['ATM_ID'] == selected_atm_id].iloc[0]
            st.rerun()
        else:
            st.stop()
    
    # 🔥 SHOW SELECTED ATM INFO
    atm = st.session_state.selected_atm
    st.success(f"✅ Navigating to: **{atm['ATM_ID']}** | {atm['AI_Score']} | {atm['Distance']}")
    
    # 🔥 ROUTE MAP
    ors_client = get_ors_client()
    
    if 'user_loc' not in st.session_state:
        st.warning("📍 Location not set. Using Chennai default.")
        st.session_state.user_loc = (13.0827, 80.2707)  # Chennai default
    
    if ors_client:
        try:
            coords = [
                (st.session_state.user_loc[1], st.session_state.user_loc[0]),
                (float(atm['Lon']), float(atm['Lat']))
            ]

            route = ors_client.directions(coords, profile='driving-car')
            geometry = route['routes'][0]['geometry']
            decoded = openrouteservice.convert.decode_polyline(geometry)

            m = folium.Map(location=st.session_state.user_loc, zoom_start=14)
            folium.Marker(st.session_state.user_loc, popup="📍 You",
                        icon=folium.Icon(color="blue")).add_to(m)
            folium.Marker([atm['Lat'], atm['Lon']],
                        popup=f"{atm['ATM_ID']}",
                        icon=folium.Icon(color="green")).add_to(m)
            folium.PolyLine(
                [(coord[1], coord[0]) for coord in decoded['coordinates']],
                color="#447DE6", weight=8
            ).add_to(m)

            st_folium(m, width=800, height=400)
            
        except:
            m = folium.Map(location=st.session_state.user_loc, zoom_start=14)
            folium.Marker(st.session_state.user_loc).add_to(m)
            folium.Marker([atm['Lat'], atm['Lon']]).add_to(m)
            folium.PolyLine(
                [st.session_state.user_loc, [atm['Lat'], atm['Lon']]],
                color="orange", weight=8
            ).add_to(m)
            st_folium(m, width=800, height=400)
    else:
        m = folium.Map(location=st.session_state.user_loc, zoom_start=14)
        folium.Marker(st.session_state.user_loc, popup="📍 You").add_to(m)
        folium.Marker([atm['Lat'], atm['Lon']], popup=f"{atm['ATM_ID']}").add_to(m)
        folium.PolyLine(
            [st.session_state.user_loc, [atm['Lat'], atm['Lon']]],
            color="orange", weight=8
        ).add_to(m)
        st_folium(m, width=800, height=400)

    # 🔥 ROUTE ACTION BUTTONS
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button("✅ Finish Journey", use_container_width=True, key="finish_route"):
            st.session_state.go_to = "🎉 Complete"  # Navigate to finish page
            st.session_state.finish_page = "🎉 Complete"
            st.rerun()
    
    with col2:
        if st.button("⭐ Save to Favorites", use_container_width=True, key="save_fav_route"):
            users = get_users()
            username = st.session_state.username
            new_fav = {
                'atm_id': atm['ATM_ID'],
                'ai_score': atm['AI_Score'].replace('%', ''),
                'added_date': datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            
            user_favorites = users.get(username, {}).get("favorites", [])
            if any(fav['atm_id'] == new_fav['atm_id'] for fav in user_favorites):
                st.toast(f"⭐ **{atm['ATM_ID']}** already in favorites!", icon="⭐")
            else:
                user_favorites.append(new_fav)
                users[username] = {"favorites": user_favorites, "password": users.get(username, {}).get("password", "")}
                save_users(users)
                st.toast(f"⭐ **{atm['ATM_ID']}** saved to favorites!", icon="⭐")
    
    with col3:
        if st.button("🔙 Back to Search", use_container_width=True, key="back_search"):
            st.session_state.go_to = "🧭 Find ATM"
            st.rerun()

elif page == "🎉 Complete":

    # 🔥 FINISH PAGE
    # Show content when navigating to this page (either via button or sidebar)
    if 'finish_page' not in st.session_state:
        st.session_state.finish_page = "🎉 Complete"
    
    # Check if there are search results - if not, show warning
    if 'results' not in st.session_state or st.session_state.results.empty:
        st.warning("👆 No navigation results! Go to 🧭 Find ATM map first.")
        if st.button("🧭 Find ATM", use_container_width=True):
            st.session_state.go_to = "🧭 Find ATM"
            st.rerun()
    else:
        st.markdown("# 🎉 Journey Completed!")
        st.markdown("### Thank you for using CashIQ 🚀")
        st.success("✅ Visit Completed Successfully!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠 Dashboard", use_container_width=True):
                for key in ['results', 'selected_atm', 'show_route', 'finish_page', 'user_loc']:
                    if key in st.session_state: del st.session_state[key]
                st.session_state.go_to = "📊 Dashboard"
                st.rerun()
        
        with col2:
            if st.button("🔍 New Search", use_container_width=True):
                for key in ['results', 'selected_atm', 'show_route', 'finish_page', 'user_loc']:
                    if key in st.session_state: del st.session_state[key]
                st.session_state.go_to = "🧭 Find ATM"
                st.rerun()

# 🔥 FAVORITES PAGE - FIXED WITH ROUTE MAP
elif page == "⭐ Favorites":
    
    st.markdown("## ⭐ Your Favorite ATMs")
    
    users = get_users()
    username = st.session_state.username
    favorites = users.get(username, {}).get("favorites", [])
    
    if not favorites:
        st.info("👆 **No favorites yet!** Add from Find ATM page")
        if st.button("🧭 Find ATM", use_container_width=True, key="find_atm_fav"):
            st.session_state.go_to = "🧭 Find ATM"
            st.rerun()
    else:
        st.markdown("### 📋 Favorites List")
        key_counter = 0
        
        for fav in favorites:
            atm_row = atm_locations[atm_locations['atm_id'] == fav['atm_id']]
            if atm_row.empty: 
                continue
            
            atm = atm_row.iloc[0]
            key_counter += 1
            
            col1, col2, col3 = st.columns([4, 1.5, 1.5])
            
            with col1:
                st.markdown(f"**{fav['atm_id']}** - {atm['bank']} ({fav['ai_score']}%)")
                st.caption(atm.get('address', 'No address'))
            
            with col2:
                if st.button("🗺️ Route", key=f"route_{fav['atm_id']}_{key_counter}", use_container_width=True):
                    st.session_state.user_loc = (13.0827, 80.2707)  # Chennai default
                    st.session_state.selected_atm = {
                        'ATM_ID': fav['atm_id'], 
                        'Lat': atm['latitude'], 
                        'Lon': atm['longitude'], 
                        'AI_Score': f"{fav['ai_score']}%",
                        'Bank': atm['bank']
                    }
                    st.session_state.go_to = "🗺️ Route"  # 🔥 NOW GOES TO NEW ROUTE PAGE
                    st.rerun()
            
            with col3:
                if st.button("❌ Remove", key=f"del_{fav['atm_id']}_{key_counter}", use_container_width=True):
                    users[username]["favorites"] = [f for f in favorites if f['atm_id'] != fav['atm_id']]
                    save_users(users)
                    st.rerun()
            
            st.markdown("─" * 125)

# 🔥 RECENT PAGE - FULLY FIXED
elif page == "📜 Recent":
    
    st.markdown("## 📜 Your Recent Searches")
    
    users = get_users()
    username = st.session_state.username
    user_recent = users.get(username, {}).get("recent", [])
    
    # Debug info
    col1, col2 = st.columns(2)
    with col1: st.caption(f"👤 {username}")
    with col2: st.caption(f"📊 {len(user_recent)} searches")
    
    if not user_recent:
        st.info("👆 No recent searches yet!")
        if st.button("🧭 Find ATM",use_container_width=True):
            st.session_state.go_to = "🧭 Find ATM"
            st.rerun()
    else:
        st.markdown("### 📋 Recent Searches")
        for i, recent in enumerate(user_recent[:10]):
            col1, col2, col3, col4 = st.columns([3, 2, 1.5, 2])
            
            with col1:
                st.markdown(f"**🔍 {recent['search_location']}**")
                st.caption(f"{recent['search_radius']}km | {recent['search_bank']}")
            
            with col2: st.caption(f"⭐ {recent['top_atm_id']}")
            with col3: st.caption(recent['search_date'])
            
            with col4:
                if st.button("🔄 Repeat", key=f"repeat_{i}"):
                    st.session_state.repeat_search = {
                        'search_location': recent['search_location'],
                        'search_radius': recent['search_radius'],
                        'search_bank': recent['search_bank']
                    }
                    st.session_state.go_to = "🧭 Find ATM"
                    st.rerun()
            
            st.markdown("─" * 125)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 🔥 DASHBOARD
elif page == "📊 Dashboard":
    
    st.markdown("# 🚀 CashIQ Dashboard")
#========

    st.header("Welcome to CashIQ the Smart ATM Locator")
    st.subheader("Find Cash. Faster. Smarter. Safer.")

    st.write("""
    In today's fast-moving world, every second matters. Searching for an ATM shouldn't waste your time or cause unnecessary stress.

    **Smart ATM Locator** is designed to help you quickly find the nearest ATM with intelligent navigation and a seamless user experience.

    Whether you're traveling, in an emergency, or simply looking for your preferred bank — we've got you covered.
    """)

    st.markdown("---")

    st.header("🌍 What Makes Us Different?")

    st.markdown("""
    🔹 **Instant Location Detection**  
    Automatically find ATMs near your current location.

    🔹 **Smart Bank Selection**  
    Choose your preferred bank and get filtered, relevant results.

    🔹 **Shortest Route Navigation**  
    Get optimized paths that save time and effort.

    🔹 **Accurate Distance Calculation**  
    Know exactly how far the ATM is before you start moving.

    🔹 **Clean & User-Friendly Interface**  
    Simple design. Smooth experience. No confusion.
    """)

    st.markdown("---")

    st.header("💡 Designed For Everyone")

    st.markdown("""
    - 🎓 Students who need quick access to cash  
    - 👩‍💼 Working professionals on tight schedules  
    - 🌍 Travelers exploring new cities  
    - 🚨 Anyone facing urgent cash needs  
    """)

    st.markdown("---")

    st.header("🚀 Get Started Now")

    
    if st.button("🧭 Find ATM",use_container_width=True):
        st.session_state.go_to = "🧭 Find ATM"
        st.rerun()

    st.write("""
    Experience faster, smarter ATM discovery.  

    Click below and locate your nearest ATM instantly.
    """)
#==============

    st.metric("🏦 Total ATMs", len(atm_locations))
    col1, col2 = st.columns(2)
    with col1:
        st.metric("⭐ Your Favorites", len(get_users().get(st.session_state.username, {}).get("favorites", [])))
    with col2:
        st.metric("📜 Your Recent", len(get_users().get(st.session_state.username, {}).get("recent", [])))
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown(f"## {page}")
    st.info("Coming soon!")

st.markdown('</div>', unsafe_allow_html=True)
