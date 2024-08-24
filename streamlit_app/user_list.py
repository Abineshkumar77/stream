import streamlit as st
import pandas as pd
from database import get_db, User
from datetime import datetime
import pytz

# Function to convert datetime to desired format
def format_datetime(dt):
    if dt:
        # Convert to IST timezone
        ist = pytz.timezone('Asia/Kolkata')
        dt_ist = dt.astimezone(ist)
        # Format as dd/mm/yyyy hh:mm:ss
        return dt_ist.strftime('%d/%m/%Y %H:%M:%S')
    return None

def fetch_users(db):
    try:
        users = db.query(User).all()
        return users
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        return []

def display():
    st.title("List of Users")

    with next(get_db()) as db:
        users = fetch_users(db)
        
        if not users:
            st.write("No users found in the database.")
            return

        # Convert user data to a DataFrame
        user_data = {
            "ID": [user.id for user in users],
            "Name": [user.name for user in users],
            "Date of Registration": [format_datetime(user.registration_date) for user in users]
        }
        df = pd.DataFrame(user_data)

        # Search and Filter
        search_query = st.text_input("Search by Name")

        if search_query:
            filtered_df = df[df['Name'].str.contains(search_query, case=False, na=False)]
        else:
            filtered_df = df

        # Display DataFrame without index
        if not filtered_df.empty:
            st.write("Showing user data:")
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        else:
            st.write("No users match the search criteria.")

# Call display function if this script is run directly
if __name__ == "__main__":
    display()
