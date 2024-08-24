#charts.py
import io
import matplotlib.pyplot as plt
import streamlit as st

def display_gender_distribution(num_male, num_female):
    labels = 'Male', 'Female'
    sizes = [num_male, num_female]
    colors = ['blue', 'pink']
    explode = (0.1, 0)  # explode the 1st slice (Male)

    fig, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
           shadow=True, startangle=90)
    ax.axis('equal')

    st.subheader("Gender Distribution")
    st.pyplot(fig)

def display_age_group_distribution(age_groups):
    labels = list(age_groups.keys())
    sizes = list(age_groups.values())

    fig, ax = plt.subplots()
    ax.bar(labels, sizes, color='skyblue')
    ax.set_xlabel('Age Groups')
    ax.set_ylabel('Number of Users')
    ax.set_title('Age Group Distribution')

    st.subheader("Age Group Distribution")
    st.pyplot(fig)

def plot_pulse_rate_distribution(pulse_rate_counts):
    categories = [
        'Below 50', '50-60', '60-70', '70-80', '80-90', '90-100', 'Above 100'
    ]
    counts = [pulse_rate_counts.get(category, 0) for category in categories]

    fig, ax = plt.subplots()
    ax.bar(categories, counts, color='skyblue')
    ax.set_xlabel('Pulse Rate Category')
    ax.set_ylabel('Number of Users')
    ax.set_title('Pulse Rate Distribution')

    st.subheader("Pulse Rate Distribution")
    st.pyplot(fig)

def plot_spo2_distribution(spo2_counts):
    categories = [
        'Below 65', '65-70', '70-75', '75-80', '80-85', '85-90', '90-95', 'Above 95'
    ]
    counts = [spo2_counts.get(category, 0) for category in categories]

    fig, ax = plt.subplots()
    ax.bar(categories, counts, color='skyblue')
    ax.set_xlabel('SpO2 Level Category')
    ax.set_ylabel('Number of Users')
    ax.set_title('SpO2 Level Distribution')

    st.subheader("SpO2 Level Distribution")
    st.pyplot(fig)

def display_pie_chart(category_counts):
    labels = list(category_counts.keys())
    sizes = list(category_counts.values())
    colors = ['skyblue', 'lightgreen', 'lightcoral', 'gold', 'lightgray', 'lightpink']
    explode = [0.1] + [0] * (len(labels) - 1)  # explode the 1st slice

    fig, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
           shadow=True, startangle=140)
    ax.axis('equal')

    st.subheader("User Health Category Distribution")
    st.pyplot(fig)

def plot_pulse_rate(df, x_col):
    plt.figure(figsize=(12, 6))
    plt.plot(df[x_col], df['pulse_rate'], marker='o', linestyle='-', color='b')
    plt.title('Pulse Rate Over Sessions')
    plt.xlabel(x_col)
    plt.ylabel('Pulse Rate (bpm)')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot()

    

def plot_grouped_bar_chart(df, x_col, value_col, ylabel, healthy_value, healthy_label, title):
    fig, ax = plt.subplots()
    positions = range(len(df))
    width = 0.35

    # Plot bars for the selected sessions
    bars1 = ax.bar([p - width/2 for p in positions], df[value_col], width, label='Selected Sessions')
    
    # Plot bars for the healthy value
    healthy_values = [healthy_value] * len(df)
    bars2 = ax.bar([p + width/2 for p in positions], healthy_values, width, label=healthy_label)

    ax.set_xlabel(x_col)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(positions)
    ax.set_xticklabels(df[x_col])
    ax.legend()

    st.pyplot(fig)


# Plot PPG Data
#PULSE-OX CODE
def plot_ppg_data(ppg_data):
    # Convert ppg_data to integers
    ppg_data = list(map(int, ppg_data))
    
    max_data_points = 2000
    if len(ppg_data) > max_data_points:
        ppg_data = ppg_data[-max_data_points:]

    fig, ax = plt.subplots()
    ax.plot(ppg_data, linestyle='-', color='b')
    ax.set_title('PPG Data Over Time')
    ax.set_xlabel('Sample Index')
    ax.set_ylabel('PPG Data')
    ax.set_xlim(0, len(ppg_data) - 1)
    ax.set_ylim(min(ppg_data) - 10, max(ppg_data) + 10)

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf