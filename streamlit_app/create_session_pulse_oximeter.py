import time
import numpy as np
import streamlit as st
import pandas as pd
import logging
import os
import subprocess
from sqlalchemy import create_engine, Column, Integer, Float, Text, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from database import SessionLocal, User, get_db, Session
from cms50e_utils.detect_cms50e_port import detect_cms50e_port
import neurokit2 as nk

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('app.log'),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

# Global variables
captured_data = {
    "timestamp": "",
    "ppg_data_str": "",
    "pulse_rates": [],
    "spo2_levels": [],
    "rmssd": 0.0,
    "sdnn": 0.0,
    "dataframe": pd.DataFrame()
}

def create_session(db, session_data: dict):
    try:
        new_session = Session(
            user_id=session_data["user_id"],
            pulse_rate=session_data["pulse_rate"],
            spo2=session_data["spo2"],
            rmssd=session_data["rmssd"],
            sdnn=session_data["sdnn"],
            ppg_data=session_data["ppg_data"]
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return new_session.id
    except Exception as e:
        st.error(f"Error creating session: {e}")
        db.rollback()
        return None

def fetch_users():
    logger.debug("Fetching users from database")
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return users
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        logger.error(f"Error fetching users: {e}")
        return []
    finally:
        db.close()

def decode_data(raw_data):
    logger.debug(f"Decoding raw data: {raw_data}")
    try:
        timestamp = raw_data[:10]
        data = raw_data[10:]
        data = ''.join(data.split())[:-10]

        dataT = data.split('ffff')
        dataT.pop()

        ppg_data, pulse_rates, spo2_levels = [], [], []

        for dat in dataT:
            byte_list = [dat[i:i+2] for i in range(0, len(dat), 2)]
            if len(byte_list) >= 7:
                ppg = int(byte_list[4], 16) & 0x7f
                pulse_rate = int(byte_list[5], 16) & 0x7f
                spo2_level = int(byte_list[6], 16) & 0x7f
                
                ppg_data.append(ppg)
                pulse_rates.append(pulse_rate)
                spo2_levels.append(spo2_level)

        ppg_data_str = ', '.join(map(str, ppg_data))
        logger.debug(f"Decoded data - Timestamp: {timestamp}, PPG Data: {ppg_data_str}, Pulse Rates: {pulse_rates}, SpO2 Levels: {spo2_levels}")
        return timestamp, ppg_data_str, pulse_rates, spo2_levels

    except Exception as e:
        st.error(f"Error decoding data: {e}")
        logger.error(f"Error decoding data: {e}")
        return "", "", [], []

def create_dataframe(timestamp, ppg_data_str, pulse_rates, spo2_levels):
    logger.debug(f"Creating DataFrame with timestamp: {timestamp}, PPG Data: {ppg_data_str}, Pulse Rates: {pulse_rates}, SpO2 Levels: {spo2_levels}")
    try:
        df = pd.DataFrame({
            "Timestamp": [timestamp] * len(pulse_rates),
            "PPG Data": ppg_data_str.split(', '),
            "Pulse Rate": pulse_rates,
            "SpO2 Level": spo2_levels
        })

        # Drop rows where PPG Data is zero
        df = df[df["PPG Data"].astype(int) != 0]
        
        logger.debug("Created DataFrame")
        return df
    except Exception as e:
        st.error(f"Error creating dataframe: {e}")
        logger.error(f"Error creating dataframe: {e}")
        return pd.DataFrame()

def run_cms50e_script(port: str, file: str):
    script_path = os.path.join(os.path.dirname(__file__), 'cms50e.py')
    logger.debug(f"Running CMS50E capture script: {script_path} with port: {port} and file: {file}")
    process = subprocess.Popen(['python', script_path, port, file], 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process

def calculate_hrv(pulse_rates_input, sampling_rate=60):
    try:
        # Check if input is a string, if so, convert it to a list of floats
        if isinstance(pulse_rates_input, str):
            pulse_rates = np.array([float(rate) for rate in pulse_rates_input.split(',')])
        elif isinstance(pulse_rates_input, list):
            pulse_rates = np.array(pulse_rates_input, dtype=float)
        else:
            raise ValueError("Invalid input type for pulse_rates. Expected string or list.")

        # Handle any zero or very small pulse rates to prevent division by zero
        pulse_rates = np.clip(pulse_rates, 1e-5, None)

        # Convert pulse rates (BPM) to RR intervals (in seconds)
        rr_intervals = 60.0 / pulse_rates  # RR intervals in seconds
        
        # Convert RR intervals to peak indices
        peak_indices = nk.intervals_to_peaks(rr_intervals, sampling_rate=sampling_rate)
        
        # Calculate HRV using the peak indices
        hrv = nk.hrv_time(peak_indices, sampling_rate=sampling_rate, show=False)
        
        # Extract HRV metrics
        rmssd = hrv["HRV_RMSSD"].iloc[0]
        sdnn = hrv["HRV_SDNN"].iloc[0]
        
        return rmssd, sdnn
    except Exception as e:
        logger.error(f"Error calculating HRV: {e}")
        return 0.0, 0.0

def display():
    st.title("CMS50E Data Capture and User Session Management")

    detected_port = detect_cms50e_port()
    
    port_option = st.selectbox(
        "Choose how to enter the COM Port:",
        options=["Auto Detect", "Manual Entry"]
    )
    
    if port_option == "Auto Detect":
        if detected_port:
            st.success(f"Detected CMS50E on port: {detected_port}")
            port = detected_port
        else:
            st.error("CMS50E device not detected. Please check the connection.")
            port = None
    else:
        port = st.text_input("Enter Serial Port (e.g., COM3):", "COM3")

    filename = "data_capture.txt"

    if port:
        logger.debug(f"Selected Serial Port: {port}")

        users = fetch_users()
        if users:
            user_names = [user.name for user in users]
            selected_user_name = st.selectbox("Select User Name", options=user_names)

            if selected_user_name:
                selected_user = next(user for user in users if user.name == selected_user_name)
                user_id = selected_user.id

                st.write(f"**User ID**: {user_id}")
                logger.debug(f"Selected User ID: {user_id}")

                timer_placeholder = st.empty()

                if st.button("Start Session", key='start_session'):
                    logger.debug("Start Session button clicked")
                    process = run_cms50e_script(port, filename)
                    st.session_state.start_time = time.time()
                    st.session_state.timer_running = True
                    st.session_state.process = process
                    logger.info(f"Session started. Data will be saved to: {filename}")

                if st.button("Stop Session", key='stop_session'):
                    logger.debug("Stop Session button clicked")
                    process = st.session_state.get('process')
                    if process:
                        process.terminate()
                        process.wait()
                        st.session_state.timer_running = False
                        logger.info("Session stopped.")

                        if os.path.exists(filename):
                            logger.debug(f"Reading captured data from: {filename}")
                            with open(filename, "r") as f:
                                data = f.read()
                            logger.debug(f"Fetched captured data: {data}")
                            if data:
                                timestamp, ppg_data_str, pulse_rates, spo2_levels = decode_data(data)
                                global captured_data
                                logger.debug(f"Updating captured data: {timestamp}, {ppg_data_str}, {pulse_rates}, {spo2_levels}")
                                rmssd, sdnn = calculate_hrv(pulse_rates)  # Calculate HRV metrics
                                captured_data = {
                                    "timestamp": timestamp,
                                    "ppg_data_str": ppg_data_str,
                                    "pulse_rates": pulse_rates,
                                    "spo2_levels": spo2_levels,
                                    "rmssd": rmssd,
                                    "sdnn": sdnn,
                                    "dataframe": create_dataframe(timestamp, ppg_data_str, pulse_rates, spo2_levels)
                                }
                            else:
                                st.warning("No data available.")
                                logger.warning("No data available.")
                        else:
                            st.error("Failed to retrieve captured data.")
                            logger.error("Failed to retrieve captured data.")
                
                avg_pulse_rate = 0.0
                avg_spo2 = 0.0
                if st.session_state.get('timer_running'):
                    elapsed_time = time.time() - st.session_state.start_time
                    elapsed_minutes = int(elapsed_time // 60)
                    elapsed_seconds = int(elapsed_time % 60)
                    timer_placeholder.write(f"**Session Timer:** {elapsed_minutes}m {elapsed_seconds}s")
                
                if captured_data["dataframe"].empty:
                    st.warning("No data available. Please run a session.")
                else:
                    st.subheader("Captured Data")
                    st.dataframe(captured_data["dataframe"])

                    if len(captured_data["pulse_rates"]) > 0 and len(captured_data["spo2_levels"]) > 0:
                        avg_pulse_rate = np.mean(captured_data["pulse_rates"])
                        avg_spo2 = np.mean(captured_data["spo2_levels"])

                    st.write(f"**Average Pulse Rate**: {avg_pulse_rate:.2f} BPM")
                    st.write(f"**Average SpO2 Level**: {avg_spo2:.2f}%")
                    st.write(f"**RMSSD**: {captured_data['rmssd']:.2f} ms")
                    st.write(f"**SDNN**: {captured_data['sdnn']:.2f} ms")

                if st.button("Save Session", key='save_session'):
                    session_data = {
                        "user_id": user_id,
                        "pulse_rate": avg_pulse_rate,
                        "spo2": avg_spo2,
                        "rmssd": captured_data["rmssd"],
                        "sdnn": captured_data["sdnn"],
                        "ppg_data": captured_data["ppg_data_str"]
                    }
                    db = SessionLocal()
                    session_id = create_session(db, session_data)
                    if session_id:
                        st.success(f"Session data saved successfully with Session ID: {session_id}")
                        logger.info(f"Session data saved successfully with Session ID: {session_id}")
                    else:
                        st.error("Failed to save session data.")
                        logger.error("Failed to save session data.")

if __name__ == "__main__":
    display()
