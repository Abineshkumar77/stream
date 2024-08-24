import streamlit as st
from database import get_db, User
from database_utils.create_user import create_user



def display():
    st.title("Create User Form")
    with st.form(key="create_user_form"):
        # Form inputs
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=0)
        gender = st.selectbox("Gender", ["Male", "Female"])
        contact = st.text_input("Contact")
        address = st.text_input("Address")
        
        submit_button = st.form_submit_button("Create User")
        
        if submit_button:
            # Prepare user data
            user_data = {
                "name": name,
                "age": age,
                "gender": gender,
                "contact": contact,
                "address": address
            }
            
            # Access the DB directly
            with next(get_db()) as db:
                user_id = create_user(db, user_data)
                if user_id:
                    st.success(f"User created successfully with ID: {user_id}")
                else:
                    st.error("Failed to create user")

# Call display function if this script is run directly
if __name__ == "__main__":
    display()
