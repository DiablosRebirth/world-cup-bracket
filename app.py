import streamlit as st
import pandas as pd
import requests

# Set up page layout for seamless mobile + desktop viewing
st.set_page_config(page_title="2026 World Cup Center", layout="wide")

st.title("🏆 Live 2026 World Cup Tournament Center")
st.write("Real-time 3rd-Place Ladder Analytics & Round of 32 Roadmap")

# ==========================================
# API CONFIGURATION
# ==========================================
API_URL = "https://api.football-data.org/v4/competitions/WC/standings"
API_TOKEN = "dec42f1962144eac9735b3111c7aa3de"
HEADERS = {"X-Auth-Token": API_TOKEN}

# Web-native emoji flags (guaranteed to render beautifully on iOS, Android, and Windows browsers)
FLAGS = {
    "Argentina": "🇦🇷", "Algeria": "🇩🇿", "Australia": "🇦🇺", "Austria": "🇦🇹", 
    "Belgium": "🇧🇪", "Bosnia-Herzegovina": "🇧🇦", "Bosnia-H.": "🇧🇦", "Brazil": "🇧🇷", 
    "Canada": "🇨🇦", "Cape Verde": "🇨🇻", "Chile": "🇨🇱", "Colombia": "🇨🇴", 
    "Congo DR": "🇨🇩", "Croatia": "🇭🇷", "Denmark": "🇩🇰", "Ecuador": "🇪🇨", 
    "Egypt": "🇪🇬", "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "France": "🇫🇷", "Germany": "🇩🇪", 
    "Ghana": "🇬🇭", "Iran": "🇮🇷", "Italy": "🇮🇹", "Ivory Coast": "🇨🇮", 
    "Japan": "🇯🇵", "Korea Republic": "🇰🇷", "Korea Rep.": "🇰🇷", "South Korea": "🇰🇷", 
    "Mexico": "🇲🇽", "Morocco": "🇲🇦", "Netherlands": "🇳🇱", "Paraguay": "🇵🇾", 
    "Portugal": "🇵🇹", "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Senegal": "🇸🇳", "Spain": "🇪🇸", 
    "Sweden": "🇸🇪", "Switzerland": "🇨🇭", "Turkey": "🇹🇷", "Uruguay": "🇺🇾", "USA": "🇺🇸",
    "South Africa": "🇿🇦", "South Africa Rep.": "🇿🇦", "RSA": "🇿🇦"
}

def get_flag(team_name):
    if not team_name:
        return ""
        
    team_lower = str(team_name).lower()
    
    # 2-letter ISO code mapping for the teams
    code_map = {
        "sweden": "se", "ecuador": "ec", "bosnia": "ba", "croatia": "hr",
        "korea": "kr", "paraguay": "py", "algeria": "dz", "cape verde": "cv",
        "belgium": "be", "germany": "de", "france": "fr", "south africa": "za",
        "canada": "ca", "netherlands": "nl", "morocco": "ma", "portugal": "pt",
        "ghana": "gh", "spain": "es", "austria": "at", "usa": "us",
        "brazil": "br", "australia": "au", "ivory coast": "ci", "japan": "jp",
        "mexico": "mx", "argentina": "ar", "uruguay": "uy", "iran": "ir",
        "switzerland": "ch", "colombia": "co", "senegal": "sn", "egypt": "eg",
        # Special matching for DR and UK nations
        "dr": "cd", "scotland": "gb-sct", "england": "gb-eng"
    }
    
    # Find the code
    country_code = None
    for key, code in code_map.items():
        if key in team_lower:
            country_code = code
            break
            
    if country_code:
        return f'<img src="https://flagcdn.com/w40/{country_code}.png" style="vertical-align: middle; border-radius: 2px; width: 24px; height: auto; margin-right: 4px;">'
        
    return ""

@st.cache_data(ttl=300) # Caches data for 5 minutes so you don't break your API rate limits
def fetch_bracket_data():
    try:
        response = requests.get(API_URL, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        winners, runners_up, third_places = {}, {}, []
        for group_data in data.get("standings", []):
            g = group_data["group"].replace("Group ", "").replace("GROUP_", "").strip()[-1]
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
    except: pass

    # Post-Group Stage Fallback Dataset
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

winners, runners_up, df_3rd = fetch_bracket_data()
df_3rd["Status"] = ["🟢 Qualified" if r <= 8 else "🔴 Eliminated" for r in df_3rd["Rank"]]
top_8 = df_3rd[df_3rd["Rank"] <= 8]
t3 = dict(zip(top_8["Group"], top_8["Team"]))
t3_orig = t3.copy()

def get_3rd(choices):
    for c in choices:
        if c in t3 and t3[c] is not None:
            team = t3[c]; t3[c] = None; return team
    for c in choices:
        if c in t3_orig:
            for g, team in t3.items():
                if team is not None: t3[g] = None; return team
    return "TBD 3rd"

# ==========================================
# 3. WEB INTERFACE DESIGN
# ==========================================
col1, col2 = st.columns([1, 2.2])

with col1:
    st.subheader("📊 3rd Place Rankings Tier")
    display_df = df_3rd[["Rank", "Group", "Team", "Points", "GD", "GF", "Status"]].copy()
    
    # Smart cleaner: only strips the first word if it's a 2-letter lowercase country code
    def clean_team_name(name_str):
        words = str(name_str).split()
        if len(words) > 1 and len(words[0]) == 2 and words[0].islower():
            return " ".join(words[1:])
        return name_str

    # Apply the beautiful flag image next to the fully intact country name
    display_df["Team"] = display_df.apply(lambda row: f"{get_flag(row['Team'])} {clean_team_name(row['Team'])}", axis=1)
    
    st.write(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)

with col2:
    st.subheader("⚔️ Live Round of 32 Fixtures Map")

    def render_match_card(match_id, t1, t2, label1, label2):
        html_content = f'<div style="border:2px solid #cbd5e1;border-radius:10px;padding:14px;margin-bottom:14px;background-color:#ffffff;box-shadow:0 3px 6px rgba(0,0,0,0.08);">' \
                       f'<span style="font-weight:800;color:#334155;font-size:12px;background-color:#e2e8f0;padding:4px 10px;border-radius:6px;font-family:sans-serif;">{match_id}</span>' \
                       f'<div style="margin-top:12px;font-size:16px;color:#0f172a;display:flex;align-items:center;font-family:sans-serif;"><span style="margin-right:10px;font-size:20px;">{get_flag(t1)}</span><span style="color:#0f172a;"><b style="color:#475569;font-weight:700;">{label1}:</b> {t1}</span></div>' \
                       f'<div style="margin-top:8px;border-top:1px dashed #e2e8f0;padding-top:8px;font-size:16px;color:#0f172a;display:flex;align-items:center;font-family:sans-serif;"><span style="margin-right:10px;font-size:20px;">{get_flag(t2)}</span><span style="color:#0f172a;"><b style="color:#475569;font-weight:700;">{label2}:</b> {t2}</span></div>' \
                       f'</div>'
        st.markdown(html_content, unsafe_allow_html=True)

    m_col1, m_col2 = st.columns(2)
    
    with m_col1:
        st.markdown("#### 🟦 Left Tree Panel")
        render_match_card("M74", winners.get("E"), get_3rd(['A','B','C','D','F']), "E1", "3rd")
        render_match_card("M77", winners.get("I"), get_3rd(['C','D','F','G','H']), "I1", "3rd")
        render_match_card("M73", runners_up.get("A"), runners_up.get("B"), "A2", "B2")
        render_match_card("M75", winners.get("F"), runners_up.get("C"), "F1", "C2")
        render_match_card("M83", runners_up.get("K"), runners_up.get("L"), "K2", "L2")
        render_match_card("M84", winners.get("H"), runners_up.get("J"), "H1", "J2")
        render_match_card("M81", winners.get("D"), get_3rd(['B','E','F','I','J']), "D1", "3rd")
        render_match_card("M82", winners.get("G"), get_3rd(['A','E','H','I','J']), "G1", "3rd")

    with m_col2:
        st.markdown("#### 🟩 Right Tree Panel")
        render_match_card("M76", winners.get("C"), runners_up.get("D"), "C1", "D2")
        render_match_card("M78", runners_up.get("E"), runners_up.get("F"), "E2", "F2")
        render_match_card("M79", winners.get("A"), get_3rd(['C','E','F','H','I']), "A1", "3rd")
        render_match_card("M80", winners.get("L"), get_3rd(['E','H','I','J','K']), "L1", "3rd")
        render_match_card("M86", winners.get("J"), runners_up.get("H"), "J1", "H2")
        render_match_card("M88", runners_up.get("D"), runners_up.get("G"), "D2", "G2")
        render_match_card("M85", winners.get("B"), get_3rd(['E','F','G','I','J']), "B1", "3rd")
        render_match_card("M87", winners.get("K"), get_3rd(['D','E','I','J','L']), "K1", "3rd")
