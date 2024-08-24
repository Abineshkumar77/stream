from asyncio.log import logger
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
import neurokit2 as nk
from sqlalchemy.orm import Session
from database import get_db, User, Session as DbSession

def get_users(db: Session):
    return db.query(User).all()

def get_user_sessions(db: Session, user_id: int):
    return db.query(DbSession).filter(DbSession.user_id == user_id).all()

def plot_pulse_rate(df, x_col):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df[x_col], df['pulse_rate'], marker='o', linestyle='-', color='b')
    ax.set_title('Pulse Rate Over Sessions')
    ax.set_xlabel(x_col)
    ax.set_ylabel('Pulse Rate (bpm)')
    ax.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

def plot_spo2(df, x_col):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df[x_col], df['spo2'], marker='o', linestyle='-', color='r')
    ax.set_title('SpO2 Over Sessions')
    ax.set_xlabel(x_col)
    ax.set_ylabel('SpO2 (%)')
    ax.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

def plot_grouped_bar_chart(df, x_col, value_col, ylabel, healthy_value, healthy_label, title):
    fig, ax = plt.subplots()
    positions = range(len(df))
    width = 0.35

    bars1 = ax.bar([p - width/2 for p in positions], df[value_col], width, label='Selected Sessions')
    healthy_values = [healthy_value] * len(df)
    bars2 = ax.bar([p + width/2 for p in positions], healthy_values, width, label=healthy_label)

    ax.set_xlabel(x_col)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(positions)
    ax.set_xticklabels(df[x_col])
    ax.legend()
    st.pyplot(fig)


def plot_ppg_signals(ppg_data):
    try:
        ppg_data = [x.strip() for x in ppg_data.split(',') if x.strip()]
        ppg_data = [x for x in ppg_data if x.replace('.', '', 1).isdigit()]
        if not ppg_data:
            st.warning("No valid PPG data found.")
            return

        ppg_list = [float(x) for x in ppg_data]
        if len(ppg_list) < 2:
            st.warning("Not enough PPG data to process.")
            return
        
        ppg_array = np.array(ppg_list)
        signals, info = nk.ppg_process(ppg_array, sampling_rate=60)

        if signals.empty or 'PPG_Clean' not in signals or 'PPG_Rate' not in signals:
            st.warning("Error in processing PPG signal. No valid peaks detected.")
            return

        ppg_clean = signals['PPG_Clean']
        heart_rate = signals['PPG_Rate']
        
        plt.figure(figsize=(10, 4))
        plt.plot(ppg_clean)
        plt.title('Cleaned PPG Signal')
        plt.xlabel('Time')
        plt.ylabel('Amplitude')
        plt.grid(True)
        plt.tight_layout()
        st.pyplot(plt.gcf())
        plt.close()

        if heart_rate.size > 0:
            plt.figure(figsize=(10, 4))
            plt.plot(heart_rate, color='r')
            plt.title('Heart Rate')
            plt.xlabel('Time')
            plt.ylabel('BPM')
            plt.grid(True)
            plt.tight_layout()
            st.pyplot(plt.gcf())
            plt.close()
        else:
            st.warning("No heart rate data available.")

    except ValueError as ve:
        st.error(f"Value error: {ve}")
    except TypeError as te:
        st.error(f"Type error: {te}")
    except ZeroDivisionError as zde:
        st.error(f"Zero division error: {zde}")
    except Exception as e:
        st.error(f"Error plotting PPG signals: {e}")

def display():
    st.title("User Session Analytics")

    # Create a database session
    db = next(get_db())
    
    # Fetch and display users
    users = get_users(db)
    user_names = [user.name for user in users]
    user_name = st.selectbox("Select a user:", user_names)

    if user_name:
        user_id = next(user.id for user in users if user.name == user_name)
        sessions = get_user_sessions(db, user_id)
        
        if sessions:
            df = pd.DataFrame([{
                'session_id': session.id,
                'pulse_rate': session.pulse_rate,
                'spo2': session.spo2,
                'rmssd': session.rmssd,
                'sdnn': session.sdnn,
                'ppg_data': session.ppg_data,
                'date_only': session.date.date()
            } for session in sessions])
            
            st.write("### PPG Data Analysis")
            
            if 'ppg_data' in df.columns:
                session_select_type = st.selectbox("Select session by:", ["Session ID", "Date"])
                if session_select_type == "Session ID":
                    session_id = st.selectbox("Select a session ID:", df['session_id'].tolist())
                    session_filter = df['session_id'] == session_id
                elif session_select_type == "Date":
                    date = st.selectbox("Select a date:", df['date_only'].unique())
                    session_filter = df['date_only'] == date

                selected_session_df = df[session_filter]

                if not selected_session_df.empty:
                    selected_session = selected_session_df.iloc[0]
                    ppg_data = selected_session['ppg_data']
                    plot_ppg_signals(ppg_data)

                    st.write("### HRV Metrics")
                    st.write(f"**RMSSD**: {selected_session['rmssd']}")
                    st.write(f"**SDNN**: {selected_session['sdnn']}")
                   
                else:
                    st.warning("No PPG data available for the selected session.")
            else:
                st.warning("PPG data column not found in the dataset.")

            st.write(f"### Sessions for {user_name}")
            st.dataframe(df)
            
            x_axis_type = st.selectbox("Select x-axis type:", ["Session ID", "Date"])
            x_col = 'session_id' if x_axis_type == "Session ID" else 'date_only'

            st.write("### Pulse Rate Over Sessions")
            plot_pulse_rate(df, x_col)
            
            st.write("### SpO2 Over Sessions")
            plot_spo2(df, x_col)
            
        else:
            st.warning("No sessions found for the selected user.")

if __name__ == "__main__":
    display()
