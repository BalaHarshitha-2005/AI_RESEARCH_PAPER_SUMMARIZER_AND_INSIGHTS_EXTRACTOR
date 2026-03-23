import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Research Paper Assistant", layout="wide")

# ------------------------------------------------
# TITLE
# ------------------------------------------------

st.markdown(
"""
# 📚 AI BASED RESEARCH PAPER SUMMARIZER AND INSIGHTS EXTRACTOR
---
"""
)

# ------------------------------------------------
# SESSION VARIABLES
# ------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "paper_id" not in st.session_state:
    st.session_state.paper_id = None

if "summary_text" not in st.session_state:
    st.session_state.summary_text = ""


# ------------------------------------------------
# LOGIN / SIGNUP
# ------------------------------------------------

if not st.session_state.logged_in:

    tab1, tab2 = st.tabs(["Login", "Signup"])

    # ---------------- LOGIN ----------------

    with tab1:

        st.subheader("Login")

        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):

            r = requests.post(
                f"{API_URL}/login",
                json={"email": email, "password": password}
            )

            if r.status_code == 200:

                data = r.json()

                if data["message"] == "Login successful":

                    st.session_state.logged_in = True
                    st.success("Login successful")
                    st.rerun()

                else:
                    st.error(data["message"])

            else:
                st.error("Server error")

    # ---------------- SIGNUP ----------------

    with tab2:

        st.subheader("Create Account")

        username = st.text_input("Username", key="signup_user")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pass")

        if st.button("Signup"):

            r = requests.post(
                f"{API_URL}/signup",
                json={
                    "username": username,
                    "email": email,
                    "password": password
                }
            )

            if r.status_code == 200:

                data = r.json()
                st.success(data["message"])

            else:
                st.error("Signup failed")


# ------------------------------------------------
# MAIN APPLICATION
# ------------------------------------------------

else:

    menu = st.radio(
        "",
        ["Upload Paper", "Generate Summary", "Chat with Paper", "Paper Improvements", "Logout"],
        horizontal=True
    )

    # ------------------------------------------------
    # UPLOAD PAPER
    # ------------------------------------------------

    if menu == "Upload Paper":

        st.subheader("Upload Research Paper")

        file = st.file_uploader("Upload PDF", type=["pdf"])

        if st.button("Upload Paper") and file:

            files = {"file": file}

            with st.spinner("Uploading paper..."):

                r = requests.post(f"{API_URL}/upload", files=files)

            if r.status_code == 200:

                data = r.json()

                st.session_state.paper_id = data["paper_id"]

                st.success("Paper uploaded successfully!")

            else:
                st.error("Upload failed")


    # ------------------------------------------------
    # GENERATE SUMMARY
    # ------------------------------------------------

    elif menu == "Generate Summary":

        st.subheader("Generate Research Paper Summary")

        if st.session_state.paper_id is None:

            st.warning("Please upload a paper first.")

        else:

            summary_type = st.selectbox(
                "Summary Type",
                ["short", "detailed", "bullet"],
                key="summary_type"
            )

            if st.button("Generate Summary"):

                with st.spinner("Generating summary..."):

                    r = requests.post(
                        f"{API_URL}/summarize",
                        json={
                            "paper_id": st.session_state.paper_id,
                            "length": summary_type
                        }
                    )

                if r.status_code == 200:

                    data = r.json()

                    if "summary" in data:

                        summary = data["summary"]

                        if isinstance(summary, list):

                            summary_text = "\n".join(summary)

                            for point in summary:
                                st.write(point)

                        else:

                            summary_text = summary
                            st.write(summary)

                        st.session_state.summary_text = summary_text

                        st.success("Summary Generated")

                    else:
                        st.error(data)

                else:
                    st.error("Backend error")


        # ---------------- DOWNLOAD SUMMARY ----------------

        if st.session_state.summary_text != "":

            st.download_button(
                label="Download Summary",
                data=st.session_state.summary_text,
                file_name="research_summary.txt",
                mime="text/plain"
            )


    # ------------------------------------------------
    # CHAT WITH PAPER
    # ------------------------------------------------

    elif menu == "Chat with Paper":

        st.subheader("Chat with Research Paper")

        question = st.text_input("Ask a question", key="chat_question")

        if st.button("Ask"):

            r = requests.post(
                f"{API_URL}/chat",
                json={"question": question}
            )

            if r.status_code == 200:

                data = r.json()

                st.write(data["answer"])

            else:
                st.error("Chat failed")


    # ------------------------------------------------
    # PAPER IMPROVEMENTS
    # ------------------------------------------------

    elif menu == "Paper Improvements":

        st.subheader("Improve Research Writing")

        text = st.text_area("Enter paragraph", key="improve_text")

        if st.button("Improve"):

            r = requests.post(
                f"{API_URL}/improve",
                json={"text": text}
            )

            if r.status_code == 200:

                data = r.json()

                st.success("Improved Version")

                st.write(data["improved_text"])

            else:
                st.error("Improvement failed")


    # ------------------------------------------------
    # LOGOUT
    # ------------------------------------------------

    elif menu == "Logout":

        st.session_state.logged_in = False
        st.session_state.paper_id = None
        st.session_state.summary_text = ""

        st.success("Logged out successfully")

        st.rerun()