from sqlalchemy.orm import Session
from database import User, Session as UserSession, SessionLocal
import streamlit as st

def delete_session(db, session_id):
    try:
        session = db.query(UserSession).filter(UserSession.id == session_id).first()
        if session:
            db.delete(session)
            db.commit()
            st.success("Session deleted successfully")
        else:
            st.error("Session not found")
    except Exception as e:
        st.error(f"Error deleting session: {e}")
        db.rollback()