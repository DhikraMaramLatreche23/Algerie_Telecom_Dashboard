import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
warnings.filterwarnings('ignore')

def show_forecasting_page():
    """Advanced Forecasting Page"""
    
    st.markdown("""
    <div class="main-header">
        <h1>🔮 Prévisions Avancées</h1>
        <p>Modèles de prévision pour l'évolution des abonnements</p>
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

    def create_forecast_model(data, model_type, forecast_periods=8):
        """Create forecast using different models"""
        try:
            if model_type == "ARIMA":
                model = ARIMA(data, order=(1, 1, 1))
                fitted_model = model.fit()
                forecast = fitted_model.forecast(steps=forecast_periods)
                confidence_int = fitted_model.get_forecast(steps=forecast_periods).conf_int()
                
                return {
                    'forecast': forecast,
                    'lower_bound': confidence_int.iloc[:, 0],
                    'upper_bound': confidence_int.iloc[:, 1],
                    'model': fitted_model,
                    'mae': None
                }
                
            elif model_type == "SARIMAX":
                model = SARIMAX(data, order=(1, 1, 1), seasonal_order=(1, 1, 1, 4))
                fitted_model = model.fit(disp=False)
                forecast = fitted_model.forecast(steps=forecast_periods)
                confidence_int = fitted_model.get_forecast(steps=forecast_periods).conf_int()
                
                return {
                    'forecast': forecast,
                    'lower_bound': confidence_int.iloc[:, 0],
                    'upper_bound': confidence_int.iloc[:, 1],
                    'model': fitted_model,
                    'mae': None
                }
                
            elif model_type == "Exponential Smoothing":
                model = ExponentialSmoothing(data, seasonal='add', seasonal_periods=4)
                fitted_model = model.fit()
                forecast = fitted_model.forecast(forecast_periods)
                
                # Simple confidence interval estimation
                residuals = fitted_model.resid
                std_error = np.std(residuals)
                
                return {
                    'forecast': forecast,
                    'lower_bound': forecast - 1.96 * std_error,
                    'upper_bound': forecast + 1.96 * std_error,
                    'model': fitted_model,
                    'mae': None
                }
                
            elif model_type == "Linear Regression":
                X = np.array(range(len(data))).reshape(-1, 1)
                y = data.values
                
                model = LinearRegression()
                model.fit(X, y)
                
                future_X = np.array(range(len(data), len(data) + forecast_periods)).reshape(-1, 1)
                forecast = model.predict(future_X)
                
                # Calculate residuals for confidence interval
                y_pred = model.predict(X)
                residuals = y - y_pred
                std_error = np.std(residuals)
                
                return {
                    'forecast': pd.Series(forecast),
                    'lower_bound': pd.Series(forecast - 1.96 * std_error),
                    'upper_bound': pd.Series(forecast + 1.96 * std_error),
                    'model': model,
                    'mae': mean_absolute_error(y, y_pred)
                }
                
            elif model_type == "Random Forest":
                # Create lag features
                lag_features = []
                for i in range(1, min(5, len(data))):
                    lag_features.append(data.shift(i))
                
                X = pd.concat(lag_features, axis=1).dropna()
                y = data[len(data) - len(X):]
                
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X, y)
                
                # Generate forecast
                forecast_values = []
                last_values = list(data.tail(4))
                
                for _ in range(forecast_periods):
                    pred = model.predict([last_values[-4:]])[0]
                    forecast_values.append(pred)
                    last_values.append(pred)
                
                # Simple confidence interval
                y_pred = model.predict(X)
                residuals = y - y_pred
                std_error = np.std(residuals)
                
                forecast_series = pd.Series(forecast_values)
                
                return {
                    'forecast': forecast_series,
                    'lower_bound': forecast_series - 1.96 * std_error,
                    'upper_bound': forecast_series + 1.96 * std_error,
                    'model': model,
                    'mae': mean_absolute_error(y, y_pred)
                }
                
        except Exception as e:
            st.error(f"Erreur dans le modèle {model_type}: {str(e)}")
            return None

    # Load data
    df = load_telecom_data()
    if df is None:
        st.error("Impossible de charger les données")
        return

    # Sidebar for model selection
    st.sidebar.markdown("### Paramètres de Prévision")
    
    # Metric selection
    forecast_metrics = {
        'Total_Internet_Subscribers': 'Total Abonnés Internet',
        'Fiber_FTTH_Subscribers': 'Abonnés Fibre FTTH',
        '4G_Subscribers': 'Abonnés 4G Mobile',
        'Total_Traffic_Consumed': 'Trafic Total Consommé',
        'Average_Revenue_Per_User_DA': 'ARPU Moyen'
    }
    
    selected_metric = st.sidebar.selectbox(
        "Métrique à Prévoir",
        options=list(forecast_metrics.keys()),
        format_func=lambda x: forecast_metrics[x]
    )
    
    # Model selection
    model_options = ["ARIMA", "SARIMAX", "Exponential Smoothing", "Linear Regression", "Random Forest"]
    selected_models = st.sidebar.multiselect(
        "Modèles de Prévision",
        options=model_options,
        default=["ARIMA", "Linear Regression"]
    )
    
    # Forecast horizon
    forecast_periods = st.sidebar.slider(
        "Périodes à Prévoir",
        min_value=2,
        max_value=12,
        value=8,
        help="Nombre de trimestres à prévoir"
    )
    
    # Year selection for display
    years_to_show = st.sidebar.slider(
        "Années Historiques à Afficher",
        min_value=2,
        max_value=len(df),
        value=min(5, len(df))
    )

    if not selected_models:
        st.warning("Veuillez sélectionner au moins un modèle de prévision")
        return

    # Main content
    st.markdown(f"### Prévision: {forecast_metrics[selected_metric]}")
    
    # Get data for selected metric
    data = df[selected_metric]
    
    # Filter data for display
    display_data = data.tail(years_to_show * 4)  # 4 quarters per year
    display_dates = df['Date'].tail(years_to_show * 4)
    
    # Create future dates
    last_date = df['Date'].iloc[-1]
    future_dates = pd.date_range(
        start=last_date + pd.DateOffset(months=3),
        periods=forecast_periods,
        freq='Q'
    )
    
    # Generate forecasts
    forecasts = {}
    for model_name in selected_models:
        with st.spinner(f"Génération des prévisions avec {model_name}..."):
            forecast_result = create_forecast_model(data, model_name, forecast_periods)
            if forecast_result:
                forecasts[model_name] = forecast_result
    
    if not forecasts:
        st.error("Aucune prévision n'a pu être générée")
        return
    
    # Visualization
    fig = go.Figure()
    
    # Historical data
    scale_factor = 1e6 if 'Subscribers' in selected_metric else 1e12 if 'Traffic' in selected_metric else 1
    scale_label = 'Millions' if 'Subscribers' in selected_metric else 'Téraoctets' if 'Traffic' in selected_metric else 'DA'
    
    fig.add_trace(go.Scatter(
        x=display_dates,
        y=display_data / scale_factor,
        mode='lines+markers',
        name='Données Historiques',
        line=dict(color='#002147', width=3),
        marker=dict(size=6)
    ))
    
    # Forecasts
    colors = ['#00A859', '#FF6B35', '#8E44AD', '#E74C3C', '#F39C12']
    
    for i, (model_name, forecast_data) in enumerate(forecasts.items()):
        color = colors[i % len(colors)]
        
        # Main forecast line
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=forecast_data['forecast'] / scale_factor,
            mode='lines+markers',
            name=f'{model_name}',
            line=dict(color=color, width=2, dash='dash'),
            marker=dict(size=4)
        ))
        
        # Confidence interval
        fig.add_trace(go.Scatter(
            x=list(future_dates) + list(future_dates[::-1]),
            y=list(forecast_data['upper_bound'] / scale_factor) + list(forecast_data['lower_bound'][::-1] / scale_factor),
            fill='tonexty' if i == 0 else 'none',
            fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name=f'{model_name} - Intervalle de Confiance',
            showlegend=False
        ))
    
    fig.update_layout(
        title=f'Prévision: {forecast_metrics[selected_metric]}',
        xaxis_title='Date',
        yaxis_title=f'{forecast_metrics[selected_metric]} ({scale_label})',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(x=0.02, y=0.98)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Forecast summary table
    st.markdown("### Résumé des Prévisions")
    
    summary_data = []
    current_value = data.iloc[-1]
    
    for model_name, forecast_data in forecasts.items():
        forecast_final = forecast_data['forecast'].iloc[-1]
        growth_rate = ((forecast_final - current_value) / current_value) * 100
        
        summary_data.append({
            'Modèle': model_name,
            'Valeur Actuelle': f"{current_value / scale_factor:.2f} {scale_label}",
            f'Prévision ({forecast_periods} trimestres)': f"{forecast_final / scale_factor:.2f} {scale_label}",
            'Croissance Prévue': f"{growth_rate:+.1f}%",
            'MAE (si disponible)': f"{forecast_data['mae']:.0f}" if forecast_data['mae'] else "N/A"
        })
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    # Model comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Analyse de Croissance")
        for model_name, forecast_data in forecasts.items():
            forecast_values = forecast_data['forecast']
            current_val = current_value
            final_val = forecast_values.iloc[-1]
            
            # Calculate CAGR
            periods_per_year = 4  # Quarterly data
            years = forecast_periods / periods_per_year
            cagr = ((final_val / current_val) ** (1/years) - 1) * 100 if years > 0 and current_val > 0 else 0
            
            st.metric(
                f"CAGR {model_name}",
                f"{cagr:.1f}%",
                delta=f"{((final_val - current_val) / current_val * 100):+.1f}% total"
            )
    
    with col2:
        st.markdown("#### Variance des Prévisions")
        if len(forecasts) > 1:
            final_forecasts = [forecast_data['forecast'].iloc[-1] for forecast_data in forecasts.values()]
            forecast_std = np.std(final_forecasts)
            forecast_mean = np.mean(final_forecasts)
            coefficient_variation = (forecast_std / forecast_mean) * 100 if forecast_mean > 0 else 0
            
            st.metric("Écart-Type", f"{forecast_std / scale_factor:.2f} {scale_label}")
            st.metric("Coefficient de Variation", f"{coefficient_variation:.1f}%")
            
            if coefficient_variation < 5:
                st.success("✅ Prévisions convergentes (faible variance)")
            elif coefficient_variation < 15:
                st.warning("⚠️ Variance modérée entre les modèles")
            else:
                st.error("❌ Forte divergence entre les modèles")
    
        # Detailed forecast table
    st.markdown("### Prévisions Détaillées par Trimestre")
    
    detailed_data = []
    for i, date in enumerate(future_dates):
        # compute quarter manually
        quarter = (date.month - 1) // 3 + 1
        row = {'Trimestre': f"{date.year}-T{quarter}"}
        for model_name, forecast_data in forecasts.items():
            value = forecast_data['forecast'].iloc[i] / scale_factor
            lower = forecast_data['lower_bound'].iloc[i] / scale_factor
            upper = forecast_data['upper_bound'].iloc[i] / scale_factor
            row[f'{model_name}'] = f"{value:.2f}"
            row[f'{model_name} (Min-Max)'] = f"{lower:.2f} - {upper:.2f}"
        detailed_data.append(row)
    
    detailed_df = pd.DataFrame(detailed_data)
    st.dataframe(detailed_df, use_container_width=True, hide_index=True)

    
    # Model performance comparison chart
    if len(forecasts) > 1:
        st.markdown("### Comparaison des Modèles")
        
        fig_comparison = go.Figure()
        
        for model_name, forecast_data in forecasts.items():
            fig_comparison.add_trace(go.Scatter(
                x=future_dates,
                y=forecast_data['forecast'] / scale_factor,
                mode='lines+markers',
                name=model_name,
                line=dict(width=3)
            ))
        
        fig_comparison.update_layout(
            title='Comparaison des Prévisions par Modèle',
            xaxis_title='Date',
            yaxis_title=f'Valeur Prévue ({scale_label})',
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig_comparison, use_container_width=True)
    
    # Export functionality
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Télécharger les Prévisions"):
            csv_data = detailed_df.to_csv(index=False)
            st.download_button(
                label="Télécharger CSV",
                data=csv_data,
                file_name=f"previsions_{selected_metric}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📊 Générer Rapport"):
            # Create comprehensive report
            report_data = {
                'Métrique': forecast_metrics[selected_metric],
                'Modèles utilisés': ', '.join(selected_models),
                'Périodes prévues': f"{forecast_periods} trimestres",
                'Valeur actuelle': f"{current_value / scale_factor:.2f} {scale_label}",
                'Date génération': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Add model-specific results
            for model_name, forecast_data in forecasts.items():
                final_forecast = forecast_data['forecast'].iloc[-1]
                growth = ((final_forecast - current_value) / current_value) * 100
                report_data[f'{model_name} - Prévision finale'] = f"{final_forecast / scale_factor:.2f} {scale_label}"
                report_data[f'{model_name} - Croissance'] = f"{growth:+.1f}%"
            
            report_df = pd.DataFrame(list(report_data.items()), columns=['Paramètre', 'Valeur'])
            
            csv_report = report_df.to_csv(index=False)
            st.download_button(
                label="Télécharger Rapport",
                data=csv_report,
                file_name=f"rapport_previsions_{selected_metric}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    show_forecasting_page()