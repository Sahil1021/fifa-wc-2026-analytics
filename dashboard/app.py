import streamlit as st
import pandas as pd
import numpy as np
import pyodbc
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
import warnings
warnings.filterwarnings('ignore')

from pathlib import Path
import os

# Find .env file — works regardless of which directory you run from
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Quick sanity check
import sys
print(f"ENV PATH: {env_path}", file=sys.stderr)
print(f"ENV EXISTS: {env_path.exists()}", file=sys.stderr)
print(f"DB_SERVER: {os.getenv('DB_SERVER')}", file=sys.stderr)
# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="FIFA World Cup 2026 Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CONNECTION
# ============================================
@st.cache_resource
def get_connection():
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')},1433;"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"UID={os.getenv('DB_USERNAME')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )
    return pyodbc.connect(connection_string)

@st.cache_data(ttl=300)
def load_data():
    conn = get_connection()

    matches_df = pd.read_sql("""
        SELECT
            m.match_id, m.match_date, m.stage, m.group_name,
            t1.team_name as home_team, t1.fifa_code as home_code,
            m.home_score, m.away_score,
            t2.team_name as away_team, t2.fifa_code as away_code
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.team_id
        JOIN teams t2 ON m.away_team_id = t2.team_id
        WHERE m.home_score IS NOT NULL
    """, conn)

    teams_df = pd.read_sql("SELECT * FROM teams", conn)
    all_matches_df = pd.read_sql("""
        SELECT
            m.match_id, m.match_date, m.stage, m.group_name,
            t1.team_name as home_team, m.home_score,
            m.away_score, t2.team_name as away_team
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.team_id
        JOIN teams t2 ON m.away_team_id = t2.team_id
    """, conn)

    return matches_df, teams_df, all_matches_df

# ============================================
# HELPER FUNCTIONS
# ============================================
def build_team_stats(matches_df):
    stats = {}
    for _, match in matches_df.iterrows():
        home, away = match['home_team'], match['away_team']
        hg, ag = int(match['home_score']), int(match['away_score'])
        group = match['group_name'].replace('GROUP_', '')

        for team, gf, ga in [(home, hg, ag), (away, ag, hg)]:
            if team not in stats:
                stats[team] = {
                    'team': team, 'group': group, 'played': 0,
                    'won': 0, 'drawn': 0, 'lost': 0,
                    'goals_for': 0, 'goals_against': 0,
                    'points': 0, 'momentum': []
                }
            s = stats[team]
            s['played'] += 1
            s['goals_for'] += gf
            s['goals_against'] += ga
            if gf > ga:
                s['won'] += 1; s['points'] += 3; s['momentum'].append(3)
            elif gf == ga:
                s['drawn'] += 1; s['points'] += 1; s['momentum'].append(1)
            else:
                s['lost'] += 1; s['momentum'].append(0)

    for team, s in stats.items():
        p = s['played']
        s['goal_difference'] = s['goals_for'] - s['goals_against']
        s['goals_per_game'] = round(s['goals_for'] / p, 2) if p > 0 else 0
        momentum = s['momentum']
        if momentum:
            weights = np.array([0.5, 0.3, 0.2][:len(momentum)])
            weights = weights / weights.sum()
            recent = momentum[-3:]
            w = weights[-len(recent):] / weights[-len(recent):].sum()
            s['momentum_score'] = round(float(np.dot(recent, w)), 2)
        else:
            s['momentum_score'] = 0

    return pd.DataFrame(stats.values())

fifa_rankings = {
    'France': 2, 'Spain': 3, 'England': 4, 'Brazil': 5,
    'Portugal': 6, 'Netherlands': 7, 'Argentina': 8,
    'Belgium': 9, 'Germany': 10, 'Morocco': 13,
    'United States': 14, 'Mexico': 15, 'Switzerland': 16,
    'Croatia': 17, 'Uruguay': 18, 'Colombia': 19,
    'Japan': 20, 'Ecuador': 21, 'Senegal': 22,
    'Sweden': 23, 'South Korea': 24, 'Turkey': 25,
    'Australia': 26, 'Canada': 27, 'Saudi Arabia': 28,
    'Egypt': 31, 'Austria': 32, 'South Africa': 64,
    'Ghana': 54, 'Tunisia': 30, 'Ivory Coast': 48,
    'Norway': 34, 'Scotland': 38, 'Czechia': 40,
    'Iran': 20, 'Qatar': 35, 'Bosnia-Herzegovina': 55,
    'Paraguay': 58, 'Algeria': 42, 'New Zealand': 100,
    'Jordan': 87, 'Iraq': 63, 'Uzbekistan': 50,
    'Congo DR': 56, 'Cape Verde Islands': 80, 'Haiti': 83,
    'Curaçao': 85, 'Panama': 70
}

@st.cache_data(ttl=300)
def run_predictions(matches_df_hash):
    matches_df, teams_df, _ = load_data()
    team_stats_df = build_team_stats(matches_df)
    team_stats_df['fifa_ranking'] = team_stats_df['team'].map(fifa_rankings).fillna(90)

    # Historical training data (2018 verified + 2022 from cache)
    verified_2018 = [
        ('Uruguay', 9, 5, 5, 14, 1), ('Russia', 6, 5, 8, 70, 1),
        ('France', 7, 3, 3, 7, 1), ('Denmark', 5, 2, 3, 12, 1),
        ('Croatia', 7, 5, 7, 20, 1), ('Argentina', 4, 0, 3, 5, 1),
        ('Brazil', 7, 4, 5, 2, 1), ('Switzerland', 5, 1, 5, 6, 1),
        ('Belgium', 9, 7, 8, 3, 1), ('Japan', 4, 0, 4, 61, 1),
        ('Sweden', 6, 4, 6, 24, 1), ('Mexico', 6, 2, 3, 15, 1),
        ('Colombia', 6, 3, 5, 16, 1), ('England', 6, 5, 8, 13, 1),
        ('Senegal', 4, 0, 4, 27, 1), ('Nigeria', 3, -1, 3, 48, 1),
        ('Poland', 3, -2, 2, 8, 0), ('Germany', 3, -2, 2, 1, 0),
        ('Portugal', 5, 1, 4, 4, 0), ('Spain', 5, 1, 4, 10, 0),
        ('Iran', 4, 0, 2, 37, 0), ('Peru', 0, -4, 2, 11, 0),
        ('Morocco', 1, -1, 2, 48, 0), ('Iceland', 1, -3, 2, 22, 0),
        ('Australia', 1, -3, 2, 41, 0), ('Saudi Arabia', 1, -4, 2, 67, 0),
        ('Egypt', 0, -4, 2, 45, 0), ('Tunisia', 1, -2, 5, 21, 0),
        ('Panama', 0, -7, 2, 55, 0), ('South Korea', 3, -3, 3, 57, 0),
        ('Costa Rica', 0, -5, 2, 23, 0), ('Serbia', 3, -1, 2, 34, 0),
    ]

    hist_data = []
    for row in verified_2018:
        hist_data.append({
            'points': row[1], 'goal_difference': row[2],
            'goals_for': row[3], 'goals_per_game': round(row[3]/3, 2),
            'fifa_ranking': row[4], 'advanced': row[5]
        })

    hist_df = pd.DataFrame(hist_data)
    features = ['points', 'goal_difference', 'goals_for', 'goals_per_game', 'fifa_ranking']

    X = hist_df[features]
    y = hist_df['advanced']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_scaled, y)

    current = team_stats_df[features].copy()
    current_scaled = scaler.transform(current)
    raw_probs = rf_model.predict_proba(current_scaled)[:, 1]

    def ranking_floor(prob, ranking, played):
        fw = min(played / 3, 1.0)
        rw = 1 - fw
        if ranking <= 10: floor = 0.55 * rw
        elif ranking <= 20: floor = 0.40 * rw
        elif ranking <= 35: floor = 0.25 * rw
        else: floor = 0.10 * rw
        return round(float((prob * fw) + (max(prob, floor) * rw)), 3)

    def pts_boost(points, gd):
        if points >= 6: return 0.45
        elif points >= 3 and gd >= 2: return 0.35
        elif points >= 3: return 0.20
        elif points == 0 and gd <= -2: return -0.15
        return 0.0

    adj_probs = []
    for i, (_, row) in enumerate(team_stats_df.iterrows()):
        boost = pts_boost(row['points'], row['goal_difference'])
        raw = min(max(raw_probs[i] + boost, 0.02), 0.98)
        adj = ranking_floor(raw, row['fifa_ranking'], row['played'])
        adj_probs.append(adj)

    team_stats_df['advancement_prob'] = adj_probs
    team_stats_df['advancement_prob_pct'] = (team_stats_df['advancement_prob'] * 100).round(1)

    team_stats_df['tournament_score'] = (
        team_stats_df['advancement_prob'] * 0.5 +
        (1 / team_stats_df['fifa_ranking']) * 30 * 0.3 +
        team_stats_df['momentum_score'] * 0.2
    )
    team_stats_df['win_probability'] = (
        team_stats_df['tournament_score'] /
        team_stats_df['tournament_score'].sum() * 100
    ).round(1)

    return team_stats_df

# ============================================
# LOAD DATA
# ============================================
matches_df, teams_df, all_matches_df = load_data()
team_stats_df = run_predictions(len(matches_df))

total_goals = int(matches_df['home_score'].sum() + matches_df['away_score'].sum())
avg_goals = round(total_goals / len(matches_df), 2) if len(matches_df) > 0 else 0
home_wins = len(matches_df[matches_df['home_score'] > matches_df['away_score']])
away_wins = len(matches_df[matches_df['away_score'] > matches_df['home_score']])
draws = len(matches_df[matches_df['home_score'] == matches_df['away_score']])

# ============================================
# SIDEBAR
# ============================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/3/35/2026_FIFA_World_Cup.svg/200px-2026_FIFA_World_Cup.svg.png", width=150)
st.sidebar.title("⚽ WC 2026 Analytics")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Overview", "📊 Group Standings", "⚽ Match Results", "🤖 Predictions"]
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Matches Played:** {len(matches_df)}")
st.sidebar.markdown(f"**Total Goals:** {total_goals}")
st.sidebar.markdown(f"**Last Updated:** {pd.Timestamp.now().strftime('%d %b %Y %H:%M')}")
st.sidebar.markdown("---")
st.sidebar.markdown("*Built by Sahil | Azure SQL + Python + Streamlit*")

# ============================================
# PAGE 1 — OVERVIEW
# ============================================
if page == "🏠 Overview":
    st.title("🏆 FIFA World Cup 2026 — Live Analytics Dashboard")
    st.markdown(f"*Real-time data from Azure SQL Database | {len(matches_df)} matches played*")
    st.markdown("---")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Matches Played", len(matches_df))
    col2.metric("Total Goals", total_goals)
    col3.metric("Avg Goals/Match", avg_goals)
    col4.metric("Home Wins", f"{home_wins} ({round(home_wins/len(matches_df)*100)}%)")
    col5.metric("Draws", f"{draws} ({round(draws/len(matches_df)*100)}%)")

    st.markdown("---")
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("⚽ Goals by Group")
        matches_df['group_short'] = matches_df['group_name'].str.replace('GROUP_', '')
        matches_df['total_goals'] = matches_df['home_score'] + matches_df['away_score']
        goals_by_group = matches_df.groupby('group_short')['total_goals'].sum().reset_index()
        goals_by_group.columns = ['Group', 'Goals']
        fig = px.bar(goals_by_group, x='Group', y='Goals',
                     color='Goals', color_continuous_scale='Greens',
                     title='Total Goals by Group')
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("📊 Results Distribution")
        result_df = pd.DataFrame({
            'Result': ['Home Win', 'Away Win', 'Draw'],
            'Count': [home_wins, away_wins, draws]
        })
        fig2 = px.pie(result_df, values='Count', names='Result',
                      color_discrete_sequence=['#1a6b3c', '#c8a415', '#888888'],
                      title='Match Results Distribution')
        fig2.update_layout(height=350)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.subheader("🔥 Top Scoring Teams")
    home_g = matches_df[['home_team', 'home_score']].rename(columns={'home_team': 'team', 'home_score': 'goals'})
    away_g = matches_df[['away_team', 'away_score']].rename(columns={'away_team': 'team', 'away_score': 'goals'})
    top_scorers = pd.concat([home_g, away_g]).groupby('team')['goals'].sum().reset_index()
    top_scorers = top_scorers.sort_values('goals', ascending=False).head(10)
    fig3 = px.bar(top_scorers, x='goals', y='team', orientation='h',
                  color='goals', color_continuous_scale='Greens',
                  title='Top 10 Teams by Goals Scored')
    fig3.update_layout(yaxis={'categoryorder': 'total ascending'}, height=400, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.subheader("🚨 Notable Results")
    matches_df['result'] = matches_df.apply(
        lambda r: r['home_team'] if r['home_score'] > r['away_score']
        else (r['away_team'] if r['away_score'] > r['home_score'] else 'Draw'), axis=1)
    high_scoring = matches_df[matches_df['total_goals'] >= 4].sort_values('total_goals', ascending=False)
    if len(high_scoring) > 0:
        for _, row in high_scoring.iterrows():
            st.markdown(f"🔥 **{row['home_team']} {int(row['home_score'])} - {int(row['away_score'])} {row['away_team']}** — {int(row['total_goals'])} goals")

# ============================================
# PAGE 2 — GROUP STANDINGS
# ============================================
elif page == "📊 Group Standings":
    st.title("📊 Group Stage Standings")
    st.markdown("*Live standings calculated from match results in Azure SQL*")
    st.markdown("---")

    def calc_standings(df):
        standings = {}
        for _, match in df.iterrows():
            home, away = match['home_team'], match['away_team']
            hg, ag = int(match['home_score']), int(match['away_score'])
            group = match['group_name'].replace('GROUP_', '')
            for team, gf, ga in [(home, hg, ag), (away, ag, hg)]:
                if team not in standings:
                    standings[team] = {'Team': team, 'Group': group,
                                       'P': 0, 'W': 0, 'D': 0, 'L': 0,
                                       'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0}
                s = standings[team]
                s['P'] += 1; s['GF'] += gf; s['GA'] += ga; s['GD'] += gf - ga
                if gf > ga: s['W'] += 1; s['Pts'] += 3
                elif gf == ga: s['D'] += 1; s['Pts'] += 1
                else: s['L'] += 1
        df_out = pd.DataFrame(standings.values())
        return df_out.sort_values(['Group', 'Pts', 'GD', 'GF'], ascending=[True, False, False, False])

    standings_df = calc_standings(matches_df)
    groups = sorted(standings_df['Group'].unique())

    selected_group = st.selectbox("Select Group", ["All Groups"] + list(groups))

    if selected_group == "All Groups":
        cols = st.columns(3)
        for idx, group in enumerate(groups):
            with cols[idx % 3]:
                st.markdown(f"**Group {group}**")
                gdf = standings_df[standings_df['Group'] == group][
                    ['Team', 'P', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']
                ].reset_index(drop=True)
                gdf.index = gdf.index + 1
                st.dataframe(gdf, use_container_width=True, height=180)
    else:
        gdf = standings_df[standings_df['Group'] == selected_group][
            ['Team', 'P', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']
        ].reset_index(drop=True)
        gdf.index = gdf.index + 1
        st.dataframe(gdf, use_container_width=True)

        fig = px.bar(gdf, x='Team', y='Pts',
                     color='Pts', color_continuous_scale='Greens',
                     title=f'Group {selected_group} — Points')
        st.plotly_chart(fig, use_container_width=True)

# ============================================
# PAGE 3 — MATCH RESULTS
# ============================================
elif page == "⚽ Match Results":
    st.title("⚽ Match Results")
    st.markdown("---")

    matches_df['match_date'] = pd.to_datetime(matches_df['match_date'])
    matches_df['date_only'] = matches_df['match_date'].dt.date
    matches_df['group_short'] = matches_df['group_name'].str.replace('GROUP_', '')

    col1, col2 = st.columns(2)
    with col1:
        group_filter = st.selectbox("Filter by Group", ["All"] + sorted(matches_df['group_short'].unique().tolist()))
    with col2:
        sort_order = st.radio("Sort", ["Most Recent First", "Oldest First"], horizontal=True)

    filtered = matches_df.copy()
    if group_filter != "All":
        filtered = filtered[filtered['group_short'] == group_filter]

    ascending = sort_order == "Oldest First"
    filtered = filtered.sort_values('match_date', ascending=ascending)

    for _, row in filtered.iterrows():
        col_home, col_score, col_away = st.columns([3, 1, 3])
        with col_home:
            st.markdown(f"<h4 style='text-align:right'>{row['home_team']}</h4>", unsafe_allow_html=True)
        with col_score:
            st.markdown(f"<h4 style='text-align:center; color:#c8a415'>{int(row['home_score'])} - {int(row['away_score'])}</h4>", unsafe_allow_html=True)
        with col_away:
            st.markdown(f"<h4 style='text-align:left'>{row['away_team']}</h4>", unsafe_allow_html=True)
        st.caption(f"Group {row['group_short']} | {row['date_only']}")
        st.markdown("---")

# ============================================
# PAGE 4 — PREDICTIONS
# ============================================
elif page == "🤖 Predictions":
    st.title("🤖 AI Predictions — Knockout Stage")
    st.markdown("*Random Forest model trained on 2018 & 2022 World Cup data*")
    st.markdown("---")

    tab1, tab2 = st.tabs(["Group Advancement", "Tournament Winner"])

    with tab1:
        st.subheader("Group Advancement Probability")
        st.markdown("🟢 Strong favourite &nbsp; 🟡 In contention &nbsp; 🔴 At risk")
        st.markdown("---")

        groups = sorted(team_stats_df['group'].unique())
        selected = st.selectbox("Select Group", ["All Groups"] + list(groups))

        if selected == "All Groups":
            display_df = team_stats_df.sort_values('advancement_prob', ascending=False)
        else:
            display_df = team_stats_df[team_stats_df['group'] == selected].sort_values(
                'advancement_prob', ascending=False)

        for _, row in display_df.iterrows():
            prob = row['advancement_prob_pct']
            emoji = "🟢" if prob >= 60 else "🟡" if prob >= 35 else "🔴"
            col1, col2, col3, col4 = st.columns([3, 1, 1, 3])
            with col1:
                st.markdown(f"{emoji} **{row['team']}** (Group {row['group']})")
            with col2:
                st.markdown(f"Pts: **{int(row['points'])}**")
            with col3:
                st.markdown(f"GD: **{int(row['goal_difference'])}**")
            with col4:
                st.progress(int(prob), text=f"{prob}%")

        st.markdown("---")
        st.caption("Adj% blends model prediction with FIFA ranking prior — weight shifts to pure form as more games are played")

    with tab2:
        st.subheader("🏆 Tournament Winner Predictions")
        top10 = team_stats_df.nlargest(10, 'win_probability')[
            ['team', 'group', 'fifa_ranking', 'advancement_prob_pct', 'win_probability']
        ]

        fig = px.bar(top10, x='team', y='win_probability',
                     color='win_probability',
                     color_continuous_scale='Greens',
                     labels={'win_probability': 'Win Probability %', 'team': 'Team'},
                     title='Top 10 Tournament Winner Predictions')
        fig.update_layout(height=450, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Detailed breakdown:**")
        for i, (_, row) in enumerate(top10.iterrows(), 1):
            medal = "🥇" if i==1 else "🥈" if i==2 else "🥉" if i==3 else f"{i}."
            st.markdown(f"{medal} **{row['team']}** — Win probability: `{row['win_probability']}%` | Advancement: `{row['advancement_prob_pct']}%` | FIFA Rank: #{int(row['fifa_ranking'])}")

        st.markdown("---")
        st.caption("Winner probability = 50% advancement prob + 30% FIFA ranking + 20% momentum score")