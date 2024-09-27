import streamlit as st
import hmac
import pandas as pd
from datetime import datetime, time
import time as t
from pytz import timezone
import github
from github import Github

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

# Main Streamlit app starts here
st.write("Hi Power Geng!")
df = pd.read_csv(r"TNB_Share_Price_Parameters.csv")
df = df.transpose()

with st.form("my_form"):
    edited_df = st.data_editor(df)
    comment = st.text_area("Comments here")

    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.table(edited_df)
        edited_df = edited_df.transpose()
        edited_df.to_csv("TNB_Share_Price_Parameters.csv", index=False)
        with open('TNB_Share_Price_Parameters.csv', 'rb') as f:
            contents = f.read()


        repo_owner = 'mirainsight'
        repo_name = 'TNB_Share_Price'
        file_path = 'TNB_Share_Price_Parameters.csv'
        token = st.secrets['Github_token']
        github = Github(token)
        repo = github.get_user(repo_owner).get_repo(repo_name)
        content = repo.get_contents(file_path)
        commit_message = f"{comment} as of {datetime.now(timezone('Asia/Singapore')).strftime(format = '%d/%-m/%Y')}"
        repo.update_file(file_path, commit_message, contents, content.sha)
        
        st.success('Saved!', icon="✅")
        
