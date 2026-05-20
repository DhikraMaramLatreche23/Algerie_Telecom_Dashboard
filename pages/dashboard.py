import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def load_data():
    """Load and preprocess data"""
    try:
        df_raw = pd.read_csv('data/internet_data.csv', index_col=0)
        df = df_raw.T
        
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
        
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace(' ', '').str.replace(',', '').str.replace('**', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        def parse_period(period_str):
            try:
                year, quarter = period_str.split('_T')
                quarter_month = {'1': '01', '2': '04', '3': '07', '4': '10'}
                return pd.to_datetime(f"{year}-{quarter_month[quarter]}-01")
            except:
                return pd.NaT
        
        df['Period'] = df.index
        df['Date'] = df.index.map(parse_period)
        df = df.sort_values('Date').reset_index(drop=True)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def main():
    st.title("📊 Algérie Télécom - Main Dashboard")
    
    df = load_data()
    
    if df is not None:
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            current_subs = df['Total_Internet_Subscribers'].iloc[-1]
            growth = ((current_subs - df['Total_Internet_Subscribers'].iloc[0]) / df['Total_Internet_Subscribers'].iloc[0]) * 100
            st.metric("Total Subscribers", f"{current_subs/1e6:.2f}M", f"{growth:+.1f}%")
        
        with col2:
            fiber_subs = df['Fiber_FTTH_Subscribers'].fillna(0).iloc[-1]
            st.metric("Fiber Subscribers", f"{fiber_subs/1e3:.0f}K")
        
        with col3:
            mobile_4g = df['4G_Subscribers'].iloc[-1]
            st.metric("4G Mobile", f"{mobile_4g/1e6:.2f}M")
        
        with col4:
            traffic = df['Total_Traffic_Consumed'].iloc[-1]
            st.metric("Data Traffic", f"{traffic/1e12:.2f}T units")
        
        # Technology Evolution
        st.subheader("Technology Adoption Over Time")
        
        fig = go.Figure()
        technologies = [
            ('Total_Internet_Subscribers', 'Total', '#002147'),
            ('ADSL_Subscribers', 'ADSL', '#E74C3C'),
            ('Fiber_FTTH_Subscribers', 'Fiber', '#00A859'),
            ('4G_Subscribers', '4G Mobile', '#9B59B6')
        ]
        
        for col, name, color in technologies:
            data = df[col].fillna(0) if col == 'Fiber_FTTH_Subscribers' else df[col]
            fig.add_trace(go.Scatter(x=df['Date'], y=data/1e6, name=name, line=dict(color=color, width=3)))
        
        fig.update_layout(height=400, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
        
        # Market Share
        st.subheader("Fixed Internet Market Share")
        
        total_fixed = df['ADSL_Subscribers'] + df['Fixed_4G_LTE_Subscribers'] + df['Fiber_FTTH_Subscribers'].fillna(0)
        fig_share = make_subplots(specs=[[{"secondary_y": False}]])
        
        technologies_share = [
            ('ADSL_Subscribers', 'ADSL', '#E74C3C'),
            ('Fixed_4G_LTE_Subscribers', 'Fixed 4G', '#3498DB'),
            ('Fiber_FTTH_Subscribers', 'Fiber', '#00A859')
        ]
        
        for col, name, color in technologies_share:
            share = (df[col].fillna(0) / total_fixed * 100)
            fig_share.add_trace(go.Scatter(x=df['Date'], y=share, name=name, line=dict(color=color, width=3)))
        
        fig_share.update_layout(height=400, template="plotly_white")
        st.plotly_chart(fig_share, use_container_width=True)

if __name__ == "__main__":
    main()