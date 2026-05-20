import streamlit as st
import os
import sys

# Add the pages directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'pages'))

# Import pages
from pages.new_entry import show_new_entry_page
from pages.forecasting import show_forecasting_page
from pages.analysis import show_analysis_page
from pages.data import show_data_page

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
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #002147 0%, #00A859 100%);
    }
    
    /* Navigation styling */
    .nav-item {
        padding: 0.5rem 1rem;
        margin: 0.25rem 0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s;
        background: rgba(255, 255, 255, 0.1);
        color: white;
    }
    
    .nav-item:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateX(5px);
    }
    
    .nav-item.active {
        background: rgba(255, 255, 255, 0.3);
        border-left: 4px solid white;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application with navigation"""
    
    # Sidebar navigation
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem; color: white;">
        <h2 style="color: white; margin: 0;">📡 Navigation</h2>
        <p style="color: rgba(255,255,255,0.8); font-size: 0.9rem; margin: 0.5rem 0;">
            Tableau de Bord Algérie Télécom
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation menu
    page_options = {
        "🏠 Tableau de Bord": "dashboard",
        "📝 Nouvel Abonnement": "new_entry", 
        "🔮 Prévisions": "forecasting",
        "📊 Analyse Avancée": "analysis",
        "📋 Gestion des Données": "data"
    }
    
    # Store selected page in session state
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = "dashboard"
    
    # Custom navigation
    for page_name, page_key in page_options.items():
        if st.sidebar.button(
            page_name,
            key=f"nav_{page_key}",
            use_container_width=True,
            type="primary" if st.session_state.selected_page == page_key else "secondary"
        ):
            st.session_state.selected_page = page_key
    
    # Add separator and info
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="color: white; text-align: center; padding: 1rem;">
        <h4>ℹ️ Information</h4>
        <p style="font-size: 0.8rem; color: rgba(255,255,255,0.8);">
            Dashboard développé pour l'analyse des données d'abonnements Internet d'Algérie Télécom
        </p>
        <p style="font-size: 0.7rem; color: rgba(255,255,255,0.6);">
            Version 1.0 | 2024
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Route to selected page
    if st.session_state.selected_page == "dashboard":
        show_dashboard()
    elif st.session_state.selected_page == "new_entry":
        show_new_entry_page()
    elif st.session_state.selected_page == "forecasting":
        show_forecasting_page()
    elif st.session_state.selected_page == "analysis":
        show_analysis_page()
    elif st.session_state.selected_page == "data":
        show_data_page()

def show_dashboard():
    """Main dashboard functionality"""
    # Import here to avoid circular imports
    from app import main_dashboard
    main_dashboard()

if __name__ == "__main__":
    main()