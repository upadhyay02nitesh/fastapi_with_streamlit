import streamlit as st
import requests

st.title("📝 Task Tracker Login")

# --- Login Section ---
username = st.text_input("Username")
password = st.text_input("Password", type="password")

from dotenv import load_dotenv
import os

load_dotenv()

def clear_login_inputs():
    st.session_state["username"] = ""
    st.session_state["password"] = ""

API_KEY = os.getenv("API_KEY")
headers = {"api-key": API_KEY}
if st.button("Login"):
    response = requests.post("http://localhost:8000/login", data={
        "username": username,
        "password": password
    }, headers=headers)

    if response.status_code == 200:
        token = response.json()["access_token"]
        st.session_state["token"] = token
        st.success("Login successful!")
        clear_login_inputs()
     
    else:
        st.error("Login failed.")

# --- Show Task Form if Logged In ---
if "token" in st.session_state:
    st.subheader("Add Task")

    title = st.text_input("Task Title")
    desc = st.text_area("Task Description")

    if st.button("Create Task"):
        headers = {
            "Authorization": f"Bearer {st.session_state['token']}",
            "api-key": API_KEY
        }
        task_data = {"title": title, "description": desc}

        res = requests.post("http://localhost:8000/tasks/", json=task_data, headers=headers)

        if res.status_code == 200:
            st.success("Task created!")
        else:
            st.error(f"Error: {res.json().get('detail', 'Unknown error')}")

    # Show tasks after task creation
if "token" in st.session_state:
    st.subheader("📋 Your Tasks")
    
    if st.button("Load My Tasks"):
        headers = {
            "Authorization": f"Bearer {st.session_state['token']}",
            "api-key": API_KEY
        }
        response = requests.get("http://localhost:8000/tasks/", headers=headers)

        if response.status_code == 200:
            tasks = response.json()
            if tasks:
                # Format tasks for display
                for task in tasks:
                    task["Status"] = "✅ Done" if task.get("completed") else "❌ Pending"
                st.dataframe(tasks)
            else:
                st.info("No tasks found.")
        else:
            st.error("Failed to fetch tasks.")