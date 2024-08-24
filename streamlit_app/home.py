import streamlit as st
from sqlalchemy.orm import Session
from database import get_db, User, Session as DBSession
from collections import Counter
from charts import display_gender_distribution, display_age_group_distribution, plot_pulse_rate_distribution, plot_spo2_distribution, display_pie_chart

def get_all_users(db: Session):
    return db.query(User).all()

def get_user_latest_session(db: Session, user_id: int):
    return db.query(DBSession).filter(DBSession.user_id == user_id).order_by(DBSession.date.desc()).first()

def get_total_sessions(db: Session):
    return db.query(DBSession).count()

def categorize_pulse_rate(pulse_rate):
    if pulse_rate < 50:
        return 'Below 50'
    elif 50 <= pulse_rate < 60:
        return '50-60'
    elif 60 <= pulse_rate < 70:
        return '60-70'
    elif 70 <= pulse_rate < 80:
        return '70-80'
    elif 80 <= pulse_rate < 90:
        return '80-90'
    elif 90 <= pulse_rate < 100:
        return '90-100'
    else:
        return 'Above 100'

def categorize_spo2(spo2):
    if spo2 < 65:
        return 'Below 65'
    elif 65 <= spo2 < 70:
        return '65-70'
    elif 70 <= spo2 < 75:
        return '70-75'
    elif 75 <= spo2 < 80:
        return '75-80'
    elif 80 <= spo2 < 85:
        return '80-85'
    elif 85 <= spo2 < 90:
        return '85-90'
    elif 90 <= spo2 < 95:
        return '90-95'
    else:
        return 'Above 95'

def categorize_user(pulse_rate, spo2):
    healthy_pulse_range = (60, 100)
    healthy_spo2_range = (95, 100)
    critical_spo2_threshold = 90

    if pulse_rate < healthy_pulse_range[0]:
        pulse_category = "Low Pulse Rate"
    elif pulse_rate > healthy_pulse_range[1]:
        pulse_category = "Elevated Pulse Rate"
    else:
        pulse_category = "Healthy"

    if spo2 < critical_spo2_threshold:
        spo2_category = "Low SpO2"
    elif spo2 < healthy_spo2_range[0]:
        spo2_category = "Mild Hypoxemia"
    else:
        spo2_category = "Healthy"

    if spo2_category == "Low SpO2":
        return "Critical"
    elif pulse_category == "Low Pulse Rate" and spo2_category in ["Healthy", "Mild Hypoxemia"]:
        return "Low Pulse Rate"
    elif pulse_category == "Elevated Pulse Rate" and spo2_category in ["Healthy", "Mild Hypoxemia"]:
        return "Elevated Pulse Rate"
    elif pulse_category == "Healthy" and spo2_category == "Healthy":
        return "Healthy"
    else:
        return "Critical"

def calculate_age_groups(users):
    age_groups = {
        '0-18': 0,
        '19-35': 0,
        '36-50': 0,
        '51-65': 0,
        '66+': 0
    }
    for user in users:
        age = user.age
        if age <= 18:
            age_groups['0-18'] += 1
        elif age <= 35:
            age_groups['19-35'] += 1
        elif age <= 50:
            age_groups['36-50'] += 1
        elif age <= 65:
            age_groups['51-65'] += 1
        else:
            age_groups['66+'] += 1
    return age_groups

def display():
    st.title("User Session Analytics")

    db = next(get_db())
    
    users = get_all_users(db)
    num_users = len(users)

    num_sessions = get_total_sessions(db)  # Update the number of sessions

    pulse_rate_categories = []
    spo2_categories = []
    categories = []

    for user in users:
        user_id = user.id
        latest_session = get_user_latest_session(db, user_id)
        
        if latest_session:
            pulse_rate = latest_session.pulse_rate
            spo2 = latest_session.spo2
            if pulse_rate is not None and spo2 is not None:
                category = categorize_user(pulse_rate, spo2)
                categories.append(category)
                pulse_rate_categories.append(categorize_pulse_rate(pulse_rate))
                spo2_categories.append(categorize_spo2(spo2))
        else:
            categories.append("No Data")

    num_male = sum(1 for user in users if user.gender.strip().lower() == 'male')
    num_female = sum(1 for user in users if user.gender.strip().lower() == 'female')
    
    age_groups = calculate_age_groups(users)
    category_counts = Counter(categories)

    st.subheader("Statistics")
    st.write(f"**Number of Users**: {num_users}")
    st.write(f"**Number of Sessions**: {num_sessions}")  # Display the updated number of sessions
    st.write(f"**Number of Male Users**: {num_male}")
    st.write(f"**Number of Female Users**: {num_female}")

    display_gender_distribution(num_male, num_female)
    display_age_group_distribution(age_groups)
    
    if pulse_rate_categories:
        pulse_rate_count = Counter(pulse_rate_categories)
        plot_pulse_rate_distribution(pulse_rate_count)

    if spo2_categories:
        spo2_count = Counter(spo2_categories)
        plot_spo2_distribution(spo2_count)

    if category_counts:
        display_pie_chart(category_counts)

if __name__ == "__main__":
    display()
