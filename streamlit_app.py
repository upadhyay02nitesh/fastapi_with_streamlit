import streamlit as st
import requests
import os
from dotenv import load_dotenv

st.set_page_config(page_title="Task Tracker", layout="centered")

st.title("📝 Task Tracker Login")

# --- Load environment ---
load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://fastapi-with-streamlit-r66r.onrender.com"

# --- Session State Defaults ---
if "token" not in st.session_state:
    st.session_state.token = None

# --- Login Section ---
username = st.text_input("Username", key="username")
password = st.text_input("Password", type="password", key="password")

if st.button("Login"):
    headers = {"api-key": API_KEY}
    response = requests.post(f"{BASE_URL}/login", data={
        "username": username,
        "password": password
    }, headers=headers)

    if response.status_code == 200:
        st.session_state.token = response.json()["access_token"]
        st.success("Login successful!")
    else:
        st.error("Login failed. Check your credentials.")

# --- Logout ---
if st.session_state.get("token"):
    if st.button("Logout"):
        headers = {
            "Authorization": f"Bearer {st.session_state['token']}",
            "api-key": API_KEY
        }
        response = requests.post(f"{BASE_URL}/logout", headers=headers)

        if response.status_code == 200:
            st.success(response.json().get("message"))
            # Clear token from session
            st.session_state["token"] = None
            # Rerun app to reset view to login form
            st.experimental_rerun()
        else:
            st.error("Logout failed.")


# --- Add Task Section ---
if st.session_state.token:
    st.subheader("➕ Create Task")
    title = st.text_input("Task Title")
    desc = st.text_area("Task Description")

    if st.button("Create Task"):
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "api-key": API_KEY
        }
        task_data = {"title": title, "description": desc}

        res = requests.post(f"{BASE_URL}/tasks/", json=task_data, headers=headers)
        if res.status_code == 200:
            st.success("✅ Task created successfully!")
        else:
            st.error(f"❌ Error: {res.json().get('detail', 'Unknown error')}")

# --- View Tasks Section ---
if st.session_state.token:
    st.subheader("📋 Your Tasks")
    if st.button("Load My Tasks"):
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "api-key": API_KEY
        }
        response = requests.get(f"{BASE_URL}/tasks/", headers=headers)

        if response.status_code == 200:
            tasks = response.json()
            if tasks:
                for task in tasks:
                    task["Status"] = "✅ Done" if task.get("completed") else "❌ Pending"
                st.dataframe(tasks)
            else:
                st.info("No tasks found.")
        else:
            st.error("Failed to fetch tasks.")


    st.subheader("✏️ Update Task")
    task_id_update = st.number_input("Task ID to Update", min_value=1, step=1)
    updated_title = st.text_input("Updated Title")
    updated_desc = st.text_area("Updated Description")
    updated_completed = st.checkbox("Completed?")

    if st.button("Update Task"):
        update_data = {
            "title": updated_title,
            "description": updated_desc,
            "completed": updated_completed
        }
        headers = {
            "Authorization": f"Bearer {st.session_state['token']}",
            "api-key": API_KEY
        }

        res = requests.put(f"https://fastapi-with-streamlit-r66r.onrender.com/tasks/{task_id_update}",
                           json=update_data, headers=headers)

        if res.status_code == 200:
            st.success("✅ Task updated successfully!")
        else:
            st.error(f"❌ Update failed: {res.json().get('detail', 'Unknown error')}")
    st.subheader("🗑️ Delete Task")
    task_id_delete = st.number_input("Task ID to Delete", min_value=1, step=1)

    if st.button("Delete Task"):
        headers = {
            "Authorization": f"Bearer {st.session_state['token']}",
            "api-key": API_KEY
        }

        res = requests.delete(f"https://fastapi-with-streamlit-r66r.onrender.com/tasks/{task_id_delete}",
                              headers=headers)

        if res.status_code == 200:
            st.success("🗑️ Task deleted successfully!")
        else:
            st.error(f"❌ Delete failed: {res.json().get('detail', 'Unknown error')}")
