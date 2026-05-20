import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import datetime
import os

def show_data_page():
    """Data Management and Display Page"""
    
    st.markdown("""
    <div class="main-header">
        <h1>📊 Gestion des Données</h1>
        <p>Visualisation et gestion des données Algérie Télécom</p>
    </div>
    """, unsafe_allow_html=True)

    @st.cache_data
    def load_telecom_data():
        """Load and preprocess Algeria Telecom data"""
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
            df['Year'] = df['Date'].dt.year
            df['Quarter'] = df['Date'].dt.quarter
            
            df = df.reset_index(drop=True)
            df = df.sort_values('Date').reset_index(drop=True)
            df = df.fillna(0)
            
            return df
        except Exception as e:
            st.error(f"Erreur lors du chargement des données: {str(e)}")
            return None

    def load_subscription_data():
        """Load subscription data if exists"""
        try:
            if os.path.exists('data/subscriptions.csv'):
                return pd.read_csv('data/subscriptions.csv')
            else:
                return pd.DataFrame(columns=['Client_Name', 'Category', 'Region', 'Amount', 'Date'])
        except Exception as e:
            st.error(f"Erreur lors du chargement des abonnements: {str(e)}")
            return pd.DataFrame(columns=['Client_Name', 'Category', 'Region', 'Amount', 'Date'])

    def to_excel(df_list, sheet_names):
        """Convert multiple dataframes to Excel"""
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for df, sheet_name in zip(df_list, sheet_names):
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        output.seek(0)
        return output

    # Load data
    df_telecom = load_telecom_data()
    df_subscriptions = load_subscription_data()
    
    if df_telecom is None:
        st.error("Impossible de charger les données principales")
        return

    # Sidebar controls
    st.sidebar.markdown("### Options d'Affichage")
    
    data_source = st.sidebar.selectbox(
        "Source de Données",
        options=["Données Historiques", "Nouveaux Abonnements", "Données Combinées"],
        help="Choisir quelle source de données afficher"
    )
    
    show_summary = st.sidebar.checkbox("Afficher le Résumé", value=True)
    show_charts = st.sidebar.checkbox("Afficher les Graphiques", value=True)

    # Display historical data
    if data_source in ["Données Historiques", "Données Combinées"]:
        st.markdown("## 📈 Données Historiques Algérie Télécom")
        
        if show_summary:
            # Data summary
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Périodes de Données",
                    len(df_telecom),
                    help="Nombre total de trimestres"
                )
            
            with col2:
                date_range = f"{df_telecom['Date'].min().strftime('%Y-%m')} à {df_telecom['Date'].max().strftime('%Y-%m')}"
                st.metric(
                    "Période Couverte",
                    date_range
                )
            
            with col3:
                total_subscribers = df_telecom['Total_Internet_Subscribers'].iloc[-1] / 1e6
                st.metric(
                    "Total Abonnés",
                    f"{total_subscribers:.1f}M"
                )
            
            with col4:
                data_quality = (df_telecom.notna().sum().sum() / (len(df_telecom) * len(df_telecom.columns))) * 100
                st.metric(
                    "Qualité des Données",
                    f"{data_quality:.1f}%"
                )
        
        # Data filters
        st.markdown("### 🔍 Filtres et Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Year filter
            years_available = sorted(df_telecom['Year'].dropna().unique())
            selected_years = st.multiselect(
                "Années",
                options=years_available,
                default=years_available[-3:] if len(years_available) >= 3 else years_available
            )
        
        with col2:
            # Quarter filter
            quarters_available = [1, 2, 3, 4]
            selected_quarters = st.multiselect(
                "Trimestres",
                options=quarters_available,
                default=quarters_available
            )
        
        with col3:
            # Column selector
            numeric_columns = df_telecom.select_dtypes(include=[np.number]).columns.tolist()
            numeric_columns = [col for col in numeric_columns if col not in ['Year', 'Quarter']]
            
            selected_columns = st.multiselect(
                "Colonnes à Afficher",
                options=numeric_columns,
                default=numeric_columns[:6]
            )
        
        # Apply filters
        filtered_data = df_telecom[
            (df_telecom['Year'].isin(selected_years)) &
            (df_telecom['Quarter'].isin(selected_quarters))
        ].copy()
        
        # Display filtered data
        st.markdown("### 📋 Tableau des Données")
        
        display_columns = ['Period', 'Date', 'Year', 'Quarter'] + selected_columns
        display_data = filtered_data[display_columns]
        
        # Format numeric columns for better display
        formatted_data = display_data.copy()
        for col in selected_columns:
            if 'Subscribers' in col:
                formatted_data[col] = formatted_data[col].apply(lambda x: f"{x/1e6:.2f}M" if pd.notna(x) and x != 0 else "0")
            elif 'Traffic' in col:
                formatted_data[col] = formatted_data[col].apply(lambda x: f"{x/1e12:.2f}T" if pd.notna(x) and x != 0 else "0")
            elif 'Revenue' in col or 'ARPU' in col:
                formatted_data[col] = formatted_data[col].apply(lambda x: f"{x:,.0f} DA" if pd.notna(x) and x != 0 else "0 DA")
        
        st.dataframe(formatted_data, use_container_width=True, hide_index=True)
        
        # Charts
        if show_charts and len(filtered_data) > 0:
            st.markdown("### 📊 Visualisations des Données")
            
            # Time series chart
            if len(selected_columns) > 0:
                fig_ts = go.Figure()
                
                colors = ['#002147', '#00A859', '#FF6B35', '#8E44AD', '#E74C3C', '#F39C12']
                
                for i, col in enumerate(selected_columns[:6]):  # Limit to 6 series for readability
                    scale_factor = 1e6 if 'Subscribers' in col else 1e12 if 'Traffic' in col else 1
                    scale_label = 'M' if 'Subscribers' in col else 'T' if 'Traffic' in col else ''
                    
                    fig_ts.add_trace(go.Scatter(
                        x=filtered_data['Date'],
                        y=filtered_data[col] / scale_factor,
                        mode='lines+markers',
                        name=col.replace('_', ' '),
                        line=dict(color=colors[i % len(colors)], width=2),
                        marker=dict(size=4)
                    ))
                
                fig_ts.update_layout(
                    title='Évolution Temporelle des Métriques Sélectionnées',
                    xaxis_title='Date',
                    yaxis_title='Valeur',
                    hovermode='x unified',
                    template='plotly_white',
                    height=500,
                    legend=dict(x=0.02, y=0.98)
                )
                
                st.plotly_chart(fig_ts, use_container_width=True)

    # Display subscription data
    if data_source in ["Nouveaux Abonnements", "Données Combinées"]:
        st.markdown("## 📝 Nouveaux Abonnements")
        
        if len(df_subscriptions) > 0:
            if show_summary:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Abonnements", len(df_subscriptions))
                
                with col2:
                    total_revenue = df_subscriptions['Amount'].sum()
                    st.metric("Revenus Total", f"{total_revenue:,.0f} DA")
                
                with col3:
                    avg_amount = df_subscriptions['Amount'].mean()
                    st.metric("Montant Moyen", f"{avg_amount:,.0f} DA")
                
                with col4:
                    most_popular = df_subscriptions['Category'].mode().iloc[0] if len(df_subscriptions) > 0 else "N/A"
                    st.metric("Catégorie Populaire", most_popular)
            
            # Subscription filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                categories = ['Tous'] + list(df_subscriptions['Category'].unique())
                selected_category = st.selectbox("Catégorie", options=categories)
            
            with col2:
                regions = ['Tous'] + list(df_subscriptions['Region'].unique())
                selected_region = st.selectbox("Région", options=regions)
            
            with col3:
                # Date range
                if 'Date' in df_subscriptions.columns:
                    df_subscriptions['Date'] = pd.to_datetime(df_subscriptions['Date'])
                    date_range = st.date_input(
                        "Période",
                        value=(df_subscriptions['Date'].min(), df_subscriptions['Date'].max()),
                        min_value=df_subscriptions['Date'].min(),
                        max_value=df_subscriptions['Date'].max()
                    )
            
            # Apply subscription filters
            filtered_subs = df_subscriptions.copy()
            
            if selected_category != 'Tous':
                filtered_subs = filtered_subs[filtered_subs['Category'] == selected_category]
            
            if selected_region != 'Tous':
                filtered_subs = filtered_subs[filtered_subs['Region'] == selected_region]
            
            if len(date_range) == 2:
                filtered_subs = filtered_subs[
                    (filtered_subs['Date'] >= pd.to_datetime(date_range[0])) &
                    (filtered_subs['Date'] <= pd.to_datetime(date_range[1]))
                ]
            
            st.dataframe(
                filtered_subs.sort_values('Date' if 'Date' in filtered_subs.columns else filtered_subs.columns[0], ascending=False),
                use_container_width=True,
                hide_index=True
            )
            
            # Subscription charts
            if show_charts and len(filtered_subs) > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Category distribution
                    category_counts = filtered_subs['Category'].value_counts()
                    fig_cat = px.pie(
                        values=category_counts.values,
                        names=category_counts.index,
                        title='Répartition par Catégorie',
                        color_discrete_sequence=['#002147', '#00A859', '#FF6B35', '#8E44AD', '#E74C3C']
                    )
                    st.plotly_chart(fig_cat, use_container_width=True)
                
                with col2:
                    # Region distribution
                    region_counts = filtered_subs['Region'].value_counts().head(10)
                    fig_region = px.bar(
                        x=region_counts.values,
                        y=region_counts.index,
                        orientation='h',
                        title='Top 10 Régions',
                        color_discrete_sequence=['#00A859']
                    )
                    fig_region.update_layout(xaxis_title='Nombre d\'Abonnements', yaxis_title='Région')
                    st.plotly_chart(fig_region, use_container_width=True)
        else:
            st.info("Aucun nouvel abonnement enregistré")

    # Data export section
    st.markdown("## 📥 Export des Données")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # CSV export for historical data
        if st.button("📄 Export CSV - Données Historiques"):
            csv_historical = df_telecom.to_csv(index=False)
            st.download_button(
                label="Télécharger Données Historiques CSV",
                data=csv_historical,
                file_name=f"donnees_historiques_algerie_telecom_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        # CSV export for subscriptions
        if st.button("📄 Export CSV - Abonnements"):
            if len(df_subscriptions) > 0:
                csv_subscriptions = df_subscriptions.to_csv(index=False)
                st.download_button(
                    label="Télécharger Abonnements CSV",
                    data=csv_subscriptions,
                    file_name=f"nouveaux_abonnements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("Aucune donnée d'abonnement à exporter")
    
    with col3:
        # Excel export (combined)
        if st.button("📊 Export Excel - Tout"):
            excel_data = to_excel(
                [df_telecom, df_subscriptions] if len(df_subscriptions) > 0 else [df_telecom],
                ['Donnees_Historiques', 'Nouveaux_Abonnements'] if len(df_subscriptions) > 0 else ['Donnees_Historiques']
            )
            
            st.download_button(
                label="Télécharger Excel Complet",
                data=excel_data,
                file_name=f"algerie_telecom_complet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # Data quality report
    st.markdown("## 🔍 Rapport de Qualité des Données")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Données Historiques")
        
        # Missing values analysis
        missing_data = df_telecom.isnull().sum()
        missing_percent = (missing_data / len(df_telecom)) * 100
        
        quality_data = pd.DataFrame({
            'Colonne': missing_data.index,
            'Valeurs Manquantes': missing_data.values,
            'Pourcentage': missing_percent.values
        })
        
        quality_data = quality_data[quality_data['Valeurs Manquantes'] > 0]
        
        if len(quality_data) > 0:
            st.dataframe(quality_data, hide_index=True, use_container_width=True)
        else:
            st.success("✅ Aucune valeur manquante détectée")
        
        # Data types
        st.markdown("#### Types de Données")
        dtype_info = pd.DataFrame({
            'Colonne': df_telecom.dtypes.index,
            'Type': df_telecom.dtypes.values
        })
        st.dataframe(dtype_info, hide_index=True, use_container_width=True)
    
    with col2:
        st.markdown("### Nouveaux Abonnements")
        
        if len(df_subscriptions) > 0:
            # Data completeness
            completeness = (df_subscriptions.notna().sum() / len(df_subscriptions)) * 100
            
            completeness_data = pd.DataFrame({
                'Colonne': completeness.index,
                'Complétude (%)': completeness.values
            })
            
            st.dataframe(completeness_data, hide_index=True, use_container_width=True)
            
            # Duplicate check
            duplicates = df_subscriptions.duplicated().sum()
            if duplicates > 0:
                st.warning(f"⚠️ {duplicates} doublons détectés")
            else:
                st.success("✅ Aucun doublon détecté")
                
        else:
            st.info("Aucune donnée d'abonnement à analyser")

if __name__ == "__main__":
    show_data_page()