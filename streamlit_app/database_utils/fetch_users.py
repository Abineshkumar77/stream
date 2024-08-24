from sqlalchemy.orm import Session
from database import User, Session as UserSession, SessionLocal
import streamlit as st


def fetch_users():
    """Fetch all users from the database."""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return users
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        return []
    finally:
        db.close()