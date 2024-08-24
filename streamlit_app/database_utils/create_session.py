from sqlalchemy.orm import Session
from database import User, Session as UserSession, SessionLocal
import streamlit as st

def create_session(db: Session, session_data: dict):
    """Create a new session record in the database."""
    try:
        new_session = UserSession(
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