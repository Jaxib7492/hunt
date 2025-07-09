import streamlit as st
import gspread
from google.oauth2 import service_account
import os

# -------- Google Sheets Setup --------
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1Bu8mzwoJUXw3JAD63nmTcmAlYo9GdR9vQyzGkukTWgA"
SHEET_NAME = "Outreach Data"

scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scopes
)
client = gspread.authorize(creds)

# -------- Persistent Name Store --------
NAME_FILE = "name_store.txt"

def save_name_to_file(name):
    with open(NAME_FILE, "w", encoding="utf-8") as f:
        f.write(name)

def load_name_from_file():
    if os.path.exists(NAME_FILE):
        with open(NAME_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def save_reference_entry(name, email, reference):
    sheet = client.open_by_url(GSHEET_URL).worksheet(SHEET_NAME)
    data = sheet.get_all_values()

    existing_emails = [row[2].strip().lower() for row in data if len(row) > 2]
    if email.strip().lower() in existing_emails:
        st.error("❌ This email already exists in the sheet.")
        return False

    next_row = None
    for i, row in enumerate(data[1:], start=2):
        b_empty = len(row) <= 1 or row[1].strip() == ""
        c_empty = len(row) <= 2 or row[2].strip() == ""
        f_empty = len(row) <= 5 or row[5].strip() == ""
        if b_empty and c_empty and f_empty:
            next_row = i
            break

    if not next_row:
        next_row = len(data) + 1

    sheet.update_cell(next_row, 2, name)
    sheet.update_cell(next_row, 3, email)
    sheet.update_cell(next_row, 6, reference)

    return True

# ----------------------
# Session-memory name handling WITHOUT session_state

# Use a global variable to store the current name during the session
_current_name = ""

def get_current_name():
    global _current_name
    return _current_name

def set_current_name(name):
    global _current_name
    _current_name = name

# ----------------------

def main():
    st.set_page_config(page_title="Outreach Submission Form")
    st.title("📋 Outreach Submission Form")

    # Load current name in memory (starts empty on app launch)
    current_name = get_current_name()

    with st.form("entry_form"):
        name = st.text_input("👤 Your Name", value=current_name)
        contact = st.text_input("📧 Client Email")
        reference = st.text_area("📝 Reference Message")

        submitted = st.form_submit_button("Submit")

        if submitted:
            if not name or not contact or not reference:
                st.warning("⚠️ Please fill in all fields.")
            else:
                # Save name locally on disk
                save_name_to_file(name)
                # Save name in session memory (global variable)
                set_current_name(name)

                success = save_reference_entry(name, contact, reference)
                if success:
                    st.success("✅ Entry submitted successfully!")

if __name__ == "__main__":
    main()
