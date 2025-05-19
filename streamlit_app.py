import streamlit as st
import requests
import os
from dotenv import load_dotenv

st.set_page_config(page_title="Task Tracker", layout="centered")

st.title("📝 Taskit – Your Task Management Buddy")

# --- Load environment ---
load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://fastapi-with-streamlit-r66r.onrender.com"

# --- Session State Defaults ---
if "token" not in st.session_state:
    st.session_state.token = None

with st.expander("🔐 Register New Account"):
    reg_username = st.text_input("New Username", key="reg_user")
    reg_password = st.text_input("New Password", type="password", key="reg_pass")

    if st.button("Register"):
        headers = {"api-key": API_KEY}
        payload = {"username": reg_username, "password": reg_password}

        res = requests.post(f"{BASE_URL}/register", json=payload, headers=headers)

        if res.status_code == 200:
            st.success("🎉 Registration successful! You can now log in.")
        else:
            st.error(f"❌ Registration failed: {res.json().get('detail', 'Unknown error')}")

# --- Login Section ---
st.subheader("🔑 Login to Your Account")
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
            st.rerun()
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

if st.session_state.token:
    st.subheader("📋 Your Tasks")

    # Inputs for pagination and limiting
    last_id = st.number_input("Last Task ID (for pagination, optional)", min_value=0, step=1, value=0)
    limit = st.number_input("Number of tasks to fetch (limit)", min_value=1, max_value=100, step=1, value=10)

    if st.button("Load My Tasks"):
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "api-key": API_KEY
        }

        # Build params dictionary for query string
        params = {}
        if last_id > 0:
            params["last_id"] = last_id-1
        params["limit"] = limit

        response = requests.get(f"{BASE_URL}/tasks/", headers=headers, params=params)

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


with st.expander("📘 About Taskit – Your Task Management Buddy", expanded=True):
    st.markdown("""
    **Taskit** is a real-world **task management application** built using **microservices architecture** to deliver a clean, fast, and reliable user experience.

    - 🖥️ **Frontend**: Built with [Streamlit](https://streamlit.io), deployed to **Streamlit Cloud** for a seamless user interface.
    - ⚙️ **Backend**: Developed using [FastAPI](https://fastapi.tiangolo.com/), deployed to **Render** for scalable and fast API responses.
    - 🗄️ **Database**: Hosted using **Railway (free tier)** for remote, cloud-based MySQL database management.
    - 🧱 **Architecture**: Microservices-based structure, separating the frontend, backend, and database services for modularity, scalability, and maintainability.

    ### 💡 Why Taskit?
    Taskit aims to offer users a real-world experience with clean UI and full CRUD features:
    - Register & Login securely using JWT tokens
    - Create, read, update, and delete tasks
    - Track task completion with real-time feedback
    - Built with production-ready principles using APIs and token-based authentication

    🔐 Protected using secure headers and API keys  
    📦 Deployed on modern cloud platforms for a reliable experience  
    🧑‍💻 Great for developers, students, or anyone looking to manage tasks simply and effectively
    """)
