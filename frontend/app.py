import streamlit as st
import requests


# dummy values , in real app : store this securely
USER_CREDENTIALS = {
    "admin":"password123",
    "arnav":"123"
}


def login():
    st.title('login')
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    login_button = st.button("Login")

    if login_button:
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login Successful!")
        else:
            st.error("Invalid credentials")


def get_backend_message():
    try:
        # call the FastAPI backend
        response = requests.get("http://localhost:8000/message")

        if response.status_code == 200:
            return response.json()["message"]
        else:
            return "failed to get message"
    except Exception as e:
        return f"Error: {e}"


def fetch_failures():
    try:
        response = requests.get("http://localhost:8000/failures")
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        st.error(f"Failed to fetch failures {e}")
        return []


def fetch_logs(failure_id):
    try:
        response = requests.post(f"http://localhost:8000/logs", json={"failure_id":failure_id})

        if response.status_code == 200:
            return response.json()["logs"]
        else:
            return ["Failed to fetch logs"]
    
    except Exception as e:
        return [f"Error fetching logs : {e}"]


def analyze_logs(logs):
    try:
        response = requests.post("http://localhost:8000/analyze", json={"logs":logs})

        if response.status_code == 200:
            return response.json()["analysis"]
        else:
            return "Failed to analyze logs"
        
    except Exception as e:
        return f"Error during analysis {e}"



def suggest_fix(failure_text, analysis):
    try:
        response = requests.post("http://localhost:8000/suggest_fix", json={
            "failure_type": failure_text,
            "analysis": analysis
        })
        if response.status_code == 200:
            return response.json()["suggestion"]
        else:
            return "Failed to suggest a fix"
    except Exception as e:
        return f"Error suggesting fix: {e}"



def main_app():
    st.title(f"Welcome, {st.session_state.username}")

    st.write("fetching message from backend...")

    message = get_backend_message()

    st.success(f"Message : {message}")

    st.subheader("1. Fetch failure")
    failures = fetch_failures()
    if failures:
        options={f"{f['type']} - {f['details']}" : f["id"] for f in failures}
        selected_label = st.selectbox("Select a failure to investigate", list(options.keys()))

        selected_id = options[selected_label]

        st.success(f"Selected Failure : {selected_label}")

        st.subheader("2. Fetch Logs")
        logs = fetch_logs(selected_id)

        for log in logs:
            st.code(log, language="bash")

        # 3. Analyze Button
        st.subheader("3. Analyze")
        if st.button("Analyze logs"):
            analysis = analyze_logs(logs)
            st.success("Analysis complete")
            st.text_area("Analysis Result", value = analysis, height = 150)

            st.subheader("4. Suggest Fix")
            fix = suggest_fix(selected_label, analysis)
            st.text_area("Suggested Fix", value=fix, height=100)
    else:
        st.warning("No failures found")

    # if st.button("Logout"):
    #     st.session_state.logged_in = False
    #     st.experimental_rerun()







def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        main_app()
    else:
        login()


if __name__ == "__main__":
    main()
    
            
