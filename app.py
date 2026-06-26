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

    # Solid Global Fallbacks (Static text snapshot if API is completely unreachable)
    w = {"A": "Mexico", "B": "Switzerland", "C": "Brazil", "D": "USA", "E": "Germany", "F": "Netherlands", "G": "Egypt", "H": "Spain", "I": "France", "J": "Argentina", "K": "Portugal", "L": "England"}
    r = {"A": "South Africa", "B": "Canada", "C": "Morocco", "D": "Australia", "E": "Ivory Coast", "F": "Japan", "G": "Iran", "H": "Uruguay", "I": "Norway", "J": "Austria", "K": "Colombia", "L": "Ghana"}
    df_mock = pd.DataFrame([
        {"Group": "A", "Team": "South Korea", "Points": 4, "GD": 1, "GF": 4},
        {"Group": "C", "Team": "Scotland", "Points": 4, "GD": 0, "GF": 3},
        {"Group": "F", "Team": "Sweden", "Points": 4, "GD": 0, "GF": 2},
        {"Group": "L", "Team": "Ecuador", "Points": 3, "GD": 1, "GF": 5},
        {"Group": "B", "Team": "Bosnia-H.", "Points": 3, "GD": 0, "GF": 3},
        {"Group": "D", "Team": "Paraguay", "Points": 3, "GD": -1, "GF": 2},
        {"Group": "J", "Team": "Algeria", "Points": 3, "GD": -1, "GF": 2},
        {"Group": "K", "Team": "Croatia", "Points": 3, "GD": -2, "GF": 1}
    ])
    df_mock["Rank"] = df_mock.index + 1
    return w, r, df_mock

# ==========================================
# DATA INGESTION & PIPELINE SETUP
# ==========================================
fetch_res = fetch_bracket_data()

# Absolute validation guard: Unpack cleanly or load whole structural fallback at once
if fetch_res and len(fetch_res) == 3 and fetch_res[2] is not None:
    winners, runners_up, df_3rd = fetch_res
else:
    winners = {"A": "Mexico", "B": "Switzerland", "C": "Brazil", "D": "USA", "E": "Germany", "F": "Netherlands", "G": "Egypt", "H": "Spain", "I": "France", "J": "Argentina", "K": "Portugal", "L": "England"}
    runners_up = {"A": "South Africa", "B": "Canada", "C": "Morocco", "D": "Australia", "E": "Ivory Coast", "F": "Japan", "G": "Iran", "H": "Uruguay", "I": "Norway", "J": "Austria", "K": "Colombia", "L": "Ghana"}
    df_3rd = pd.DataFrame([
        {"Group": "A", "Team": "South Korea", "Points": 4, "GD": 1, "GF": 4},
        {"Group": "C", "Team": "Scotland", "Points": 4, "GD": 0, "GF": 3},
        {"Group": "F", "Team": "Sweden", "Points": 4, "GD": 0, "GF": 2},
        {"Group": "L", "Team": "Ecuador", "Points": 3, "GD": 1, "GF": 5},
        {"Group": "B", "Team": "Bosnia-H.", "Points": 3, "GD": 0, "GF": 3},
        {"Group": "D", "Team": "Paraguay", "Points": 3, "GD": -1, "GF": 2},
        {"Group": "J", "Team": "Algeria", "Points": 3, "GD": -1, "GF": 2},
        {"Group": "K", "Team": "Croatia", "Points": 3, "GD": -2, "GF": 1}
    ])
    df_3rd["Rank"] = df_3rd.index + 1

df_3rd["Status"] = ["🟢 Qualified" if r <= 8 else "🔴 Eliminated" for r in df_3rd["Rank"]]
top_8 = df_3rd[df_3rd["Rank"] <= 8].copy()

# ==========================================
# DYNAMIC 3RD-PLACE ALLOCATION ENGINE
# ==========================================
available_3rd = top_8.sort_values(by="Rank").to_dict(orientation="records")

def get_live_3rd(preferred_groups):
    for team_record in available_3rd:
        if team_record["Group"] in preferred_groups:
            available_3rd.remove(team_record)
            return team_record["Team"]
            
    if available_3rd:
        next_best = available_3rd.pop(0)
        return next_best["Team"]
    return "TBD"

# Calculate arrays linearly without structural leaks
m74_3rd = get_live_3rd(['A','B','C','D','F'])
m77_3rd = get_live_3rd(['C','D','F','G','H'])
m79_3rd = get_live_3rd(['C','E','F','H','I'])
m80_3rd = get_live_3rd(['E','H','I','J','K'])
m82_3rd = get_live_3rd(['A','E','H','I','J'])
m81_3rd = get_live_3rd(['B','E','F','I','J'])
m87_3rd = get_live_3rd(['D','E','I','J','L'])
m85_3rd = get_live_3rd(['E','F','G','I','J'])

# ==========================================
# 3. WEB INTERFACE DESIGN
# ==========================================
col1, col2 = st.columns([1, 2.2])

name_replacements = {
    "congo dr": "DR Congo",
    "korea republic": "South Korea",
    "cengo dr": "DR Congo"
}

def clean_team_name(name_str):
    if not name_str or str(name_str).lower() == "none":
        return "TBD"
    words = str(name_str).split()
    if len(words) > 1 and len(words[0]) == 2 and words[0].islower():
        name_str = " ".join(words[1:])
    return name_replacements.get(name_str.lower(), name_str)

with col1:
    st.subheader("📊 3rd Place Rankings Tier")
    display_df = df_3rd[["Rank", "Group", "Team", "Points", "GD", "GF", "Status"]].copy()
    display_df["Team"] = display_df.apply(lambda row: f"{get_flag(row['Team'])} {clean_team_name(row['Team'])}", axis=1)
    st.write(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)

with col2:
    st.subheader("⚔️ Live Round of 32 Fixtures Map")

    def render_match_card(match_id, t1, t2, label1, label2):
        clean_t1 = clean_team_name(t1)
        clean_t2 = clean_team_name(t2)

        html_content = f'<div style="border:2px solid #cbd5e1;border-radius:10px;padding:14px;margin-bottom:14px;background-color:#ffffff;box-shadow:0 3px 6px rgba(0,0,0,0.08);">' \
                       f'<span style="font-weight:800;color:#334155;font-size:12px;background-color:#e2e8f0;padding:4px 10px;border-radius:6px;font-family:sans-serif;">{match_id}</span>' \
                       f'<div style="margin-top:12px;font-size:16px;color:#0f172a;display:flex;align-items:center;font-family:sans-serif;"><span style="margin-right:10px;font-size:20px;">{get_flag(t1)}</span><span style="color:#0f172a;"><b style="color:#475569;font-weight:700;">{label1}:</b> {clean_t1}</span></div>' \
                       f'<div style="margin-top:8px;border-top:1px dashed #e2e8f0;padding-top:8px;font-size:16px;color:#0f172a;display:flex;align-items:center;font-family:sans-serif;"><span style="margin-right:10px;font-size:20px;">{get_flag(t2)}</span><span style="color:#0f172a;"><b style="color:#475569;font-weight:700;">{label2}:</b> {clean_t2}</span></div>' \
                       f'</div>'
        st.markdown(html_content, unsafe_allow_html=True)

    m_col1, m_col2 = st.columns(2)
    
    with m_col1:
        st.markdown("#### 🟦 Left Tree Panel")
        render_match_card("M73", runners_up.get("A"), runners_up.get("B"), "A2", "B2")
        render_match_card("M75", winners.get("F"), runners_up.get("C"), "F1", "C2")
        render_match_card("M74", winners.get("E"), m74_3rd, "E1", "3rd")
        render_match_card("M77", winners.get("I"), m77_3rd, "I1", "3rd")
        render_match_card("M83", runners_up.get("K"), runners_up.get("L"), "K2", "L2")
        render_match_card("M84", winners.get("H"), runners_up.get("J"), "H1", "J2")
        render_match_card("M81", winners.get("D"), m81_3rd, "D1", "3rd")
        render_match_card("M82", winners.get("G"), m82_3rd, "G1", "3rd")

    with m_col2:
        st.markdown("#### 🟩 Right Tree Panel")
        render_match_card("M76", winners.get("C"), runners_up.get("F"), "C1", "F2")
        render_match_card("M78", runners_up.get("E"), runners_up.get("I"), "E2", "I2")
        render_match_card("M79", winners.get("A"), m79_3rd, "A1", "3rd")
        render_match_card("M80", winners.get("L"), m80_3rd, "L1", "3rd")
        render_match_card("M86", winners.get("J"), runners_up.get("H"), "J1", "H2")
        render_match_card("M88", runners_up.get("D"), runners_up.get("G"), "D2", "G2")
        render_match_card("M85", winners.get("B"), m85_3rd, "B1", "3rd")
        render_match_card("M87", winners.get("K"), m87_3rd, "K1", "3rd")
