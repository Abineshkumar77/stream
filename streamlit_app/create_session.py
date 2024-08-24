import streamlit as st
import numpy as np
import neurokit2 as nk
from database import get_db, Session, User
from database_utils.create_session import create_session
def calculate_hrv(ppg_data_str):
    """
    Calculate RMSSD and SDNN from PPG data given as a comma-separated string, with a sampling rate of 60 Hz.
    
    Parameters:
    ppg_data_str (str): Comma-separated string of PPG data values.
    
    Returns:
    tuple: (RMSSD, SDNN) in seconds, or (0.0, 0.0) as placeholders if calculation fails.
    """
    try:
        # Convert the comma-separated string to a numpy array of floating-point numbers
        ppg_data = np.array([float(x) for x in ppg_data_str.split(',')], dtype=float)

        # Preprocess PPG data using NeuroKit2
        clean_ppg = nk.ppg_clean(ppg_data, sampling_rate=60)

        # Extract peaks from the clean PPG signal
        signals, info = nk.ppg_process(clean_ppg, sampling_rate=60)
        peak_indices = info['PPG_Peaks']

        if len(peak_indices) < 2:
            return 0.0, 0.0

        # Convert peak indices to RR intervals in seconds
        rr_intervals = np.diff(peak_indices) / 60.0  # Sampling rate is 60 Hz

        # Calculate RMSSD and SDNN
        if len(rr_intervals) < 2:
            return 0.0, 0.0

        differences = np.diff(rr_intervals)
        rmssd = np.sqrt(np.mean(differences ** 2))
        sdnn = np.std(rr_intervals)

        return rmssd, sdnn

    except Exception as e:
        st.error(f"Error in HRV calculation: {e}")
        return 0.0, 0.0

def get_users(db):
    try:
        users = db.query(User).all()
        return users
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        return []

def display():
    st.title("Create Session Form")
    
    # Access the DB directly
    with next(get_db()) as db:
        users = get_users(db)
        
        if not users:
            st.error("No users found in the database.")
            return
        
        # Create a dictionary to map user names to IDs
        user_options = {f"{user.name} (ID: {user.id})": user.id for user in users}
        
        with st.form(key="create_session_form"):
            selected_user = st.selectbox("Select User", options=list(user_options.keys()))
            user_id = user_options[selected_user] if selected_user else None
            pulse_rate = st.number_input("Pulse Rate", min_value=0.0)
            spo2 = st.number_input("SpO2", min_value=0.0)
            ppg_data = st.text_area("PPG Data")
            
            if ppg_data:
                # Calculate HRV values if PPG data is provided
                rmssd, sdnn = calculate_hrv(ppg_data)
            else:
                rmssd, sdnn = 0.0, 0.0  # Placeholder values if no PPG data is provided

            st.number_input("RMSSD", min_value=0.0, value=rmssd, format="%.3f", key="rmssd")
            st.number_input("SDNN", min_value=0.0, value=sdnn, format="%.3f", key="sdnn")
            
            submit_button = st.form_submit_button("Create Session")
            
            if submit_button:
                if user_id is None:
                    st.error("Please select a user.")
                else:
                    # Prepare session data
                    session_data = {
                        "user_id": user_id,
                        "pulse_rate": pulse_rate,
                        "spo2": spo2,
                        "rmssd": rmssd,
                        "sdnn": sdnn,
                        "ppg_data": ppg_data,
                    }
                    
                    # Create session
                    session_id = create_session(db, session_data)
                    if session_id:
                        st.success(f"Session created successfully with ID: {session_id}")
                    else:
                        st.error("Failed to create session")

# Call display function if this script is run directly
if __name__ == "__main__":
    display()
