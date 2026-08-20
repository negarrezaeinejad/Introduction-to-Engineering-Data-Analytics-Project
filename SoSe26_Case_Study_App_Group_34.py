import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ==========================================
# 1. PAGE CONFIGURATION & HIGH-CONTRAST UI
# ==========================================
st.set_page_config(
    page_title="Ultimate Vehicle Recall Dashboard", 
    page_icon="🚘", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for high readability and crisp borders
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Source Sans Pro', sans-serif; 
        color: #1e272e; 
    }
    h1, h2, h3, h4 { color: #0984e3; font-weight: 700; }
    
    /* Top KPI Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #dcdde1;
        border-left: 6px solid #0984e3;
        padding: 15px;
        border-radius: 6px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Journey Trace Boxes */
    .journey-box { 
        padding: 25px; 
        border-radius: 8px; 
        background-color: #f5f6fa; 
        border: 2px solid #0984e3; 
        margin-top: 15px; 
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        color: #2f3542;
        font-size: 16px;
    }
    .journey-box h4 {
        color: #0984e3;
        margin-bottom: 15px;
        margin-top: 0;
        font-size: 22px;
        border-bottom: 2px solid #dcdde1;
        padding-bottom: 5px;
    }
    .journey-box b { color: #2f3542; font-weight: 700; }
    
    .journey-arrow { 
        font-size: 32px; 
        color: #718093; 
        text-align: center; 
        font-weight: bold;
        margin-top: 80px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA PIPELINE & STATE MANAGEMENT
# ==========================================
@st.cache_data
def load_data():
    primary_path = "data/SoSe26_Case_Study_finalData_Group_34.csv"
    fallback_path = "SoSe26_Case_Study_finalData_Group_34.csv"
    
    if os.path.exists(primary_path):
        df = pd.read_csv(primary_path, sep=';', low_memory=False)
    elif os.path.exists(fallback_path):
        df = pd.read_csv(fallback_path, sep=';', low_memory=False)
    else:
        st.error("⚠️ Data file not found. Please ensure the CSV is in the 'data/' folder.")
        return pd.DataFrame()
    
    df['Produktionsdatum'] = pd.to_datetime(df['Produktionsdatum'], errors='coerce')
    df['Zulassung'] = pd.to_datetime(df['Zulassung'], errors='coerce')
    df['Lag_Days'] = (df['Zulassung'] - df['Produktionsdatum']).dt.days
    return df[df['Lag_Days'] >= 0]

df = load_data()

# Robust State Initialization
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "📊 Executive Overview"
if "search_id" not in st.session_state:
    st.session_state.search_id = ""

# ==========================================
# 3. SIDEBAR FILTERS
# ==========================================
logo_path = "www/logo.png"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.markdown("### 🏛️ Dept. of Quality Science")
    
st.sidebar.header("🔍 Global Dashboard Filters")
st.sidebar.markdown("Changes here apply to all tabs.")

if not df.empty:
    priorities = st.sidebar.multiselect("Priority Zone", options=sorted(df['Recall_Priority'].dropna().unique()), default=df['Recall_Priority'].unique())
    cities = st.sidebar.multiselect("Closest Major City", options=sorted(df['Closest_City'].dropna().unique()), default=df['Closest_City'].unique())
    plants = st.sidebar.multiselect("Manufacturing Plant", options=sorted(df['Werksnummer'].dropna().unique()), default=df['Werksnummer'].unique())
    
    max_dist = float(df['Min_Distance_City_KM'].max())
    distance_range = st.sidebar.slider("Distance to City (KM)", 0.0, max_dist, (0.0, max_dist), step=5.0)
    
    min_d, max_d = df['Produktionsdatum'].min().date(), df['Produktionsdatum'].max().date()
    dates = st.sidebar.slider("Production Date Range", min_value=min_d, max_value=max_d, value=(min_d, max_d))
    
    mask = (
        df['Recall_Priority'].isin(priorities) & 
        df['Closest_City'].isin(cities) & 
        df['Werksnummer'].isin(plants) &
        (df['Min_Distance_City_KM'] >= distance_range[0]) & 
        (df['Min_Distance_City_KM'] <= distance_range[1]) &
        (df['Produktionsdatum'].dt.date >= dates[0]) & 
        (df['Produktionsdatum'].dt.date <= dates[1])
    )
    filtered_df = df[mask]

    # ==========================================
    # 4. MAIN DASHBOARD HEADER & KPIs
    # ==========================================
    st.title("Ultimate Type11 Vehicle Recall Center")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Selected Vehicles", f"{len(filtered_df):,}")
    c2.metric("Critical Priority (<=50km)", f"{len(filtered_df[filtered_df['Recall_Priority'] == 'High Priority (<=50km)']):,}")
    c3.metric("Avg Logistics Lag", f"{filtered_df['Lag_Days'].mean():.1f} Days" if not filtered_df.empty else "0")
    c4.metric("Active Supply Plants", f"{filtered_df['Werksnummer'].nunique()}")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 5. DYNAMIC NAVIGATION (Decoupled State)
    # ==========================================
    nav_options = [
        "📊 Executive Overview", 
        "🗺️ Geospatial Maps", 
        "🚘 Vehicle Lifecycle Trace", 
        "🏭 Supply Chain Analytics", 
        "🗄️ Data & Statistics"
    ]
    
    # Callback to update our custom state variable safely
    def update_tab():
        st.session_state.current_tab = st.session_state.nav_radio

    st.radio(
        "Navigation", 
        nav_options, 
        index=nav_options.index(st.session_state.current_tab), # Read from state
        horizontal=True, 
        key="nav_radio", # Unique widget key
        on_change=update_tab, # Update state on click
        label_visibility="collapsed"
    )
    
    # Assign the active tab
    selected_tab = st.session_state.current_tab

    st.markdown("---")

    # ==========================================
    # 6. TAB ROUTING & VISUALIZATIONS
    # ==========================================
    
    # ---------------------------------
    # TAB 1: EXECUTIVE OVERVIEW
    # ---------------------------------
    if selected_tab == "📊 Executive Overview":
        col_a, col_b = st.columns(2)
        with col_a:
            if not filtered_df.empty:
                city_counts = filtered_df['Closest_City'].value_counts().reset_index()
                city_counts.columns = ['City', 'Count']
                fig_city = px.bar(city_counts, x='City', y='Count', title="Recall Volume by Major City", color_discrete_sequence=['#0984e3'])
                fig_city.update_traces(texttemplate='%{y}', textposition='outside')
                fig_city.update_layout(xaxis_title="", yaxis_title="Vehicle Count")
                st.plotly_chart(fig_city, use_container_width=True)
                st.caption("💡 **How to read:** The height of the bar and the number above it indicate the total volume of recalled vehicles registered near each specific city.")
                
        with col_b:
            if not filtered_df.empty:
                priority_counts = filtered_df['Recall_Priority'].value_counts().reset_index()
                priority_counts.columns = ['Priority', 'Count']
                color_map = {'High Priority (<=50km)': '#d63031', 'Medium Priority (50-100km)': '#fdcb6e', 'Outside Zone': '#b2bec3'}
                fig_priority = px.pie(priority_counts, names='Priority', values='Count', title="Priority Zone Distribution", color='Priority', color_discrete_map=color_map, hole=0.45)
                fig_priority.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_priority, use_container_width=True)
                st.caption("💡 **How to read:** The slices represent the percentage of vehicles falling into each geographic risk zone. Larger slices mean higher liability in that area.")
                
        col_c, col_d = st.columns(2)
        with col_c:
            if not filtered_df.empty:
                timeline_df = filtered_df.groupby(filtered_df['Produktionsdatum'].dt.to_period('M')).size().reset_index(name='New Vehicles')
                timeline_df['Produktionsdatum'] = timeline_df['Produktionsdatum'].astype(str)
                timeline_df['Cumulative Total'] = timeline_df['New Vehicles'].cumsum()
                fig_area = px.area(timeline_df, x='Produktionsdatum', y='Cumulative Total', title="Cumulative Recall Liability Growth", color_discrete_sequence=['#d63031'])
                st.plotly_chart(fig_area, use_container_width=True)
                st.caption("💡 **How to read:** The upward curve shows the total running sum of defective vehicles as they were produced month over month.")
                
        with col_d:
            if not filtered_df.empty:
                plant_city_df = filtered_df.groupby(['Werksnummer', 'Closest_City']).size().reset_index(name='Count')
                plant_city_df['Werksnummer'] = plant_city_df['Werksnummer'].astype(str)
                fig_tree = px.treemap(plant_city_df, path=['Werksnummer', 'Closest_City'], values='Count', title="Volume Proportions: Assembly Plant to Destination City", color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_tree.update_traces(textinfo="label+value")
                st.plotly_chart(fig_tree, use_container_width=True)
                st.caption("💡 **How to read:** The size of each block represents the volume of vehicles. Click on a specific Plant ID to zoom in and see exactly which cities it shipped to.")
                
        col_e, col_f = st.columns(2)
        with col_e:
            if not filtered_df.empty:
                sun_df = filtered_df.groupby(['Recall_Priority', 'Closest_City', 'Werksnummer']).size().reset_index(name='Count')
                sun_df['Werksnummer'] = sun_df['Werksnummer'].astype(str)
                fig_sun = px.sunburst(sun_df, path=['Recall_Priority', 'Closest_City', 'Werksnummer'], values='Count', title="Hierarchical Recall Flow: Zone ➔ City ➔ Plant", color_discrete_sequence=px.colors.qualitative.Safe)
                fig_sun.update_traces(textinfo="label+percent parent")
                st.plotly_chart(fig_sun, use_container_width=True)
                st.caption("💡 **How to read:** Start from the inner circle (Priority Zone) and read outwards to see the City and Origin Plant breakdown. Click a slice to drill down.")
                
        with col_f:
            if not filtered_df.empty:
                prod_df = filtered_df.groupby(filtered_df['Produktionsdatum'].dt.to_period('M')).size().reset_index(name='Count')
                prod_df['Type'] = 'Produced'
                prod_df['Date'] = prod_df['Produktionsdatum'].astype(str)

                reg_df = filtered_df.groupby(filtered_df['Zulassung'].dt.to_period('M')).size().reset_index(name='Count')
                reg_df['Type'] = 'Registered'
                reg_df['Date'] = reg_df['Zulassung'].astype(str)

                flow_df = pd.concat([prod_df[['Date', 'Count', 'Type']], reg_df[['Date', 'Count', 'Type']]])
                fig_flow = px.line(flow_df, x='Date', y='Count', color='Type', title="Monthly Volume: Production vs. Registration", color_discrete_sequence=['#0984e3', '#00b894'])
                st.plotly_chart(fig_flow, use_container_width=True)
                st.caption("💡 **How to read:** Compare the blue line (vehicles produced) against the green line (vehicles registered). Wide gaps indicate severe supply chain bottlenecks.")

    # ---------------------------------
    # TAB 2: GEOSPATIAL MAPS
    # ---------------------------------
    elif selected_tab == "🗺️ Geospatial Maps":
        st.markdown("### 📍 Interactive Point Map")
        st.info("💡 **Interactive Feature:** Click on any vehicle dot on this map. The dashboard will automatically capture the ID, jump to the **Vehicle Lifecycle Trace**, and pull the records.")
        
        if not filtered_df.empty:
            map_limit = 10000
            map_df = filtered_df.sample(map_limit, random_state=42).reset_index(drop=True) if len(filtered_df) > map_limit else filtered_df.copy().reset_index(drop=True)
            
            fig_map = px.scatter_mapbox(
                map_df, lat="Breitengrad_num", lon="Laengengrad_num", color="Recall_Priority",
                hover_name="ID_Fahrzeug", hover_data={"Closest_City": True, "Min_Distance_City_KM": ":.1f", "Breitengrad_num": False, "Laengengrad_num": False},
                color_discrete_map={'High Priority (<=50km)': '#d63031', 'Medium Priority (50-100km)': '#fdcb6e', 'Outside Zone': '#b2bec3'},
                zoom=5.2, center={"lat": 51.1657, "lon": 10.4515}, height=600
            )
            fig_map.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
            
            # The Magic Jump Trigger (Safely updating decoupled state)
            map_event = st.plotly_chart(fig_map, use_container_width=True, on_select="rerun", selection_mode="points")
            if map_event and "selection" in map_event and map_event["selection"]["points"]:
                clicked_idx = map_event["selection"]["points"][0]["point_index"]
                selected_id = map_df.iloc[clicked_idx]["ID_Fahrzeug"]
                
                # Check to prevent infinite loops, then trigger jump
                if st.session_state.search_id != selected_id or st.session_state.current_tab != "🚘 Vehicle Lifecycle Trace":
                    st.session_state.search_id = selected_id
                    st.session_state.current_tab = "🚘 Vehicle Lifecycle Trace"
                    st.rerun()
                
            st.caption("💡 **How to read:** Each point represents a registered vehicle. The colors indicate their priority status based on proximity to a major city.")

        st.markdown("---")
        st.markdown("### 🔥 Density Heatmap")
        if not filtered_df.empty:
            fig_density = px.density_mapbox(
                map_df, lat='Breitengrad_num', lon='Laengengrad_num', z=None, radius=8,
                center=dict(lat=51.1657, lon=10.4515), zoom=5.2, mapbox_style="carto-positron", height=500, color_continuous_scale="Inferno"
            )
            fig_density.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_density, use_container_width=True)
            st.caption("💡 **How to read:** The bright yellow/white zones represent the highest geographical density of recalled vehicles, useful for targeting massive recall campaigns.")

    # ---------------------------------
    # TAB 3: VEHICLE LIFECYCLE TRACE
    # ---------------------------------
    elif selected_tab == "🚘 Vehicle Lifecycle Trace":
        st.markdown("### Specific Vehicle Forensics")
        
        # Search box uses session state to auto-fill if clicked from map
        search_id = st.text_input("Enter Vehicle ID (e.g., 11-1-11-433682):", value=st.session_state.search_id)
        
        if search_id:
            vehicle_data = df[df['ID_Fahrzeug'] == search_id]
            if not vehicle_data.empty:
                v = vehicle_data.iloc[0]
                
                tr_a, tr_b, tr_c = st.columns([2, 1, 2])
                with tr_a:
                    st.markdown(f"""
                    <div class="journey-box">
                        <h4>🏭 Assembly & Parts</h4>
                        <b>Plant ID:</b> {v['Werksnummer']}<br>
                        <b>Manufacturer ID:</b> {v['Herstellernummer']}<br>
                        <b>Engine Code:</b> {v['ID_Motor']}<br>
                        <b>Production Date:</b> {v['Produktionsdatum'].strftime('%B %d, %Y')}
                    </div>
                    """, unsafe_allow_html=True)
                
                with tr_b:
                    st.markdown(f"<div class='journey-arrow'> ⏱️ {v['Lag_Days']} Days<br>⟶ </div>", unsafe_allow_html=True)
                
                with tr_c:
                    st.markdown(f"""
                    <div class="journey-box">
                        <h4>📍 Final Registration</h4>
                        <b>Registered City:</b> {v['Gemeinden']}<br>
                        <b>Closest Major City:</b> {v['Closest_City']}<br>
                        <b>Distance to Ban Zone:</b> {v['Min_Distance_City_KM']:.1f} km<br>
                        <b>Registration Date:</b> {v['Zulassung'].strftime('%B %d, %Y')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                st.markdown("<br>", unsafe_allow_html=True)
                map_col, table_col = st.columns([1, 2])
                
                with map_col:
                    st.markdown(f"**Location Map: {v['Gemeinden']}**")
                    trace_map = px.scatter_mapbox(
                        pd.DataFrame({'lat': [v['Breitengrad_num']], 'lon': [v['Laengengrad_num']]}),
                        lat='lat', lon='lon', zoom=9, height=300, color_discrete_sequence=['#0984e3']
                    )
                    trace_map.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
                    st.plotly_chart(trace_map, use_container_width=True)
                    st.caption("💡 **How to read:** Pinpoints the exact registration municipality of this specific vehicle.")
                
                with table_col:
                    st.markdown("**Batch Analysis: Other affected vehicles registered in the same city on the same date**")
                    batch_df = df[(df['Gemeinden'] == v['Gemeinden']) & (df['Zulassung'] == v['Zulassung']) & (df['ID_Fahrzeug'] != v['ID_Fahrzeug'])]
                    if not batch_df.empty:
                        st.dataframe(batch_df[['ID_Fahrzeug', 'ID_Motor', 'Werksnummer', 'Lag_Days']].head(10), use_container_width=True, height=300)
                    else:
                        st.info("No other recalled vehicles were registered in this municipality on this exact date.")
                    st.caption("💡 **How to read:** If multiple cars appear here, it indicates dealership batches, meaning bulk recall notices could be routed to this specific region.")
            else:
                st.error("⚠️ Vehicle ID not found in the dataset.")

    # ---------------------------------
    # TAB 4: SUPPLY CHAIN ANALYTICS
    # ---------------------------------
    elif selected_tab == "🏭 Supply Chain Analytics":
        sc1, sc2 = st.columns(2)
        with sc1:
            if not filtered_df.empty:
                fig_hist = px.histogram(filtered_df, x='Lag_Days', nbins=50, title="Distribution of Logistics Delays", color_discrete_sequence=['#8e44ad'])
                fig_hist.update_layout(xaxis_title="Days Between Production and Registration", yaxis_title="Vehicle Count")
                st.plotly_chart(fig_hist, use_container_width=True)
                st.caption("💡 **How to read:** The tallest bars show the most common wait times. A long tail to the right means some vehicles sat in logistics for an excessive amount of time.")
                
        with sc2:
            if not filtered_df.empty:
                plant_df = filtered_df['Werksnummer'].value_counts().reset_index()
                plant_df.columns = ['Plant ID', 'Total Engines Produced']
                plant_df['Plant ID'] = plant_df['Plant ID'].astype(str)
                fig_plant = px.bar(plant_df, x='Total Engines Produced', y='Plant ID', orientation='h', title="Defect Volume by Origin Plant", color_discrete_sequence=['#27ae60'])
                fig_plant.update_traces(texttemplate='%{x}', textposition='outside')
                fig_plant.update_layout(xaxis_title="Volume of Vehicles", yaxis_title="Plant ID")
                st.plotly_chart(fig_plant, use_container_width=True)
                st.caption("💡 **How to read:** Identifies exactly which manufacturing plants are responsible for the highest volume of recalled vehicles.")

        sc3, sc4 = st.columns(2)
        with sc3:
            if not filtered_df.empty:
                box_df = filtered_df.copy()
                box_df['Werksnummer'] = box_df['Werksnummer'].astype(str)
                fig_box = px.box(box_df, x='Werksnummer', y='Lag_Days', title="Logistics Delay Spread per Plant", color_discrete_sequence=['#f39c12'])
                st.plotly_chart(fig_box, use_container_width=True)
                st.caption("💡 **How to read:** The colored box represents where the majority of shipping times fell. Dots above the whiskers highlight extreme outlier delays for that specific plant.")
                
        with sc4:
            if not filtered_df.empty:
                fig_scatter = px.scatter(
                    filtered_df.sample(5000) if len(filtered_df) > 5000 else filtered_df, 
                    x='Min_Distance_City_KM', y='Lag_Days', opacity=0.5,
                    title="Correlation: Distance to City vs. Shipping Delay",
                    color_discrete_sequence=['#16a085']
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
                st.caption("💡 **How to read:** Evaluates if shipping vehicles further away (x-axis) resulted in longer delays (y-axis). A scattered cloud means distance is not the primary cause of delay.")

        sc5, sc6 = st.columns(2)
        with sc5:
            if not filtered_df.empty:
                heat_df = filtered_df.copy()
                heat_df['Werksnummer'] = heat_df['Werksnummer'].astype(str)
                fig_heat = px.density_heatmap(
                    heat_df, x='Closest_City', y='Werksnummer', z='Lag_Days', histfunc='avg', 
                    title="Average Delay (Days) Matrix: Plant vs Destination",
                    color_continuous_scale="Blues", text_auto=".1f"
                )
                st.plotly_chart(fig_heat, use_container_width=True)
                st.caption("💡 **How to read:** Darker blue squares indicate plant-to-city shipping routes that suffer from the highest average logistics delays.")
                
        with sc6:
            if not filtered_df.empty:
                lag_trend = filtered_df.groupby(filtered_df['Produktionsdatum'].dt.to_period('M'))['Lag_Days'].mean().reset_index()
                lag_trend['Date'] = lag_trend['Produktionsdatum'].astype(str)
                fig_trend = px.line(lag_trend, x='Date', y='Lag_Days', title="Shipping Efficiency: Average Lag Over Time", markers=True, color_discrete_sequence=['#e84393'])
                st.plotly_chart(fig_trend, use_container_width=True)
                st.caption("💡 **How to read:** An upward trend indicates the supply chain was getting slower over time, while a downward trend shows shipping times were improving.")

    # ---------------------------------
    # TAB 5: DATA EXPORT & STATISTICS
    # ---------------------------------
    elif selected_tab == "🗄️ Data & Statistics":
        exp1, exp2 = st.columns([1, 2])
        
        with exp1:
            st.markdown("### Numerical Summary")
            st.markdown("Statistical breakdown of numerical fields based on current filters.")
            st.dataframe(filtered_df[['Lag_Days', 'Min_Distance_City_KM']].describe(), use_container_width=True)
            
            csv = filtered_df.to_csv(index=False, sep=';').encode('utf-8')
            st.download_button(
                label="⬇️ Download Filtered CSV for Reporting",
                data=csv,
                file_name='filtered_recall_data.csv',
                mime='text/csv',
                use_container_width=True
            )
            
        with exp2:
            st.markdown("### Raw Extraction View")
            display_df = filtered_df.drop(columns=['Laengengrad_num', 'Breitengrad_num'], errors='ignore')
            st.dataframe(display_df, use_container_width=True, height=500)
else:
    st.warning("⚠️ No data matches the current filter selection.")