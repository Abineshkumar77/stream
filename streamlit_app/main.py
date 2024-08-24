import streamlit as st
from streamlit_option_menu import option_menu
from home import display  # Ensure this file contains the 'display' function

# Sidebar menu
with st.sidebar:
    selected = option_menu(
        "Main Menu",
        ["Home", "User Management", "Session Management", "User Session Analytics"],
        icons=["house", "person", "activity", "bar-chart"],
        menu_icon="cast",
        default_index=0,
    )

if selected == "Home":
    st.title("Welcome to User Health Dashboard")
    display()
elif selected == "User Management":
    user_management = option_menu(
        "User Management",
        ["Create User", "List Users", "User Management"],
        icons=["person-plus", "list", "person"],
        menu_icon="person",
        default_index=0,
        orientation="vertical"
    )
    if user_management == "Create User":
        import create_user
        st.title("Create User")
        create_user.display()
    elif user_management == "List Users":
        import user_list
        st.title("List Users")
        user_list.display()
    elif user_management == "User Management":
        import user_management
        st.title("User Management")
        user_management.display()
elif selected == "Session Management":
    session_management = option_menu(
        "Session Management",
        ["Create Session Through Pulse Oximeter(CMS50E)", "Create Session Manually", "View All Sessions", "Session Management"],
        icons=["activity", "pencil", "list", "info-circle"],
        menu_icon="activity",
        default_index=0,
        orientation="vertical"
    )
    if session_management == "Create Session Through Pulse Oximeter(CMS50E)":
        import create_session_pulse_oximeter
        create_session_pulse_oximeter.display()
    
    elif session_management == "Create Session Manually":
        import create_session
        create_session.display()

    elif session_management == "View All Sessions":
        import sessions_list
        sessions_list.display()
    
    elif session_management == "Session Management":
        import session_management
        session_management.display()

elif selected == "User Session Analytics":
    import user_session_analytics
    user_session_analytics.display()
