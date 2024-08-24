from sqlalchemy.orm import Session
from database import User, Session as UserSession, SessionLocal
import streamlit as st

def fetch_all_sessions(db):
    try:
        sessions = db.query(UserSession).all()
        return sessions
    except Exception as e:
        st.error(f"Error fetching sessions: {e}")
        return []