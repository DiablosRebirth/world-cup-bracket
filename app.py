@st.cache_data(ttl=60) # Set to 1 minute for live tournament tracking
def fetch_bracket_data():
    try:
        response = requests.get(API_URL, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        winners, runners_up, third_places = {}, {}, []
        
        for group_data in data.get("standings", []):
            raw_group = group_data.get("group", "")
            g = raw_group.replace("Group ", "").replace("GROUP_", "").strip()
            if not g:
                continue
                
            table = group_data.get("table", [])
            if len(table) >= 1: 
                winners[g] = table[0]["team"]["shortName"]
            if len(table) >= 2: 
                runners_up[g] = table[1]["team"]["shortName"]
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
        # Gracefully log the live warning in the sidebar without halting execution
        st.sidebar.warning(f"🔄 Running on Bracket Fallback: {e}")

    # --- SOLID FALLBACK DATASET ---
    # This guarantees the app ALWAYS has data to load even if the API throws a wrench
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
winners, runners_up, df_3rd = fetch_bracket_data()

# Absolute safety check: If df_3rd is completely missing or empty, build an empty fallback shell 
if df_3rd is None or df_3rd.empty:
    df_3rd = pd.DataFrame(columns=["Rank", "Group", "Team", "Points", "GD", "GF"])

df_3rd["Status"] = ["🟢 Qualified" if r <= 8 else "🔴 Eliminated" for r in df_3rd["Rank"]]
top_8 = df_3rd[df_3rd["Rank"] <= 8]
t3 = dict(zip(top_8["Group"], top_8["Team"]))
t3_orig = t3.copy()
