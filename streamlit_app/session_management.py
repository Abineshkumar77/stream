import streamlit as st
from sqlalchemy.orm import Session
from database import get_db, Session as DbSession, User
from datetime import datetime
import pytz
import numpy as np
import neurokit2 as nk
from database_utils.delete_session import delete_session
from database_utils.fetch_all_sessions import fetch_all_sessions
from database_utils.fetch_all_users import fetch_all_users
from cms50e_utils.calculate_hrv import calculate_hrv
# Function to format datetime
def format_datetime(dt):
    if dt:
        # Convert to IST timezone
        ist = pytz.timezone('Asia/Kolkata')
        dt_ist = dt.astimezone(ist)
        # Format as dd/mm/yyyy hh:mm:ss
        return dt_ist.strftime('%d/%m/%Y %H:%M:%S')
    return None

def display():
    st.title("Session Management")

    # Fetch all sessions and users
    with next(get_db()) as db:
        sessions = fetch_all_sessions(db)
        users = fetch_all_users(db)

        if sessions:
            # Create a list of options for dropdown
            session_options = [f"Session ID: {session.id} - User ID: {session.user_id}" for session in sessions]
            
            # Create a selectbox with options
            selected_option = st.selectbox("Select Session", options=session_options, format_func=lambda x: x)
            
            if selected_option:
                selected_id = int(selected_option.split(" - ")[0].split(": ")[1])
                session = next((session for session in sessions if session.id == selected_id), None)
                
                if session:
                    st.write("Session Details:")
                    
                    # Create HTML table for session details
                    session_details = {
                        "Session ID": session.id,
                        "User ID": session.user_id,
                        "Pulse Rate": session.pulse_rate,
                        "SpO2": session.spo2,
                        "RMSSD": session.rmssd,
                        "SDNN": session.sdnn,
                        "PPG Data": session.ppg_data,
                        "Date": format_datetime(session.date)
                    }
                    
                    # Generate the HTML table without headers
                    html = "<table style='border-collapse: collapse; width: 60%;'>"
                    for label, value in session_details.items():
                        html += f"<tr><td style='padding: 8px; border: 1px solid #ddd;'><b>{label}</b></td><td style='padding: 8px; border: 1px solid #ddd;'>{value}</td></tr>"
                    html += "</table>"
                    
                    st.markdown(html, unsafe_allow_html=True)
                    
                    # Update Session
                    st.subheader("Update Session")
                    with st.form(key="update_session_form"):
                        new_pulse_rate = st.number_input("New Pulse Rate", value=session.pulse_rate)
                        new_spo2 = st.number_input("New SpO2", value=session.spo2)
                        new_ppg_data = st.text_area("New PPG Data", value=session.ppg_data)
                        
                        update_button = st.form_submit_button("Update Session")
                        
                        if update_button:
                            # Calculate new RMSSD and SDNN
                            new_rmssd, new_sdnn = calculate_hrv(new_ppg_data)
                            
                            updates = {
                                "pulse_rate": new_pulse_rate,
                                "spo2": new_spo2,
                                "rmssd": new_rmssd,
                                "sdnn": new_sdnn,
                                "ppg_data": new_ppg_data
                            }
                            update_session(db, session.id, updates)
                    
                    # Delete Session
                    if st.button("Delete Session"):
                        delete_session(db, session.id)
        else:
            st.write("No sessions found.")

def update_session(db, session_id, updates):
    try:
        session = db.query(DbSession).filter(DbSession.id == session_id).first()
        if session:
            for key, value in updates.items():
                setattr(session, key, value)
            db.commit()
            db.refresh(session)
            st.success("Session updated successfully")
        else:
            st.error("Session not found")
    except Exception as e:
        st.error(f"Error updating session: {e}")
        db.rollback()



# Call display function if script is run directly
if __name__ == "__main__":
    display()
