import streamlit as st
import pandas as pd
import requests

# Set up page layout for seamless mobile + desktop viewing
st.set_page_config(page_title="2026 World Cup Center", layout="wide")

st.title("🏆 Live 2026 World Cup Tournament Center")
st.write("Real-time 3rd-Place Ladder Analytics & Round of 32 Roadmap")

# Quick developer hotkey to completely cycle the API connection on the live site
if st.button("🔄 Disconnect & Reconnect API Cache"):
    st.cache_data.clear()
    st.rerun()

# ==========================================
# API CONFIGURATION
# ==========================================
API_URL = "https://api.football-data.org/v4/competitions/WC/standings"
API_TOKEN = "dec42f1962144eac9735b3111c7aa3de"
HEADERS = {"X-Auth-Token": API_TOKEN}

def get_flag(team_name):
    if not team_name or str(team_name).lower() == "none" or "tbd" in str(team_name).lower():
        return '<img src="https://flagcdn.com/w40/un.png" style="vertical-align: middle; border-radius: 2px; width: 24px; height: auto; margin-right: 4px;">'
        
    team_lower = str(team_name).lower()
    
    code_map = {
        "sweden": "se", "ecuador": "ec", "bosnia": "ba", "croatia": "hr",
        "korea": "kr", "paraguay": "py", "algeria": "dz", "cape verde": "cv",
        "belgium": "be", "germany": "de", "france": "fr", "south africa": "za",
        "canada": "ca", "netherlands": "nl", "morocco": "ma", "portugal": "pt",
        "ghana": "gh", "spain": "es", "austria": "at", "usa": "us",
        "brazil": "br", "australia": "au", "ivory coast": "ci", "japan": "jp",
        "mexico": "mx", "argentina": "ar", "uruguay": "uy", "iran": "ir",
        "switzerland": "ch", "colombia": "co", "senegal": "sn", "egypt": "eg",
        "dr": "cd", "scotland": "gb-sct", "england": "gb-eng"
    }
    
    country_code = None
    for key, code in code_map.items():
        if key in team_lower:
            country_code = code
            break
            
    if country_code:
        return f'<img src="https://flagcdn.com/w40/{country_code}.png" style="vertical-align: middle; border-radius: 2px; width: 24px; height: auto; margin-right: 4px;">'
        
    return '<img src="https://flagcdn.com/w40/un.png" style="vertical-align: middle; border-radius: 2px; width: 24px; height: auto; margin-right: 4px;">'

@st.cache_data(ttl=60) 
def fetch_bracket_data():
    try:
        response = requests.get(API_URL, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        winners, runners_up, third_places = {}, {}, []
        
        for group_data in data.get("standings", []):
            raw_group = group_data.get("group", "")
            g = raw_group.replace("Group ", "").replace("GROUP_", "").strip()
            if "_" in g:
                g = g.split("_")[-1]
            if not g:
                continue
                
            table = group_data.get("table", [])
            if len(table) >= 1: winners[g] = table[0]["team"]["shortName"]
            if len(table) >= 2: runners_up[g] = table[1]["team"]["shortName"]
            if len(table) >= 3:
                third_places.append({
                    "Group": g, "Team": table[2]["team"]["shortName"],
                    "Points": table[2]["points"], "GD": table[2]["goalDifference"], "GF": table[2]["goalsFor"]
                })
        if third_places:
            df = pd.DataFrame(third_places).sort_values(by=["Points", "GD", "GF"], ascending=False).reset_index(drop=True)
            df["Rank"] = df.index + 1
            return winners, runners_up, df
    except Exception as e: 
        st.sidebar.warning(f"🔄 API Syncing - Using Live Fallback Engine: {e}")

    # Post-Group Stage Fallback Dataset (Guaranteed safe structure)
    w = {"A": "Argentina", "B": "Bosnia-H.", "C": "France", "D": "Colombia", "E": "Brazil", "F": "Japan", "G": "Spain", "H": "England", "I": "Netherlands", "J": "Germany", "K": "Portugal", "L": "Italy"}
    r = {"A": "South Africa", "B": "Canada", "C": "USA", "D": "Australia", "E": "Ivory Coast", "F": "Japan", "G": "Iran", "H": "Uruguay", "I": "France", "J": "Austria", "K": "Colombia", "L": "Paraguay"}
    df_mock = pd.DataFrame([
        {"Group": "F", "Team": "Sweden", "Points": 4, "GD": 0, "GF": 6}, {"Group": "E", "Team": "Ecuador", "Points": 4, "GD": 0, "GF": 2},
        {"Group": "B", "Team": "Bosnia-H.", "Points": 4, "GD": -1, "GF": 5}, {"Group": "L", "Team": "Croatia", "Points": 3, "GD": -1, "GF": 3},
        {"Group": "A", "Team": "Korea Republic", "Points": 3, "GD": -1, "GF": 2}, {"Group": "D", "Team": "Paraguay", "Points": 3, "GD": -2, "GF": 2},
        {"Group": "J", "Team": "Algeria", "Points": 3, "GD": -2, "GF": 2}, {"Group": "C", "Team": "Scotland", "Points": 3, "GD": -3, "GF": 1},
        {"Group": "H", "Team": "Cape Verde", "Points": 2, "GD": 0, "GF": 2}, {"Group": "G", "Team": "Belgium", "Points": 2, "GD": 0, "GF": 1},
        {"Group": "K", "Team": "Congo DR", "Points": 1, "GD": -1, "GF": 1}, {"Group": "I", "Team": "Senegal", "Points": 0, "GD": -3, "GF": 3}
    ])
    df_mock["Rank"] = df_mock.index + 1
    return w, r, df_mock

# ==========================================
# DATA INGESTION & PIPELINE SETUP
# ==========================================
fetch_res = fetch_bracket_data()

# Absolutely ensure variables are unpacked correctly regardless of live or fallback state
if fetch_res and len(fetch_res) == 3:
    winners, runners_up, df_3rd = fetch_res
else:
    # Safe immediate emergency definition if the data structure gets corrupted
    winners, runners_up = {}, {}
    df_3rd = pd.DataFrame(columns=["Rank", "Group", "Team", "Points", "GD", "GF"])

# Fallback mechanism if df_3rd is empty or missing columns
if df_3rd is None or df_3rd.empty or "Rank" not in df_3rd.columns:
    df_3rd = pd.DataFrame([
        {"Group": "F", "Team": "Sweden", "Points": 4, "GD": 0, "GF": 6},
        {"Group": "E", "Team": "Ecuador", "Points": 4, "GD": 0, "GF": 2},
        {"Group": "B", "Team": "Bosnia-H.", "Points": 4, "GD": -1, "GF": 5},
        {"Group": "L", "Team": "Croatia", "Points": 3, "GD": -1, "GF": 3},
        {"Group": "A", "Team": "Korea Republic", "Points": 3, "GD": -1, "GF": 2},
        {"Group": "D", "Team": "Paraguay", "Points": 3, "GD": -2, "GF": 2},
        {"Group": "J", "Team": "Algeria", "Points": 3, "GD": -2, "GF": 2},
        {"Group": "C", "Team": "Scotland", "Points": 3, "GD": -3, "GF": 1}
    ])
    df_3rd["Rank"] = df_3rd.index + 1

df_3rd["Status"] = ["🟢 Qualified" if r <= 8 else "🔴 Eliminated" for r in df_3rd["Rank"]]

# Safely extract the top 8 teams for the bracket mapping
top_8 = df_3rd[df_3rd["Rank"] <= 8].copy()

# ==========================================
# DYNAMIC 3RD-PLACE ALLOCATION ENGINE
# ==========================================
# Create a valid list of dictionaries to draw from sequentially without matching errors
available_3rd = top_8.sort_values(by="Rank").to_dict(orientation="records")

def get_live_3rd(preferred_groups):
    # 1. Look for the highest-ranked available team matching preferred groups
    for team_record in available_3rd:
        if team_record["Group"] in preferred_groups:
            available_3rd.remove(team_record)
            return team_record["Team"]
            
    # 2. Live Fallback: Grab the best ranked team remaining in the pool
    if available_3rd:
        next_best = available_3rd.pop(0)
        return next_best["Team"]
        
    return "TBD"

# Run allocation sequences smoothly
m74_3rd = get_live_3rd(['A','B','C','D','F'])
m77_3rd = get_live_3rd(['C','D','F','G','H'])
m79_3rd = get_live_3rd(['C','E','F','H','I'])
m80_3rd = get_live_3rd(['E','H','I','J','K'])
m82_3rd = get_live_3rd(['A','E','H','I','J'])
m81_3rd = get_live_3rd(['B','E','F','I','J'])
m87_3rd = get_live_3rd(['D','E','I','J','L'])
m85_3rd = get_live_3rd(['E','F','G','I','J'])
