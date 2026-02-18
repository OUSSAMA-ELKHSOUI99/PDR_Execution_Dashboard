import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, MarkerCluster

# --- PAGE CONFIG ---
st.set_page_config(page_title="Système d'Aide à la Décision - Marrakech-Safi", layout="wide", page_icon="🇲🇦")

# Custom CSS to make metrics look like "Government Cards"
st.markdown("""
<style>
    .main-header {font-size:30px; font-weight:bold; color:#1f77b4;}
    .sub-header {font-size:20px; color:#555;}
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("PDR_Marrakech_Safi_Projects.csv", sep=";")
        
        # --- NEW FEATURE: SIMULATE GPS COORDINATES ---
        # Since we don't have real GPS data, we simulate it around Marrakech coordinates
        # Center of Marrakech-Safi approx: 31.6 -8.0
        # We add random "jitter" to scatter points across the region
        np.random.seed(42) # Consistent random numbers
        df["lat"] = 31.62 + np.random.uniform(-0.5, 0.5, len(df))
        df["lon"] = -8.00 + np.random.uniform(-0.8, 0.8, len(df))
        
        
    except FileNotFoundError:
        return None, None

    try:
        df_water = pd.read_csv("Water_Data_Marrakech_Safi.csv", sep=";")
    except FileNotFoundError:
        st.error("⚠️ Fichier Eau manquant. Lancez le script de génération Eau.")
        return None, None

    return df, df_water    

df, df_water = load_data()

if df is None or df_water is None :
    st.error("⚠️ Veuillez générer le fichier CSV d'abord (Step 1).")
    st.stop()

# --- SIDEBAR: FILTERS & EXPORT ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Flag_of_Morocco.svg/1280px-Flag_of_Morocco.svg.png", width=50)
st.sidebar.title("PORTAIL RÉGIONAL")
st.sidebar.info("Système d'Aide à la Décision")

# st.sidebar.title("🔍 Filtres PDR")


# selected_province = st.sidebar.multiselect(
#     "Province", options=df["Province"].unique(), default=df["Province"].unique()
# )
# selected_sector = st.sidebar.multiselect(
#     "Secteur", options=df["Secteur"].unique(), default=df["Secteur"].unique()
# )

# # Apply Filters
# df_filtered = df[
#     (df["Province"].isin(selected_province)) & 
#     (df["Secteur"].isin(selected_sector))
# ]




navigation = st.sidebar.radio(
    "Navigation",
    ["🏠 Vue d'Ensemble (Synthèse)", "📊 Pilotage PDR (Projets)", "💧 Vigilance Eau (SIG)"]
)

st.sidebar.markdown("---")
st.sidebar.caption("© 2026 Conseil Régional Marrakech-Safi")
if navigation == "🏠 Vue d'Ensemble (Synthèse)":
    st.markdown("<h1 class='main-header'>Tableau de Bord Exécutif</h1>", unsafe_allow_html=True)
    st.markdown("Synthèse des indicateurs clés de la région.")
    
    # Global Metrics
    total_budget = df['Budget_DH'].sum()
    critical_water = len(df_water[df_water["Statut"].str.contains("Critique")])
    delayed_projects = len(df[df["Statut"] == "En Retard"])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Budget Total Engagé", f"{total_budget/1e6:.0f} MDH")
    col2.metric("🚨 Alertes Sécheresse", f"{critical_water} Zones", delta="Priorité Absolue", delta_color="inverse")
    col3.metric("⚠️ Projets en Retard", f"{delayed_projects} Projets", delta="Action Requise", delta_color="inverse")

    st.markdown("---")
    
    # Combined Map (Advanced Feature)
    st.subheader("📍 Carte Unifiée des Risques et Investissements")
    st.info("Cette carte superpose les projets d'investissement (Bleu) et les alertes hydriques (Rouge).")
    
    m = folium.Map(location=[31.6, -8.0], zoom_start=8, tiles="CartoDB positron")
    
    # Layer 1: Critical Water Zones (Red Heatmap)
    heat_data = df_water[df_water["Statut"].str.contains("Critique")][['lat', 'lon']].values.tolist()
    HeatMap(heat_data, radius=25, blur=20, gradient={0.4: 'red', 1: 'darkred'}).add_to(m)
    
    # Layer 2: PDR Projects (Blue Circles)
    # We only show big projects (> 10MDH) to avoid clutter
    big_projects = df[df["Budget_DH"] > 10000000]
    for _, row in big_projects.iterrows():
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=5,
            color="blue",
            fill=True,
            fill_opacity=0.6,
            popup=f"<b>{row['Intitulé_Projet']}</b><br>Budget: {row['Budget_DH']/1e6:.1f} MDH"
        ).add_to(m)
        
    st_folium(m, width="100%", height=500) 
elif navigation == "📊 Pilotage PDR (Projets)":
#     selected_province = st.sidebar.multiselect(
#      "Province", options=df["Province"].unique(), default=df["Province"].unique()
#     )
#     selected_sector = st.sidebar.multiselect(
#     "Secteur", options=df["Secteur"].unique(), default=df["Secteur"].unique()
#     )

# # Apply Filters
#     df_filtered = df[
#     (df["Province"].isin(selected_province)) & 
#     (df["Secteur"].isin(selected_sector))
#     ]
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        prov = st.multiselect("Filtrer par Province", df["Province"].unique(), default=df["Province"].unique())
    with col_f2:
        sect = st.multiselect("Filtrer par Secteur", df["Secteur"].unique(), default=df["Secteur"].unique())
        
    df_filtered = df[(df["Province"].isin(prov)) & (df["Secteur"].isin(sect))]

    # --- NEW FEATURE: EXPORT DATA ---
    st.sidebar.markdown("---")
    st.sidebar.header("📂 Exportation")
    csv = df_filtered.to_csv(index=False, sep=";").encode('utf-8-sig')
    st.sidebar.download_button(
        label="📥 Télécharger en Excel (CSV)",
        data=csv,
        file_name='Projets_PDR_Filtres.csv',
        mime='text/csv',
        help="Télécharger les données filtrées pour usage administratif."
    )

# --- HEADER & KPIs ---
    st.title("🗺️ Tableau de Bord Stratégique : Région Marrakech-Safi")
    st.markdown("### Suivi de l'Exécution du Plan de Développement Régional (PDR)")


    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Budget Engagé", f"{df_filtered['Budget_DH'].sum()/1e6:.1f} MDH", delta="En Millions de DH")
    col2.metric("🏗️ Projets Actifs", len(df_filtered))
    col3.metric("⚠️ Projets en Retard", len(df_filtered[df_filtered["Statut"] == "En Retard"]), delta_color="inverse")
    col4.metric("✅ Taux d'Achèvement Moyen", f"{df_filtered['Taux_Avancement'].mean():.1f}%")

    st.markdown("---")

    # --- ROW 2: MAP & ALERTS (The "Territorial Intelligence" Layer) ---
    col_map, col_alerts = st.columns([2, 1])

    with col_map:
        st.subheader("📍 Carte Territoriale des Projets")
        # Using Plotly Mapbox for professional look
        fig_map = px.scatter_mapbox(
            df_filtered, 
            lat="lat", 
            lon="lon", 
            color="Secteur",
            size="Budget_DH", # Bigger budget = Bigger dot
            hover_name="Intitulé_Projet",
            hover_data={"Province": True, "Statut": True, "lat": False, "lon": False},
            zoom=7, 
            center={"lat": 31.62, "lon": -8.00},
            mapbox_style="carto-positron", # Clean map style
            title="Répartition Géographique des Investissements"
        )
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)

    with col_alerts:
        st.subheader("🚨 Alertes Critiques")
        st.markdown("Projets nécessitant une **intervention immédiate** (Statut: Suspendu ou En Retard > 10MDH).")

        # Filter for "Critical" projects
        critical_projects = df_filtered[
            (df_filtered["Statut"].isin(["Suspendu", "En Retard"])) & 
            (df_filtered["Budget_DH"] > 5000000) # Only big projects
        ].sort_values("Budget_DH", ascending=False).head(5)

        for index, row in critical_projects.iterrows():
            st.error(f"**{row['Province']}**: {row['Intitulé_Projet']} ({row['Statut']})")

    # --- ROW 3: ANALYTICS ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📊 Répartition Budgétaire par Province")
        fig_bar = px.bar(
            df_filtered.groupby("Province")["Budget_DH"].sum().reset_index(),
            x="Budget_DH", y="Province", orientation="h",
            color="Budget_DH", color_continuous_scale="Viridis",
            text_auto=".2s"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.subheader("📈 Avancement par Secteur")
        # Box plot is better for engineering roles: it shows distribution of progress
        fig_box = px.box(
            df_filtered, 
            x="Secteur", 
            y="Taux_Avancement", 
            color="Secteur",
            title="Dispersion de l'avancement des projets par secteur"
        )
        st.plotly_chart(fig_box, use_container_width=True)

    col_left2, = st.columns(1)

    with col_left2:
        st.subheader("🏗️ État d'Avancement des Projets")
        # A Pie Chart showing project status (Blocked, Done, In Progress)
        fig_status = px.pie(
            df_filtered,
            names="Statut",
            title="Répartition des Projets par Statut",
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig_status, use_container_width=True)

    st.subheader("📋 Liste Détaillée des Projets")
    st.dataframe(df_filtered)

elif navigation == "💧 Vigilance Eau (SIG)":
    # st.sidebar.title("💧 Filtres Hydrologiques")
    selected_type = st.multiselect("Type d'Infrastructure", df_water["Type"].unique(), default=df_water["Type"].unique())
    show_critical = st.checkbox("Afficher uniquement les zones CRITIQUES", value=False)

    # Apply filters
    df_filtered = df_water[df_water["Type"].isin(selected_type)]
    if show_critical:
        df_filtered = df_filtered[df_filtered["Statut"].str.contains("Critique")]

    # --- MAIN PAGE ---
    st.title("🌍 Carte de Vigilance : Ressources Hydriques")
    st.markdown("Suivi géospatial des barrages, forages et zones agricoles de la région Marrakech-Safi.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Points d'Eau Suivis", len(df_filtered))
    col2.metric("Zones Critiques", len(df_filtered[df_filtered["Statut"].str.contains("Critique")]))
    # Calculate average dam level if dams are present
    dams = df_filtered[df_filtered["Type"] == "Barrage (Dam)"]
    avg_level = dams["Niveau_Ou_Debit"].mean() if not dams.empty else 0
    col3.metric("Niveau Moyen des Barrages", f"{avg_level:.1f}%", delta="-5% vs 2023", delta_color="inverse")

    # --- THE MAP ---
    m = folium.Map(location=[31.8, -8.5], zoom_start=8, tiles="CartoDB positron")

    # 1. Add Heatmap (Visualizing Density of Alerts)
    # We use the coordinates of "Critical" points to build a heat layer
    critical_points = df_water[df_water["Statut"].str.contains("Critique")]
    if not critical_points.empty:
        heat_data = [[row['lat'], row['lon']] for index, row in critical_points.iterrows()]
        HeatMap(heat_data, radius=15, blur=20, gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}).add_to(m)

    # 2. Add Markers (Clustered for performance)
    marker_cluster = MarkerCluster().add_to(m)

    for index, row in df_filtered.iterrows():
        # Color logic
        color = "green"
        if "Critique" in row["Statut"]:
            color = "red"
        elif "Maintenance" in row["Statut"]:
            color = "orange"
        elif row["Type"] == "Barrage (Dam)":
            color = "blue"

        # Icon logic
        icon_type = "tint" # default water drop
        if row["Type"] == "Zone Agricole":
            icon_type = "leaf"
        elif row["Type"] == "Barrage (Dam)":
            icon_type = "database" # looks like a dam wall/storage

        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=f"<b>{row['Nom']}</b><br>Statut: {row['Statut']}<br>Niveau: {row['Niveau_Ou_Debit']}",
            tooltip=row['Type'],
            icon=folium.Icon(color=color, icon=icon_type, prefix="fa")
        ).add_to(marker_cluster)

    # Display Map in Streamlit
    st_folium(m, width="100%", height=600)






    st.markdown("### 📋 Détails des Infrastructures")
    st.dataframe(df_filtered)

