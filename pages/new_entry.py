import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go

def show_new_entry_page():
    """New Entry Page for adding subscription data"""
    
    st.markdown("""
    <div class="main-header">
        <h1>📝 Nouveau Abonnement</h1>
        <p>Ajouter un nouvel abonnement Internet</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Load existing subscription data
    def load_subscriptions():
        """Load existing subscription data"""
        try:
            if os.path.exists('data/subscriptions.csv'):
                return pd.read_csv('data/subscriptions.csv')
            else:
                return pd.DataFrame(columns=['Client_Name', 'Category', 'Region', 'Amount', 'Date', 'Entry_DateTime'])
        except Exception as e:
            st.error(f"Erreur lors du chargement: {str(e)}")
            return pd.DataFrame(columns=['Client_Name', 'Category', 'Region', 'Amount', 'Date', 'Entry_DateTime'])
    
    def save_subscription(new_data):
        """Save new subscription to CSV"""
        try:
            df_existing = load_subscriptions()
            df_new = pd.DataFrame([new_data])
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined.to_csv('data/subscriptions.csv', index=False)
            return True
        except Exception as e:
            st.error(f"Erreur lors de la sauvegarde: {str(e)}")
            return False
    
    # Form for new entry
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📋 Informations Abonnement")
            
            with st.form("subscription_form"):
                # Client information
                client_name = st.text_input(
                    "Nom du Client *",
                    placeholder="Ex: Ahmed Benali",
                    help="Nom complet du client"
                )
                
                # Subscription category
                category = st.selectbox(
                    "Catégorie d'Abonnement *",
                    options=["", "ADSL", "4G Fixe", "Fibre FTTH", "4G Mobile", "3G Mobile"],
                    help="Type de connexion Internet"
                )
                
                # Wilaya/Region
                regions = [
                    "", "Alger", "Oran", "Constantine", "Batna", "Djelfa", "Sétif", 
                    "Annaba", "Sidi Bel Abbès", "Biskra", "Tébessa", "El Oued", 
                    "Skikda", "Tiaret", "Béjaïa", "Tlemcen", "Ouargla", "Blida",
                    "Jijel", "Relizane", "Mascara", "M'Sila", "Oum El Bouaghi",
                    "Laghouat", "El Tarf", "Khenchela", "Souk Ahras", "Bouira",
                    "Médéa", "Tindouf", "Chlef", "Ghardaïa", "Aïn Defla"
                ]
                
                region = st.selectbox(
                    "Wilaya *",
                    options=regions,
                    help="Wilaya du client"
                )
                
                # Amount
                amount = st.number_input(
                    "Montant Mensuel (DA) *",
                    min_value=0.0,
                    max_value=50000.0,
                    step=100.0,
                    help="Montant de l'abonnement mensuel en dinars algériens"
                )
                
                # Date
                subscription_date = st.date_input(
                    "Date d'Abonnement *",
                    value=date.today(),
                    help="Date de début de l'abonnement"
                )
                
                # Notes (optional)
                notes = st.text_area(
                    "Notes (optionnel)",
                    placeholder="Informations supplémentaires...",
                    height=100
                )
                
                # Submit button
                submitted = st.form_submit_button(
                    "💾 Enregistrer l'Abonnement",
                    type="primary",
                    use_container_width=True
                )
                
                if submitted:
                    # Validation
                    errors = []
                    if not client_name.strip():
                        errors.append("Nom du client requis")
                    if not category:
                        errors.append("Catégorie d'abonnement requise")
                    if not region:
                        errors.append("Wilaya requise")
                    if amount <= 0:
                        errors.append("Montant doit être supérieur à 0")
                    
                    if errors:
                        for error in errors:
                            st.error(f"❌ {error}")
                    else:
                        # Prepare data
                        new_subscription = {
                            'Client_Name': client_name.strip(),
                            'Category': category,
                            'Region': region,
                            'Amount': amount,
                            'Date': subscription_date.strftime('%Y-%m-%d'),
                            'Entry_DateTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'Notes': notes.strip() if notes else ""
                        }
                        
                        # Save data
                        if save_subscription(new_subscription):
                            st.success("✅ Abonnement enregistré avec succès!")
                            st.balloons()
                            
                            # Show confirmation
                            st.info(f"""
                            **Détails de l'abonnement:**
                            - Client: {client_name}
                            - Catégorie: {category}
                            - Wilaya: {region}
                            - Montant: {amount:,.0f} DA/mois
                            - Date: {subscription_date.strftime('%d/%m/%Y')}
                            """)
                        else:
                            st.error("❌ Erreur lors de l'enregistrement")
        
        with col2:
            st.markdown("### 📊 Aperçu des Données")
            
            # Load and display recent subscriptions
            df_subs = load_subscriptions()
            
            if len(df_subs) > 0:
                # Summary statistics
                total_subs = len(df_subs)
                total_revenue = df_subs['Amount'].sum()
                avg_amount = df_subs['Amount'].mean()
                
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Total Abonnements</div>
                    <div class="metric-value">{total_subs}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Revenus Total</div>
                    <div class="metric-value">{total_revenue:,.0f} DA</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Montant Moyen</div>
                    <div class="metric-value">{avg_amount:,.0f} DA</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Recent entries
                st.markdown("#### Entrées Récentes")
                recent_df = df_subs.tail(5).sort_values('Entry_DateTime', ascending=False)
                
                for _, row in recent_df.iterrows():
                    st.markdown(f"""
                    <div style="background: #f8f9fa; padding: 0.5rem; margin: 0.5rem 0; border-radius: 8px; border-left: 3px solid #00A859;">
                        <strong>{row['Client_Name']}</strong><br>
                        {row['Category']} - {row['Region']}<br>
                        <span style="color: #00A859; font-weight: bold;">{row['Amount']:,.0f} DA</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Category distribution chart
                if len(df_subs) > 0:
                    st.markdown("#### Répartition par Catégorie")
                    category_counts = df_subs['Category'].value_counts()
                    
                    fig_category = px.pie(
                        values=category_counts.values,
                        names=category_counts.index,
                        color_discrete_sequence=['#002147', '#00A859', '#FF6B35', '#FFA500', '#8E44AD']
                    )
                    
                    fig_category.update_layout(
                        height=300,
                        margin=dict(l=0, r=0, t=0, b=0)
                    )
                    
                    st.plotly_chart(fig_category, use_container_width=True)
            
            else:
                st.info("Aucune donnée d'abonnement disponible.")
    
    # Display all subscriptions table
    st.markdown("### 📋 Tous les Abonnements")
    
    df_subs = load_subscriptions()
    
    if len(df_subs) > 0:
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            category_filter = st.multiselect(
                "Filtrer par Catégorie",
                options=df_subs['Category'].unique(),
                default=df_subs['Category'].unique()
            )
        
        with col2:
            region_filter = st.multiselect(
                "Filtrer par Wilaya",
                options=df_subs['Region'].unique(),
                default=df_subs['Region'].unique()
            )
        
        with col3:
            amount_range = st.slider(
                "Plage de Montant (DA)",
                min_value=int(df_subs['Amount'].min()),
                max_value=int(df_subs['Amount'].max()),
                value=(int(df_subs['Amount'].min()), int(df_subs['Amount'].max())),
                step=100
            )
        
        # Apply filters
        filtered_df = df_subs[
            (df_subs['Category'].isin(category_filter)) &
            (df_subs['Region'].isin(region_filter)) &
            (df_subs['Amount'] >= amount_range[0]) &
            (df_subs['Amount'] <= amount_range[1])
        ]
        
        # Display filtered data
        st.dataframe(
            filtered_df.sort_values('Entry_DateTime', ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
        # Export button
        if len(filtered_df) > 0:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Télécharger CSV",
                data=csv,
                file_name=f"abonnements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("Aucun abonnement enregistré.")

if __name__ == "__main__":
    show_new_entry_page()