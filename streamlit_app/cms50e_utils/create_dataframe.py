
import os
import subprocess
import pandas as pd
import streamlit as st
from asyncio.log import logger


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