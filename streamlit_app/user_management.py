import streamlit as st
from sqlalchemy.orm import Session
from database import get_db, User
from datetime import datetime
import pytz
from database_utils.fetch_all_users import fetch_all_users

# Function to format datetime
def format_datetime(dt):
    if dt:
        # Convert to IST timezone
        ist = pytz.timezone('Asia/Kolkata')
        dt_ist = dt.astimezone(ist)
        # Format as dd/mm/yyyy hh:mm:ss
        return dt_ist.strftime('%d/%m/%Y %H:%M:%S')
    return None


def display():
    st.title("User Management")

    # Fetch all users
    with next(get_db()) as db:
        users = fetch_all_users(db)
        
        if users:
            # Create list of options for dropdown
            user_options = [f"{user.id} - {user.name}" for user in users]
            
            # Create a selectbox with options
            selected_option = st.selectbox("Select User", options=user_options, format_func=lambda x: x)
            
            if selected_option:
                selected_id = int(selected_option.split(" - ")[0])
                user = next((user for user in users if user.id == selected_id), None)
                
                if user:
                    st.write("User Details:")
                    
                    # Create HTML table for user details without "Value" column
                    user_details = {
                        "Label": ["ID", "Name", "Age", "Gender", "Contact", "Address", "Date of Registration"],
                        "Value": [user.id, user.name, user.age, user.gender, user.contact, user.address, format_datetime(user.registration_date)]
                    }
                    
                    # Transpose the data
                    html = "<table>"
                    for label, value in zip(user_details["Label"], user_details["Value"]):
                        html += f"<tr><td><b>{label}</b></td><td>{value}</td></tr>"
                    html += "</table>"
                    
                    st.markdown(html, unsafe_allow_html=True)
                    
                    # Update User
                    st.subheader("Update User")
                    with st.form(key="update_user_form"):
                        new_name = st.text_input("New Name", value=user.name)
                        new_age = st.number_input("New Age", value=user.age, min_value=0)
                        new_gender = st.selectbox("New Gender", ["Male", "Female"], index=["Male", "Female"].index(user.gender))
                        new_contact = st.text_input("New Contact", value=user.contact)
                        new_address = st.text_input("New Address", value=user.address)
                        
                        update_button = st.form_submit_button("Update User")
                        
                        if update_button:
                            updates = {
                                "name": new_name,
                                "age": new_age,
                                "gender": new_gender,
                                "contact": new_contact,
                                "address": new_address
                            }
                            update_user(db, user.id, updates)
                    
                    # Delete User
                    if st.button("Delete User"):
                        delete_user(db, user.id)
        else:
            st.write("No users found.")

def update_user(db, user_id, updates):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in updates.items():
                setattr(user, key, value)
            db.commit()
            db.refresh(user)
            st.success("User updated successfully")
        else:
            st.error("User not found")
    except Exception as e:
        st.error(f"Error updating user: {e}")
        db.rollback()

def delete_user(db, user_id):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            st.success("User deleted successfully")
        else:
            st.error("User not found")
    except Exception as e:
        st.error(f"Error deleting user: {e}")
        db.rollback()

# Call display function if script is run directly
if __name__ == "__main__":
    display()
