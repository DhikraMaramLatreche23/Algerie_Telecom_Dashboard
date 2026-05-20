import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

# Configure page
st.set_page_config(
    page_title="Algérie Télécom Dashboard",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Algérie Télécom branding
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #002147 0%, #00A859 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 33, 71, 0.3);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #00A859;
        margin-bottom: 1rem;
    }
    
    .metric-title {
        color: #002147;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        color: #00A859;
        font-size: 2rem;
        font-weight: bold;
        line-height: 1;
    }
    
    .metric-delta {
        font-size: 0.8rem;
        margin-top: 0.25rem;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #002147 0%, #00A859 100%);
    }
    
    .stSelectbox > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    div.stButton > button {
        background: linear-gradient(135deg, #002147 0%, #00A859 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 33, 71, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📡 Algérie Télécom Dashboard</h1>
    <p>Analyse Avancée des Abonnements Internet et Prévisions</p>
</div>
""", unsafe_allow_html=True)

# Load data function
@st.cache_data
def load_telecom_data():
    """Load and preprocess Algeria Telecom data"""
    try:
        # Load main internet data
        df_raw = pd.read_csv('data/internet_data.csv', index_col=0)
        df = df_raw.T
        
        # Clean column names
        column_mapping = {
            'Parc_global_des_abonnés_Internet': 'Total_Internet_Subscribers',
            'Abonnés_ADSL': 'ADSL_Subscribers',
            'Abonnés_Internet_4G_LTE_fixe': 'Fixed_4G_LTE_Subscribers',
            'Abonnés_Internet_fibre_FTTH': 'Fiber_FTTH_Subscribers',
            'Abonnés_actifs_de_l\'Internet_mobile 3G/4G': 'Mobile_3G_4G_Subscribers',
            '3G': '3G_Subscribers',
            '4G': '4G_Subscribers',
            'Total_du_trafic_consommé': 'Total_Traffic_Consumed',
            'Revenu_mensuel_moyenpar_abonné(DA)': 'Average_Revenue_Per_User_DA'
        }
        
        df.columns = [column_mapping.get(col, col) for col in df.columns]
        
        # Clean numeric data
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace(' ', '').str.replace(',', '').str.replace('**', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Create proper date column
        def parse_period(period_str):
            try:
                year, quarter = period_str.split('_T')
                quarter_month = {'1': '01', '2': '04', '3': '07', '4': '10'}
                return pd.to_datetime(f"{year}-{quarter_month[quarter]}-01")
            except:
                return pd.NaT
        
        df['Period'] = df.index
        df['Date'] = df.index.map(parse_period)
        df['Year'] = df['Date'].dt.year
        df['Quarter'] = df['Date'].dt.quarter
        
        df = df.reset_index(drop=True)
        df = df.sort_values('Date').reset_index(drop=True)
        df = df.fillna(0)
        
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        return None

# Load subscription data if exists
@st.cache_data
def load_subscription_data():
    """Load new subscription entries if file exists"""
    try:
        if os.path.exists('data/subscriptions.csv'):
            return pd.read_csv('data/subscriptions.csv')
        else:
            return pd.DataFrame(columns=['Client_Name', 'Category', 'Region', 'Amount', 'Date'])
    except Exception as e:
        st.error(f"Erreur lors du chargement des abonnements: {str(e)}")
        return pd.DataFrame(columns=['Client_Name', 'Category', 'Region', 'Amount', 'Date'])

# Main dashboard
def main_dashboard():
    """Main dashboard with KPIs and visualizations"""
    
    # Load data
    df = load_telecom_data()
    subscriptions_df = load_subscription_data()
    
    if df is None:
        st.error("❌ Impossible de charger les données. Veuillez vérifier le fichier 'data/internet_data.csv'")
        return
    
    # Key Performance Indicators
    st.markdown("### 📊 Indicateurs Clés de Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_subscribers = df['Total_Internet_Subscribers'].iloc[-1] / 1e6
        prev_subscribers = df['Total_Internet_Subscribers'].iloc[-2] / 1e6 if len(df) > 1 else total_subscribers
        growth_rate = ((total_subscribers - prev_subscribers) / prev_subscribers * 100) if prev_subscribers > 0 else 0
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Abonnés Internet</div>
            <div class="metric-value">{total_subscribers:.1f}M</div>
            <div class="metric-delta" style="color: {'green' if growth_rate >= 0 else 'red'}">
                {growth_rate:+.1f}% vs trimestre précédent
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        fiber_subscribers = df['Fiber_FTTH_Subscribers'].iloc[-1] / 1e6
        prev_fiber = df['Fiber_FTTH_Subscribers'].iloc[-2] / 1e6 if len(df) > 1 else fiber_subscribers
        fiber_growth = ((fiber_subscribers - prev_fiber) / prev_fiber * 100) if prev_fiber > 0 else 0
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Abonnés Fibre FTTH</div>
            <div class="metric-value">{fiber_subscribers:.2f}M</div>
            <div class="metric-delta" style="color: {'green' if fiber_growth >= 0 else 'red'}">
                {fiber_growth:+.1f}% vs trimestre précédent
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        mobile_4g = df['4G_Subscribers'].iloc[-1] / 1e6
        prev_4g = df['4G_Subscribers'].iloc[-2] / 1e6 if len(df) > 1 else mobile_4g
        mobile_4g_growth = ((mobile_4g - prev_4g) / prev_4g * 100) if prev_4g > 0 else 0
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Abonnés 4G Mobile</div>
            <div class="metric-value">{mobile_4g:.1f}M</div>
            <div class="metric-delta" style="color: {'green' if mobile_4g_growth >= 0 else 'red'}">
                {mobile_4g_growth:+.1f}% vs trimestre précédent
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        arpu = df['Average_Revenue_Per_User_DA'].iloc[-1]
        prev_arpu = df['Average_Revenue_Per_User_DA'].iloc[-2] if len(df) > 1 else arpu
        arpu_growth = ((arpu - prev_arpu) / prev_arpu * 100) if prev_arpu > 0 else 0
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">ARPU Moyen (DA)</div>
            <div class="metric-value">{arpu:,.0f}</div>
            <div class="metric-delta" style="color: {'green' if arpu_growth >= 0 else 'red'}">
                {arpu_growth:+.1f}% vs trimestre précédent
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Time Series Charts
    st.markdown("### 📈 Évolution des Abonnements par Technologie")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Subscribers Evolution
        fig_subscribers = go.Figure()
        
        fig_subscribers.add_trace(go.Scatter(
            x=df['Date'], 
            y=df['Total_Internet_Subscribers']/1e6,
            mode='lines+markers',
            name='Total Internet',
            line=dict(color='#002147', width=3),
            marker=dict(size=6)
        ))
        
        fig_subscribers.add_trace(go.Scatter(
            x=df['Date'], 
            y=df['4G_Subscribers']/1e6,
            mode='lines+markers',
            name='4G Mobile',
            line=dict(color='#00A859', width=2),
            marker=dict(size=4)
        ))
        
        fig_subscribers.add_trace(go.Scatter(
            x=df['Date'], 
            y=df['Fiber_FTTH_Subscribers']/1e6,
            mode='lines+markers',
            name='Fibre FTTH',
            line=dict(color='#FF6B35', width=2),
            marker=dict(size=4)
        ))
        
        fig_subscribers.update_layout(
            title='Évolution des Abonnés (Millions)',
            xaxis_title='Date',
            yaxis_title='Abonnés (Millions)',
            hovermode='x unified',
            template='plotly_white',
            height=400,
            legend=dict(x=0.02, y=0.98)
        )
        
        st.plotly_chart(fig_subscribers, use_container_width=True)
    
    with col2:
        # Technology Mix (Pie Chart)
        latest_data = df.iloc[-1]
        technologies = {
            'ADSL': latest_data['ADSL_Subscribers'],
            '4G Fixe': latest_data['Fixed_4G_LTE_Subscribers'],
            'Fibre FTTH': latest_data['Fiber_FTTH_Subscribers'],
            '4G Mobile': latest_data['4G_Subscribers']
        }
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=list(technologies.keys()),
            values=list(technologies.values()),
            hole=0.4,
            marker_colors=['#002147', '#00A859', '#FF6B35', '#FFA500']
        )])
        
        fig_pie.update_layout(
            title='Répartition par Technologie (Trimestre Actuel)',
            height=400,
            showlegend=True,
            legend=dict(x=0.85, y=0.5)
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Traffic and Revenue Analysis
    st.markdown("### 💰 Analyse du Trafic et des Revenus")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Traffic Evolution
        fig_traffic = go.Figure()
        
        fig_traffic.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Total_Traffic_Consumed']/1e12,
            mode='lines+markers',
            name='Trafic Total',
            line=dict(color='#002147', width=3),
            fill='tonexty',
            fillcolor='rgba(0, 33, 71, 0.1)'
        ))
        
        fig_traffic.update_layout(
            title='Évolution du Trafic Consommé (Téraoctets)',
            xaxis_title='Date',
            yaxis_title='Trafic (To)',
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig_traffic, use_container_width=True)
    
    with col2:
        # ARPU Evolution
        fig_arpu = go.Figure()
        
        fig_arpu.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Average_Revenue_Per_User_DA'],
            mode='lines+markers',
            name='ARPU',
            line=dict(color='#00A859', width=3),
            marker=dict(size=6)
        ))
        
        fig_arpu.update_layout(
            title='Évolution du Revenu Moyen par Utilisateur (DA)',
            xaxis_title='Date',
            yaxis_title='ARPU (DA)',
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig_arpu, use_container_width=True)
    
    # New subscriptions summary
    if len(subscriptions_df) > 0:
        st.markdown("### 📝 Résumé des Nouveaux Abonnements")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_new = len(subscriptions_df)
            st.metric("Nouveaux Abonnements", total_new)
        
        with col2:
            total_revenue = subscriptions_df['Amount'].sum()
            st.metric("Revenus Nouveaux Abonnés", f"{total_revenue:,.0f} DA")
        
        with col3:
            avg_revenue = subscriptions_df['Amount'].mean() if len(subscriptions_df) > 0 else 0
            st.metric("Revenu Moyen/Abonné", f"{avg_revenue:,.0f} DA")
        
        # Show recent subscriptions
        st.markdown("#### Abonnements Récents")
        recent_subs = subscriptions_df.sort_values('Date', ascending=False).head(5)
        st.dataframe(recent_subs, use_container_width=True)

if __name__ == "__main__":
    main_dashboard()