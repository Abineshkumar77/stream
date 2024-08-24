from sqlalchemy.orm import Session
from database import User, Session as UserSession, SessionLocal
import streamlit as st


def create_user(db, user_data: dict):
    try:
        new_user = User(
            name=user_data["name"],
            age=user_data["age"],
            gender=user_data["gender"],
            contact=user_data["contact"],
            address=user_data["address"]
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user.id
    except Exception as e:
        st.error(f"Error creating user: {e}")
        db.rollback()
        return None