import streamlit as st
import pandas as pd
from database import get_db, Session, User
from datetime import datetime
import pytz
from sqlalchemy.orm import joinedload

# Function to convert datetime to desired format
def format_datetime(dt):
    if dt:
        # Convert to IST timezone
        ist = pytz.timezone('Asia/Kolkata')
        dt_ist = dt.astimezone(ist)
        # Format as dd/mm/yyyy hh:mm:ss
        return dt_ist.strftime('%d/%m/%Y %H:%M:%S')
    return None

def fetch_sessions(db):
    try:
        # Fetch all sessions and load related user data to avoid lazy loading issues
        sessions = db.query(Session).options(joinedload(Session.user)).all()
        return sessions
    except Exception as e:
        st.error(f"Error fetching sessions: {e}")
        return []

def display():
    st.title("List of Sessions")

    with next(get_db()) as db:
        sessions = fetch_sessions(db)
        
        if not sessions:
            st.write("No sessions found in the database.")
            return

        # Convert session data to a DataFrame
        session_data = {
            "Session ID": [session.id for session in sessions],
            "User Name": [session.user.name for session in sessions],
            "Pulse Rate": [session.pulse_rate for session in sessions],
            "SpO2": [session.spo2 for session in sessions],
            "RMSSD": [session.rmssd for session in sessions],
            "SDNN": [session.sdnn for session in sessions],
            "Date": [format_datetime(session.date) for session in sessions]
        }
        df = pd.DataFrame(session_data)

        # Search and Filter
        search_query = st.text_input("Search by User Name")

        if search_query:
            filtered_df = df[df['User Name'].str.contains(search_query, case=False, na=False)]
        else:
            filtered_df = df

        # Display DataFrame without index
        if not filtered_df.empty:
            st.write("Showing session data:")
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        else:
            st.write("No sessions match the search criteria.")

# Call display function if this script is run directly
if __name__ == "__main__":
    display()
