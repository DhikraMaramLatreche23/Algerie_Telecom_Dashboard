import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.ensemble import IsolationForest
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
import warnings
warnings.filterwarnings('ignore')

def show_analysis_page():
    """Advanced Analysis Page"""
    
    st.markdown("""
    <div class="main-header">
        <h1>📊 Analyse Avancée</h1>
        <p>Analyse statistique approfondie des données Algérie Télécom</p>
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

    def analyze_metric_deep_dive(df, metric_name, display_name):
        """Comprehensive analysis of a single metric"""
        
        data = df[metric_name]
        
        # Calculate key statistics
        current_value = data.iloc[-1]
        peak_value = data.max()
        lowest_value = data.min()
        total_growth = ((current_value - data.iloc[0]) / data.iloc[0]) * 100 if data.iloc[0] > 0 else 0
        years = (df['Date'].iloc[-1] - df['Date'].iloc[0]).days / 365.25
        cagr = ((current_value / data.iloc[0]) ** (1/years) - 1) * 100 if years > 0 and data.iloc[0] > 0 else 0
        qoq_growth = data.pct_change() * 100
        avg_qoq_growth = qoq_growth.mean()
        volatility = qoq_growth.std()
        
        return {
            'current_value': current_value,
            'peak_value': peak_value,
            'lowest_value': lowest_value,
            'total_growth': total_growth,
            'cagr': cagr,
            'avg_qoq_growth': avg_qoq_growth,
            'volatility': volatility,
            'qoq_growth': qoq_growth
        }

    def detect_anomalies(df, metric_name):
        """Detect anomalies in time series data"""
        data = df[metric_name]
        
        # Z-score method
        z_scores = np.abs(stats.zscore(data))
        statistical_outliers = z_scores > 2.5
        
        # Isolation Forest
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        isolation_outliers = iso_forest.fit_predict(data.values.reshape(-1, 1)) == -1
        
        # IQR method
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        iqr_outliers = (data < (Q1 - 1.5 * IQR)) | (data > (Q3 + 1.5 * IQR))
        
        # Combined anomalies
        combined_anomalies = (statistical_outliers.astype(int) + 
                             isolation_outliers.astype(int) + 
                             iqr_outliers.astype(int)) >= 2
        
        return {
            'statistical_outliers': statistical_outliers,
            'isolation_outliers': isolation_outliers,
            'iqr_outliers': iqr_outliers,
            'combined_anomalies': combined_anomalies,
            'z_scores': z_scores
        }

    def perform_stationarity_test(data):
        """Perform stationarity tests"""
        try:
            adf_stat, adf_pvalue, _, _, adf_critical, _ = adfuller(data)
            is_stationary = adf_pvalue < 0.05
            
            return {
                'adf_statistic': adf_stat,
                'adf_pvalue': adf_pvalue,
                'adf_critical_values': adf_critical,
                'is_stationary': is_stationary
            }
        except Exception as e:
            return None

    # Load data
    df = load_telecom_data()
    if df is None:
        st.error("Impossible de charger les données")
        return

    # Sidebar controls
    st.sidebar.markdown("### Paramètres d'Analyse")
    
    analysis_metrics = {
        'Total_Internet_Subscribers': 'Total Abonnés Internet',
        'Fiber_FTTH_Subscribers': 'Abonnés Fibre FTTH',
        '4G_Subscribers': 'Abonnés 4G Mobile',
        'ADSL_Subscribers': 'Abonnés ADSL',
        'Total_Traffic_Consumed': 'Trafic Total Consommé',
        'Average_Revenue_Per_User_DA': 'ARPU Moyen'
    }
    
    selected_metric = st.sidebar.selectbox(
        "Métrique à Analyser",
        options=list(analysis_metrics.keys()),
        format_func=lambda x: analysis_metrics[x]
    )
    
    analysis_type = st.sidebar.multiselect(
        "Types d'Analyse",
        options=[
            "Statistiques Descriptives",
            "Analyse de Tendance",
            "Détection d'Anomalies",
            "Décomposition Saisonnière",
            "Tests de Stationnarité",
            "Analyse de Corrélation"
        ],
        default=[
            "Statistiques Descriptives",
            "Analyse de Tendance",
            "Détection d'Anomalies"
        ]
    )

    # Main analysis
    st.markdown(f"## 🔍 Analyse: {analysis_metrics[selected_metric]}")
    
    # Get analysis data
    metric_analysis = analyze_metric_deep_dive(df, selected_metric, analysis_metrics[selected_metric])
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    scale_factor = 1e6 if 'Subscribers' in selected_metric else 1e12 if 'Traffic' in selected_metric else 1
    scale_label = 'M' if 'Subscribers' in selected_metric else 'T' if 'Traffic' in selected_metric else ''
    
    with col1:
        st.metric(
            "Valeur Actuelle",
            f"{metric_analysis['current_value']/scale_factor:.2f}{scale_label}",
            delta=f"{metric_analysis['total_growth']:+.1f}% total"
        )
    
    with col2:
        st.metric(
            "Pic Historique",
            f"{metric_analysis['peak_value']/scale_factor:.2f}{scale_label}"
        )
    
    with col3:
        st.metric(
            "CAGR",
            f"{metric_analysis['cagr']:+.1f}%/an"
        )
    
    with col4:
        st.metric(
            "Volatilité",
            f"{metric_analysis['volatility']:.1f}%"
        )

    # Analysis sections
    if "Statistiques Descriptives" in analysis_type:
        st.markdown("### 📈 Statistiques Descriptives")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution plot
            data = df[selected_metric]
            
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(
                x=data/scale_factor,
                nbinsx=15,
                name='Distribution',
                marker_color='#002147',
                opacity=0.7
            ))
            
            fig_hist.update_layout(
                title='Distribution des Valeurs',
                xaxis_title=f'Valeur ({scale_label})',
                yaxis_title='Fréquence',
                template='plotly_white',
                height=400
            )
            
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Box plot
            fig_box = go.Figure()
            fig_box.add_trace(go.Box(
                y=data/scale_factor,
                name=analysis_metrics[selected_metric],
                marker_color='#00A859'
            ))
            
            fig_box.update_layout(
                title='Analyse des Quartiles',
                yaxis_title=f'Valeur ({scale_label})',
                template='plotly_white',
                height=400
            )
            
            st.plotly_chart(fig_box, use_container_width=True)
        
        # Summary statistics table
        stats_data = {
            'Statistique': ['Moyenne', 'Médiane', 'Écart-type', 'Min', 'Max', 'Q1', 'Q3', 'Asymétrie', 'Aplatissement'],
            'Valeur': [
                f"{data.mean()/scale_factor:.2f}{scale_label}",
                f"{data.median()/scale_factor:.2f}{scale_label}",
                f"{data.std()/scale_factor:.2f}{scale_label}",
                f"{data.min()/scale_factor:.2f}{scale_label}",
                f"{data.max()/scale_factor:.2f}{scale_label}",
                f"{data.quantile(0.25)/scale_factor:.2f}{scale_label}",
                f"{data.quantile(0.75)/scale_factor:.2f}{scale_label}",
                f"{stats.skew(data):.3f}",
                f"{stats.kurtosis(data):.3f}"
            ]
        }
        
        st.dataframe(pd.DataFrame(stats_data), hide_index=True, use_container_width=True)

    if "Analyse de Tendance" in analysis_type:
        st.markdown("### 📊 Analyse de Tendance")
        
        data = df[selected_metric]
        
        # Trend analysis plot
        fig_trend = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Évolution Temporelle avec Tendance',
                'Taux de Croissance Trimestrielle',
                'Moyennes Mobiles',
                'Analyse des Résidus'
            )
        )
        
        # Historical data with trend
        fig_trend.add_trace(
            go.Scatter(x=df['Date'], y=data/scale_factor, mode='lines+markers', 
                      name='Données', line=dict(color='#002147')),
            row=1, col=1
        )
        
        # Add trend line
        z = np.polyfit(range(len(data)), data, 1)
        p = np.poly1d(z)
        fig_trend.add_trace(
            go.Scatter(x=df['Date'], y=p(range(len(data)))/scale_factor, 
                      mode='lines', name='Tendance', line=dict(color='#FF6B35', dash='dash')),
            row=1, col=1
        )
        
        # Growth rates
        growth_rates = metric_analysis['qoq_growth'][1:]
        colors = ['green' if x >= 0 else 'red' for x in growth_rates]
        fig_trend.add_trace(
            go.Bar(x=df['Date'][1:], y=growth_rates, marker_color=colors, 
                   name='Croissance QoQ', opacity=0.7),
            row=1, col=2
        )
        
        # Moving averages
        ma_4 = data.rolling(window=4).mean()
        ma_8 = data.rolling(window=8).mean()
        
        fig_trend.add_trace(
            go.Scatter(x=df['Date'], y=data/scale_factor, mode='lines', 
                      name='Original', line=dict(color='#002147', width=1), opacity=0.5),
            row=2, col=1
        )
        fig_trend.add_trace(
            go.Scatter(x=df['Date'], y=ma_4/scale_factor, mode='lines', 
                      name='MA-4T', line=dict(color='#00A859', width=2)),
            row=2, col=1
        )
        if len(data) >= 8:
            fig_trend.add_trace(
                go.Scatter(x=df['Date'], y=ma_8/scale_factor, mode='lines', 
                          name='MA-8T', line=dict(color='#FF6B35', width=2)),
                row=2, col=1
            )
        
        # Residuals analysis
        residuals = data - p(range(len(data)))
        fig_trend.add_trace(
            go.Scatter(x=df['Date'], y=residuals/scale_factor, mode='lines+markers', 
                      name='Résidus', line=dict(color='#8E44AD')),
            row=2, col=2
        )
        
        fig_trend.update_layout(height=600, showlegend=True, template='plotly_white')
        st.plotly_chart(fig_trend, use_container_width=True)

    if "Détection d'Anomalies" in analysis_type:
        st.markdown("### 🚨 Détection d'Anomalies")
        
        anomaly_results = detect_anomalies(df, selected_metric)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Anomalies Z-score", anomaly_results['statistical_outliers'].sum())
        with col2:
            st.metric("Isolation Forest", anomaly_results['isolation_outliers'].sum())
        with col3:
            st.metric("Anomalies IQR", anomaly_results['iqr_outliers'].sum())
        
        # Anomaly visualization
        data = df[selected_metric]
        fig_anomaly = go.Figure()
        
        # Normal data
        fig_anomaly.add_trace(go.Scatter(
            x=df['Date'], 
            y=data/scale_factor,
            mode='lines+markers',
            name='Données Normales',
            line=dict(color='#002147'),
            marker=dict(size=4)
        ))
        
        # Highlight anomalies
        if anomaly_results['combined_anomalies'].any():
            anomaly_data = df.loc[anomaly_results['combined_anomalies']]
            fig_anomaly.add_trace(go.Scatter(
                x=anomaly_data['Date'],
                y=anomaly_data[selected_metric]/scale_factor,
                mode='markers',
                name='Anomalies Détectées',
                marker=dict(color='red', size=10, symbol='x')
            ))
        
        fig_anomaly.update_layout(
            title='Détection d\'Anomalies dans les Données',
            xaxis_title='Date',
            yaxis_title=f'{analysis_metrics[selected_metric]} ({scale_label})',
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig_anomaly, use_container_width=True)

    if "Décomposition Saisonnière" in analysis_type:
        st.markdown("### 📅 Décomposition Saisonnière")
        
        data = df[selected_metric]
        
        if len(data) >= 8:  # Need at least 2 cycles for quarterly data
            try:
                decomposition = seasonal_decompose(data, model='additive', period=4)
                
                fig_decomp = make_subplots(
                    rows=4, cols=1,
                    subplot_titles=('Original', 'Tendance', 'Saisonnalité', 'Résidus'),
                    vertical_spacing=0.08
                )
                
                fig_decomp.add_trace(
                    go.Scatter(x=df['Date'], y=decomposition.observed/scale_factor, 
                              name='Original', line=dict(color='#002147')),
                    row=1, col=1
                )
                
                fig_decomp.add_trace(
                    go.Scatter(x=df['Date'], y=decomposition.trend/scale_factor, 
                              name='Tendance', line=dict(color='#00A859')),
                    row=2, col=1
                )
                
                fig_decomp.add_trace(
                    go.Scatter(x=df['Date'], y=decomposition.seasonal/scale_factor, 
                              name='Saisonnalité', line=dict(color='#FF6B35')),
                    row=3, col=1
                )
                
                fig_decomp.add_trace(
                    go.Scatter(x=df['Date'], y=decomposition.resid/scale_factor, 
                              name='Résidus', line=dict(color='#8E44AD')),
                    row=4, col=1
                )
                
                fig_decomp.update_layout(
                    height=800,
                    showlegend=False,
                    template='plotly_white'
                )
                
                st.plotly_chart(fig_decomp, use_container_width=True)
                
                # Seasonal strength
                seasonal_strength = np.var(decomposition.seasonal) / np.var(decomposition.resid + decomposition.seasonal)
                st.info(f"Force Saisonnière: {seasonal_strength:.3f}")
                
            except Exception as e:
                st.error(f"Erreur dans la décomposition saisonnière: {str(e)}")
        else:
            st.warning("Pas assez de données pour la décomposition saisonnière (minimum 8 périodes)")

    if "Tests de Stationnarité" in analysis_type:
        st.markdown("### 🔬 Tests de Stationnarité")
        
        data = df[selected_metric]
        stationarity_result = perform_stationarity_test(data)
        
        if stationarity_result:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Test de Dickey-Fuller Augmenté")
                if stationarity_result['is_stationary']:
                    st.success(f"✅ Série stationnaire (p-value: {stationarity_result['adf_pvalue']:.4f})")
                else:
                    st.warning(f"⚠️ Série non-stationnaire (p-value: {stationarity_result['adf_pvalue']:.4f})")
                
                st.write(f"Statistique ADF: {stationarity_result['adf_statistic']:.4f}")
            
            with col2:
                st.markdown("#### Valeurs Critiques ADF")
                for key, value in stationarity_result['adf_critical_values'].items():
                    st.write(f"{key}: {value:.4f}")

    if "Analyse de Corrélation" in analysis_type:
        st.markdown("### 🔗 Analyse de Corrélation")
        
        # Correlation matrix
        numeric_cols = ['Total_Internet_Subscribers', 'Fiber_FTTH_Subscribers', 
                       '4G_Subscribers', 'ADSL_Subscribers', 
                       'Total_Traffic_Consumed', 'Average_Revenue_Per_User_DA']
        
        correlation_data = df[numeric_cols].corr()
        
        # Plotly heatmap
        fig_corr = go.Figure(data=go.Heatmap(
            z=correlation_data.values,
            x=[analysis_metrics.get(col, col) for col in correlation_data.columns],
            y=[analysis_metrics.get(col, col) for col in correlation_data.index],
            colorscale='RdBu',
            zmid=0,
            text=correlation_data.values,
            texttemplate="%{text:.2f}",
            textfont={"size": 10}
        ))
        
        fig_corr.update_layout(
            title='Matrice de Corrélation',
            template='plotly_white',
            height=500
        )
        
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Strongest correlations
        st.markdown("#### Corrélations les Plus Fortes")
        
        # Get correlations with selected metric
        selected_corr = correlation_data[selected_metric].abs().sort_values(ascending=False)
        selected_corr = selected_corr[selected_corr.index != selected_metric]  # Remove self-correlation
        
        for metric, corr_value in selected_corr.head(3).items():
            corr_direction = "positive" if correlation_data[selected_metric][metric] > 0 else "négative"
            st.write(f"• **{analysis_metrics.get(metric, metric)}**: {corr_value:.3f} (corrélation {corr_direction})")

    # Export analysis results
    st.markdown("### 📥 Export des Résultats")
    
    if st.button("Générer Rapport d'Analyse"):
        # Create analysis report
        report_data = {
            'Métrique': analysis_metrics[selected_metric],
            'Période d\'analyse': f"{df['Date'].min().strftime('%Y-%m')} à {df['Date'].max().strftime('%Y-%m')}",
            'Valeur actuelle': f"{metric_analysis['current_value']/scale_factor:.2f}{scale_label}",
            'Croissance totale': f"{metric_analysis['total_growth']:+.1f}%",
            'CAGR': f"{metric_analysis['cagr']:+.2f}%",
            'Volatilité': f"{metric_analysis['volatility']:.1f}%",
            'Croissance QoQ moyenne': f"{metric_analysis['avg_qoq_growth']:+.2f}%"
        }
        
        report_df = pd.DataFrame(list(report_data.items()), columns=['Indicateur', 'Valeur'])
        
        csv_data = report_df.to_csv(index=False)
        st.download_button(
            label="📄 Télécharger Rapport CSV",
            data=csv_data,
            file_name=f"analyse_{selected_metric}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        st.success("✅ Rapport d'analyse généré!")
        st.dataframe(report_df, hide_index=True, use_container_width=True)

if __name__ == "__main__":
    show_analysis_page()